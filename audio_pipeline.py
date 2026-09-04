"""
Core audio processing pipeline for real-time dubbing.

Flow:
  Raw PCM audio -> Whisper STT -> English transcript
                -> Translator  -> Finnish text
                -> TTS Engine   -> Finnish audio bytes

Each stage is designed to operate on short audio chunks (~2-5 seconds)
for low-latency streaming.
"""
import io
import tempfile
import wave
from pathlib import Path

from translator import Translator
from tts_engine import TTSEngine
from subtitle_generator import SubtitleGenerator
from speaker_extractor import SpeakerVoiceExtractor


class AudioPipeline:
    """Coordinates transcription, translation, and speech synthesis."""

    def __init__(self):
        self.source_lang = "auto"
        self.target_lang = "fi"
        self._whisper_model = None
        self.translator = Translator()
        self.translator.set_languages("auto", "fi")
        self.tts = TTSEngine()
        self.subtitles = SubtitleGenerator()
        self.speaker_extractor = SpeakerVoiceExtractor()
        self.speaker_profile = None

    def configure(self, source_lang: str = "auto", target_lang: str = "fi"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator.set_languages(source_lang, target_lang)

    @property
    def whisper_model(self):
        """Lazy-load Whisper to avoid startup delay if unused."""
        if self._whisper_model is None:
            try:
                import whisper
                self._whisper_model = whisper.load_model("base")
            except ImportError:
                raise RuntimeError(
                    "openai-whisper is not installed. "
                    "Run: pip install openai-whisper"
                )
        return self._whisper_model

    def _transcribe(self, pcm_bytes: bytes) -> str:
        """Transcribe raw PCM audio bytes to text using Whisper."""
        if not pcm_bytes:
            return ""

        try:
            import numpy as np
            audio_np = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            result = self.whisper_model.transcribe(
                audio_np,
                language=self.source_lang if self.source_lang != "auto" else None,
                fp16=False,
            )
            return result.get("text", "").strip()
        except Exception:
            # Fallback to temp WAV file if in-memory numpy input fails
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            try:
                with wave.open(tmp.name, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(16000)
                    wf.writeframes(pcm_bytes)

                result = self.whisper_model.transcribe(
                    tmp.name,
                    language=self.source_lang if self.source_lang != "auto" else None,
                    fp16=False,
                )
                return result.get("text", "").strip()
            finally:
                try:
                    Path(tmp.name).unlink(missing_ok=True)
                except Exception:
                    pass

    def process_chunk(self, pcm_bytes: bytes, timestamp: float, status_cb=None) -> dict:
        """
        Process a single audio chunk through the full pipeline.

        Returns a dict with keys:
          - subtitle: English subtitle text (or None)
          - sub_start / sub_end: timestamp range for the subtitle
          - dubbed_audio: Finnish TTS audio as MP3 bytes (or None)
        """
        if status_cb:
            status_cb("detecting", "🎙️ Detecting spoken audio & transcribing with Whisper...")

        transcript = self._transcribe(pcm_bytes)

        if not transcript:
            if status_cb:
                status_cb("idle", "Waiting for spoken dialogue...")
            return {"subtitle": None, "dubbed_audio": None}

        english_text = transcript

        if status_cb:
            status_cb("translating", f"🌐 Translating: \"{english_text}\" → Finnish")

        finnish_text = self.translator.translate(english_text)

        if status_cb:
            status_cb("synthesizing", f"🔊 Synthesizing Finnish speech & English subtitles...")

        dubbed_audio = self.tts.synthesize(finnish_text, lang="fi")

        # Estimate chunk duration from PCM length (16kHz, 16-bit mono)
        duration = len(pcm_bytes) / (16000 * 2)

        self.subtitles.add_cue(english_text, timestamp, timestamp + duration)

        if status_cb:
            status_cb("complete", f"✅ Dubbed & English Subtitles Ready")

        return {
            "subtitle": english_text,
            "sub_start": timestamp,
            "sub_end": round(timestamp + duration, 2),
            "dubbed_audio": dubbed_audio,
        }

    def process_video_batch(self, video_path: str, start_time: float = 0.0, max_duration: float = 120.0, progress_cb=None):
        """
        Extract audio from video file and process `max_duration` seconds (default 120s = 2 mins for fast start).
        Uses greedy Whisper decoding, batch translation, and concurrent async TTS.
        """
        import base64
        import whisper

        if progress_cb:
            progress_cb({
                "type": "status",
                "message": f"Loading audio buffer ({start_time/60:.1f}m - {(start_time+max_duration)/60:.1f}m)..."
            })

        audio = whisper.load_audio(video_path)
        sample_rate = 16000
        total_audio_duration = len(audio) / sample_rate

        start_sample = int(start_time * sample_rate)
        end_sample = int(min(len(audio), (start_time + max_duration) * sample_rate))
        if start_sample >= len(audio):
            return

        audio_slice = audio[start_sample:end_sample]
        slice_duration = len(audio_slice) / sample_rate
        if slice_duration <= 0:
            return

        if progress_cb:
            progress_cb({
                "type": "status",
                "message": f"High-speed Whisper STT transcribing ({slice_duration/60:.1f} mins)..."
            })

        # High-speed Greedy Whisper Decoding
        result = self.whisper_model.transcribe(
            audio_slice,
            language=self.source_lang if self.source_lang != "auto" else None,
            fp16=False,
            verbose=False,
            beam_size=1,
            temperature=0.0,
            best_of=1,
            condition_on_previous_text=False,
        )

        segments = result.get("segments", [])
        valid_segments = [s for s in segments if s.get("text", "").strip()]
        total_segments = len(valid_segments)

        if not valid_segments:
            return

        # High-speed Batch Translation
        raw_texts = [s["text"].strip() for s in valid_segments]
        translated_texts = self.translator.translate_batch(raw_texts)

        # High-speed Concurrent Async TTS Synthesis using extracted speaker voice profile
        pitch_str = self.speaker_profile.get("pitch_str", "+0Hz") if self.speaker_profile else "+0Hz"
        voice_id = self.speaker_profile.get("voice_id", "fi") if self.speaker_profile else "fi"
        tts_items = [(fi_text, voice_id) for fi_text in translated_texts]
        audio_results = self.tts.synthesize_batch(tts_items, pitch_str=pitch_str, voice_override=voice_id)

        for idx, (seg, en_text, fi_text, dubbed_audio) in enumerate(zip(valid_segments, raw_texts, translated_texts, audio_results), 1):
            seg_start = round(start_time + seg["start"], 2)
            seg_end = round(start_time + seg["end"], 2)

            self.subtitles.add_cue(en_text, seg_start, seg_end)
            percent = round((idx / max(1, total_segments)) * 100, 1)

            if progress_cb:
                progress_cb({
                    "type": "preprocess_progress",
                    "percent": percent,
                    "segment_index": idx,
                    "total_segments": total_segments,
                    "start_time": start_time,
                    "processed_duration": round(seg_end - start_time, 2),
                    "target_duration": round(slice_duration, 2),
                    "total_video_duration": round(total_audio_duration, 2),
                    "segment": {
                        "id": f"{int(start_time)}_{idx}",
                        "start": seg_start,
                        "end": seg_end,
                        "english_text": en_text,
                        "finnish_text": fi_text,
                        "audio_b64": base64.b64encode(dubbed_audio).decode() if dubbed_audio else None,
                    }
                })

"""
Core audio processing pipeline for real-time dubbing in DubStream v2.0.

Flow:
  Raw PCM audio / Video file -> AudioBuffer -> DubStreamOrchestrator -> Production/Preview Dubbing Output
"""
import io
import tempfile
from pathlib import Path
import numpy as np
import base64

from config import DubStreamConfig
from audio.buffer import AudioBuffer
from pipeline.orchestrator import DubStreamOrchestrator
from translator import Translator
from tts_engine import TTSEngine
from subtitle_generator import SubtitleGenerator
from speaker_extractor import SpeakerVoiceExtractor


class AudioPipeline:
    """Coordinates transcription, translation, and speech synthesis via DubStreamOrchestrator."""

    def __init__(self, config: DubStreamConfig = None):
        self.config = config or DubStreamConfig()
        self.orchestrator = DubStreamOrchestrator(config=self.config)
        self.source_lang = "auto"
        self.target_lang = "fi"
        self.translator = self.orchestrator.translator
        self.tts = self.orchestrator.voice_engine
        self.subtitles = SubtitleGenerator()
        self.speaker_extractor = SpeakerVoiceExtractor()
        self.speaker_profile = None

    def configure(self, source_lang: str = "auto", target_lang: str = "fi"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator.set_languages(source_lang, target_lang)

    @property
    def whisper_model(self):
        return self.orchestrator.transcriber.whisper_model

    def process_chunk(self, pcm_bytes: bytes, timestamp: float, status_cb=None) -> dict:
        """Process a single audio chunk through the full orchestrator pipeline."""
        if status_cb:
            status_cb("detecting", "Detecting spoken audio & processing via DubStream Orchestrator...")

        audio_buf = AudioBuffer.from_pcm16_bytes(pcm_bytes, sample_rate=16000, channels=1)
        if audio_buf.duration <= 0.05:
            if status_cb:
                status_cb("idle", "Waiting for spoken dialogue...")
            return {"subtitle": None, "dubbed_audio": None}

        profile_obj = self._get_speaker_profile_obj()
        res = self.orchestrator.run_production_pipeline(audio_buf, target_lang=self.target_lang, speaker_profile=profile_obj)

        if not res.get("subtitle"):
            if status_cb:
                status_cb("idle", "Waiting for spoken dialogue...")
            return {"subtitle": None, "dubbed_audio": None}

        english_text = res["subtitle"]
        dubbed_audio = res.get("dubbed_audio_bytes")
        duration = res["sub_end"] - res["sub_start"]

        self.subtitles.add_cue(english_text, timestamp, timestamp + duration)

        if status_cb:
            status_cb("complete", f"Dubbed ({res.get('diagnostics', {}).get('VOICE_ENGINE_SELECTED')})")

        return {
            "subtitle": english_text,
            "sub_start": timestamp,
            "sub_end": round(timestamp + duration, 2),
            "dubbed_audio": dubbed_audio,
            "diagnostics": res.get("diagnostics", {}),
        }

    def _get_speaker_profile_obj(self):
        """Convert dict or object speaker_profile to SpeakerProfile instance."""
        if isinstance(self.speaker_profile, dict):
            from voices.profile import SpeakerProfile
            return SpeakerProfile(
                speaker_id="SPEAKER_00",
                gender=self.speaker_profile.get("gender", "unknown"),
                voice_id=self.speaker_profile.get("voice_id", "fi"),
                pitch_str=self.speaker_profile.get("pitch_str", "+0Hz"),
                reference_audio=self.speaker_profile.get("ref_path"),
            )
        return self.speaker_profile

    def get_or_load_video_audio(self, video_path: str) -> np.ndarray:
        """Load and cache 16kHz mono audio for a video file to avoid expensive repeated ffmpeg passes."""
        if not hasattr(self, "_audio_cache"):
            self._audio_cache = {}

        if video_path in self._audio_cache:
            return self._audio_cache[video_path]

        import whisper
        audio_data = whisper.load_audio(video_path)
        self._audio_cache[video_path] = audio_data
        return audio_data

    def process_video_batch(
        self, video_path: str, start_time: float = 0.0, max_duration: float = 120.0, progress_cb=None
    ):
        """Process a video batch slice through DubStreamOrchestrator."""
        if progress_cb:
            progress_cb({
                "type": "status",
                "message": f"Loading audio buffer ({start_time/60:.1f}m - {(start_time+max_duration)/60:.1f}m)..."
            })

        audio_data = self.get_or_load_video_audio(video_path)
        sample_rate = 16000
        total_audio_duration = len(audio_data) / sample_rate

        start_sample = int(start_time * sample_rate)
        end_sample = int(min(len(audio_data), (start_time + max_duration) * sample_rate))
        if start_sample >= len(audio_data):
            return

        slice_samples = audio_data[start_sample:end_sample]
        slice_buffer = AudioBuffer(samples=slice_samples, sample_rate=sample_rate, channels=1)
        slice_duration = slice_buffer.duration
        if slice_duration <= 0:
            return

        if progress_cb:
            progress_cb({
                "type": "status",
                "message": f"Orchestrator processing batch ({slice_duration/60:.1f} mins)..."
            })

        profile_obj = self._get_speaker_profile_obj()
        segments_results = self.orchestrator.run_production_pipeline_multi(
            slice_buffer, target_lang=self.target_lang, speaker_profile=profile_obj
        )

        if not segments_results:
            return

        total_segs = len(segments_results)
        for idx, res in enumerate(segments_results):
            seg_start = round(start_time + res["sub_start"], 2)
            seg_end = round(start_time + res["sub_end"], 2)
            en_text = res["subtitle"]
            fi_text = res["dubbed_text"]
            dubbed_audio = res.get("dubbed_audio_bytes")
            diag = res.get("diagnostics", {})

            self.subtitles.add_cue(en_text, seg_start, seg_end)

            pct = round(((idx + 1) / total_segs) * 100.0, 1)

            if progress_cb:
                progress_cb({
                    "type": "preprocess_progress",
                    "percent": pct,
                    "segment_index": idx + 1,
                    "total_segments": total_segs,
                    "start_time": start_time,
                    "processed_duration": round(seg_end - start_time, 2),
                    "target_duration": round(slice_duration, 2),
                    "total_video_duration": round(total_audio_duration, 2),
                    "diagnostics": diag,
                    "segment": {
                        "id": f"{int(start_time)}_{idx+1}",
                        "start": seg_start,
                        "end": seg_end,
                        "english_text": en_text,
                        "finnish_text": fi_text,
                        "audio_b64": base64.b64encode(dubbed_audio).decode() if dubbed_audio else None,
                        "diagnostics": diag,
                    }
                })


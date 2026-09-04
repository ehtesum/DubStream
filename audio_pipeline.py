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
            status_cb("detecting", "🎙️ Detecting spoken audio & processing via DubStream Orchestrator...")

        audio_buf = AudioBuffer.from_pcm16_bytes(pcm_bytes, sample_rate=16000, channels=1)
        if audio_buf.duration <= 0.05:
            if status_cb:
                status_cb("idle", "Waiting for spoken dialogue...")
            return {"subtitle": None, "dubbed_audio": None}

        res = self.orchestrator.run_production_pipeline(audio_buf, target_lang=self.target_lang)

        if not res.get("subtitle"):
            if status_cb:
                status_cb("idle", "Waiting for spoken dialogue...")
            return {"subtitle": None, "dubbed_audio": None}

        english_text = res["subtitle"]
        dubbed_audio = res.get("dubbed_audio_bytes")
        duration = res["sub_end"] - res["sub_start"]

        self.subtitles.add_cue(english_text, timestamp, timestamp + duration)

        if status_cb:
            status_cb("complete", f"✅ Dubbed ({res.get('diagnostics', {}).get('VOICE_ENGINE_SELECTED')})")

        return {
            "subtitle": english_text,
            "sub_start": timestamp,
            "sub_end": round(timestamp + duration, 2),
            "dubbed_audio": dubbed_audio,
            "diagnostics": res.get("diagnostics", {}),
        }

    def process_video_batch(
        self, video_path: str, start_time: float = 0.0, max_duration: float = 120.0, progress_cb=None
    ):
        """Process a video batch slice through DubStreamOrchestrator."""
        import whisper

        if progress_cb:
            progress_cb({
                "type": "status",
                "message": f"Loading audio buffer ({start_time/60:.1f}m - {(start_time+max_duration)/60:.1f}m)..."
            })

        audio_data = whisper.load_audio(video_path)
        sample_rate = 16000
        full_buffer = AudioBuffer(samples=audio_data, sample_rate=sample_rate, channels=1)
        total_audio_duration = full_buffer.duration

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

        res = self.orchestrator.run_production_pipeline(slice_buffer, target_lang=self.target_lang)

        if not res.get("subtitle"):
            return

        seg_start = round(start_time + res["sub_start"], 2)
        seg_end = round(start_time + res["sub_end"], 2)
        en_text = res["subtitle"]
        fi_text = res["dubbed_text"]
        dubbed_audio = res.get("dubbed_audio_bytes")
        diag = res.get("diagnostics", {})

        self.subtitles.add_cue(en_text, seg_start, seg_end)

        if progress_cb:
            progress_cb({
                "type": "preprocess_progress",
                "percent": 100.0,
                "segment_index": 1,
                "total_segments": 1,
                "start_time": start_time,
                "processed_duration": round(seg_end - start_time, 2),
                "target_duration": round(slice_duration, 2),
                "total_video_duration": round(total_audio_duration, 2),
                "diagnostics": diag,
                "segment": {
                    "id": f"{int(start_time)}_1",
                    "start": seg_start,
                    "end": seg_end,
                    "english_text": en_text,
                    "finnish_text": fi_text,
                    "audio_b64": base64.b64encode(dubbed_audio).decode() if dubbed_audio else None,
                    "diagnostics": diag,
                }
            })

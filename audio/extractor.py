"""
Speech reference extractor for DubStream v2.0.

Replaces simplistic energy thresholding with quality-aware speech reference selection.
Performs:
  Audio -> VAD / Quality Analysis -> Remove silence/noise/music/clipping -> Select optimal reference
"""
from pathlib import Path
import numpy as np

from audio.buffer import AudioBuffer
from audio.vad import SpeechQualityAnalyzer


class SpeakerReferenceExtractor:
    """Extracts high-quality reference audio clips for voice profiling."""

    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
        self.analyzer = SpeechQualityAnalyzer()

    def extract_best_reference(
        self,
        audio_buf: AudioBuffer,
        target_duration: float = 5.0,
        max_search_sec: float = 180.0
    ) -> tuple[AudioBuffer, dict]:
        """
        Scan full AudioBuffer and extract clean speech reference buffer along with quality metrics.
        """
        buf_16k = audio_buf.to_mono().resample(self.target_sample_rate)

        ref_buf, quality = self.analyzer.select_best_speech_reference(
            buf_16k,
            segment_len_sec=target_duration,
            step_sec=1.0,
            max_search_sec=max_search_sec
        )

        metrics = {
            "start_time": quality.start_sec,
            "end_time": quality.end_sec,
            "duration": quality.duration,
            "quality_score": quality.quality_score,
            "snr_db": quality.snr_db,
            "clipping_ratio": quality.clipping_ratio,
            "spectral_flatness": quality.spectral_flatness,
            "energy_rms": quality.energy_rms,
        }

        return ref_buf, metrics

"""
Voice Activity Detection (VAD) and Speech Quality Analyzer for DubStream v2.0.

Evaluates audio segments for:
  - Speech presence (energy thresholding & zero-crossing rate)
  - Clipping rejection (detecting digital saturation)
  - Signal-to-Noise Ratio (SNR estimation)
  - Spectral Flatness (distinguishing clean speech from music/white noise)
  - Speech Quality Score (composite 0.0 - 1.0 metric)
"""
from dataclasses import dataclass
import numpy as np

from audio.buffer import AudioBuffer


@dataclass
class SpeechSegmentQuality:
    start_sec: float
    end_sec: float
    duration: float
    snr_db: float
    clipping_ratio: float
    spectral_flatness: float
    energy_rms: float
    quality_score: float


class SpeechQualityAnalyzer:
    """Analyzes audio buffers to isolate high-quality speech reference clips."""

    @staticmethod
    def compute_clipping_ratio(samples: np.ndarray, threshold: float = 0.98) -> float:
        """Calculate proportion of samples that exceed digital saturation threshold."""
        if len(samples) == 0:
            return 0.0
        clipped = np.abs(samples) >= threshold
        return float(np.mean(clipped))

    @staticmethod
    def compute_snr_db(samples: np.ndarray, frame_size: int = 512) -> float:
        """Estimate Signal-to-Noise Ratio (SNR) in dB by comparing top energy frames vs bottom energy floor."""
        if len(samples) < frame_size:
            return 0.0

        num_frames = len(samples) // frame_size
        frames = samples[: num_frames * frame_size].reshape(num_frames, frame_size)
        frame_rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-9)

        # 90th percentile as signal level, 10th percentile as noise floor
        signal_level = np.percentile(frame_rms, 90)
        noise_floor = np.percentile(frame_rms, 10) + 1e-7

        snr = 20.0 * np.log10(signal_level / noise_floor)
        return float(np.clip(snr, 0.0, 60.0))

    @staticmethod
    def compute_spectral_flatness(samples: np.ndarray, sr: int = 16000) -> float:
        """
        Estimate spectral flatness (geometric mean / arithmetic mean of power spectrum).
        Speech harmonic structures have low spectral flatness (~0.01 - 0.2),
        whereas white noise and music transients have higher flatness (> 0.4).
        """
        if len(samples) < 1024:
            return 0.5

        # Take FFT of signal
        fft_vals = np.abs(np.fft.rfft(samples * np.hanning(len(samples))))
        power_spec = fft_vals ** 2 + 1e-12

        geometric_mean = np.exp(np.mean(np.log(power_spec)))
        arithmetic_mean = np.mean(power_spec)

        flatness = geometric_mean / arithmetic_mean
        return float(np.clip(flatness, 0.0, 1.0))

    def evaluate_segment(self, segment_buf: AudioBuffer, start_sec: float, end_sec: float) -> SpeechSegmentQuality:
        """Calculate quality metrics and composite quality score for an AudioBuffer slice."""
        mono = segment_buf.to_mono()
        samples = mono.samples

        if len(samples) == 0:
            return SpeechSegmentQuality(
                start_sec=start_sec, end_sec=end_sec, duration=0.0,
                snr_db=0.0, clipping_ratio=1.0, spectral_flatness=1.0, energy_rms=0.0, quality_score=0.0
            )

        dur = mono.duration
        rms = float(np.sqrt(np.mean(samples ** 2)))
        clipping = self.compute_clipping_ratio(samples)
        snr = self.compute_snr_db(samples)
        flatness = self.compute_spectral_flatness(samples, mono.sample_rate)

        # Composite quality score calculation:
        # Ideal: High SNR (> 20dB), low clipping (< 0.01), low spectral flatness (< 0.25), sufficient RMS (> 0.03)
        if rms < 0.015 or clipping > 0.05:
            score = 0.0
        else:
            snr_norm = min(snr / 30.0, 1.0)
            flatness_penalty = max(0.0, 1.0 - (flatness * 2.5))
            clipping_penalty = max(0.0, 1.0 - (clipping * 50.0))
            rms_norm = min(rms / 0.15, 1.0)

            score = (0.4 * snr_norm) + (0.3 * flatness_penalty) + (0.2 * clipping_penalty) + (0.1 * rms_norm)

        return SpeechSegmentQuality(
            start_sec=start_sec,
            end_sec=end_sec,
            duration=dur,
            snr_db=snr,
            clipping_ratio=clipping,
            spectral_flatness=flatness,
            energy_rms=rms,
            quality_score=float(np.clip(score, 0.0, 1.0)),
        )

    def select_best_speech_reference(
        self, audio_buf: AudioBuffer, segment_len_sec: float = 5.0, step_sec: float = 1.0, max_search_sec: float = 300.0
    ) -> tuple[AudioBuffer, SpeechSegmentQuality]:
        """
        Scan audio buffer with sliding window to select the highest speech-quality reference clip.
        Rejects silence, noisy background, music-dominated, and clipped segments.
        """
        mono_buf = audio_buf.to_mono()
        sr = mono_buf.sample_rate
        total_samples = len(mono_buf.samples)

        max_samples = int(min(total_samples, max_search_sec * sr))
        win_samples = int(segment_len_sec * sr)
        step_samples = int(step_sec * sr)

        if total_samples < win_samples:
            quality = self.evaluate_segment(mono_buf, 0.0, mono_buf.duration)
            return mono_buf, quality

        best_quality = SpeechSegmentQuality(
            start_sec=0.0, end_sec=0.0, duration=0.0,
            snr_db=0.0, clipping_ratio=1.0, spectral_flatness=1.0, energy_rms=0.0, quality_score=-1.0
        )
        best_slice_samples = mono_buf.samples[:win_samples]

        for start in range(0, max_samples - win_samples + 1, step_samples):
            end = start + win_samples
            slice_data = mono_buf.samples[start:end]
            slice_buf = AudioBuffer(samples=slice_data, sample_rate=sr, channels=1)

            q = self.evaluate_segment(slice_buf, start_sec=start / sr, end_sec=end / sr)
            if q.quality_score > best_quality.quality_score:
                best_quality = q
                best_slice_samples = slice_data

        best_buf = AudioBuffer(samples=best_slice_samples, sample_rate=sr, channels=1)
        return best_buf, best_quality

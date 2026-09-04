"""
Loudness management and normalization for DubStream v2.0.

Provides LUFS (EBU R128), RMS, True Peak measurement, clipping detection, and gain normalization.
"""
from dataclasses import dataclass
import numpy as np

from audio.buffer import AudioBuffer


@dataclass
class LoudnessReport:
    integrated_lufs: float
    rms_db: float
    true_peak_db: float
    has_clipping: bool


class LoudnessManager:
    """Measures audio loudness and normalizes to target LUFS level (default -24.0 LUFS)."""

    def __init__(self, target_lufs: float = -24.0):
        self.target_lufs = target_lufs

    def measure(self, audio_buf: AudioBuffer) -> LoudnessReport:
        """Measure LUFS, RMS dB, and True Peak dB of an AudioBuffer."""
        mono = audio_buf.to_mono()
        samples = mono.samples

        if len(samples) == 0:
            return LoudnessReport(integrated_lufs=-70.0, rms_db=-70.0, true_peak_db=-70.0, has_clipping=False)

        rms = float(np.sqrt(np.mean(samples ** 2)))
        rms_db = 20.0 * np.log10(rms + 1e-9)

        true_peak = float(np.max(np.abs(samples)))
        true_peak_db = 20.0 * np.log10(true_peak + 1e-9)
        has_clipping = true_peak >= 0.99

        # Integrated LUFS measurement (pyloudnorm if available, else K-weighting approximation)
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(mono.sample_rate)
            lufs = float(meter.integrated_loudness(samples))
        except Exception:
            # Approximation: RMS dB - 3.0 dB
            lufs = float(rms_db - 3.0)

        return LoudnessReport(
            integrated_lufs=round(lufs, 1),
            rms_db=round(rms_db, 1),
            true_peak_db=round(true_peak_db, 1),
            has_clipping=has_clipping,
        )

    def normalize(self, audio_buf: AudioBuffer, target_lufs: float = None) -> AudioBuffer:
        """Normalize AudioBuffer gain to target LUFS level, preventing digital clipping."""
        target = target_lufs if target_lufs is not None else self.target_lufs
        report = self.measure(audio_buf)

        if report.integrated_lufs <= -65.0:
            return audio_buf

        gain_db = target - report.integrated_lufs
        # Limit max boost to +12dB
        gain_db = min(gain_db, 12.0)
        gain_linear = 10.0 ** (gain_db / 20.0)

        norm_samples = audio_buf.samples * gain_linear

        # Peak limiter check: ensure max peak does not exceed -0.5 dBFS (0.944)
        max_peak = float(np.max(np.abs(norm_samples)))
        if max_peak > 0.944:
            norm_samples = norm_samples * (0.944 / max_peak)

        return AudioBuffer(samples=norm_samples.astype(np.float32), sample_rate=audio_buf.sample_rate, channels=audio_buf.channels)

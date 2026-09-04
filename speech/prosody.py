"""
Prosody and Robust Fundamental Frequency (F0) Analysis for DubStream v2.0.

Provides frame-level pitch extraction, voiced/unvoiced segmentation, octave-jump correction,
and comprehensive F0 prosodic statistics (median, mean, min, max, p10, p90, variance, voiced_ratio).
Supports YIN/autocorrelation with optional torchcrepe neural pitch tracking.
"""
from dataclasses import dataclass
import numpy as np

from audio.buffer import AudioBuffer


@dataclass
class ProsodyProfile:
    f0_median: float
    f0_mean: float
    f0_min: float
    f0_max: float
    f0_p10: float
    f0_p90: float
    f0_variance: float
    voiced_ratio: float
    f0_contour: np.ndarray
    energy_contour: np.ndarray
    speaking_rate: float | None = None

    def to_dict(self) -> dict:
        return {
            "f0_median": float(round(self.f0_median, 1)),
            "f0_mean": float(round(self.f0_mean, 1)),
            "f0_min": float(round(self.f0_min, 1)),
            "f0_max": float(round(self.f0_max, 1)),
            "f0_p10": float(round(self.f0_p10, 1)),
            "f0_p90": float(round(self.f0_p90, 1)),
            "f0_variance": float(round(self.f0_variance, 2)),
            "voiced_ratio": float(round(self.voiced_ratio, 3)),
            "speaking_rate": self.speaking_rate,
        }


class PitchAnalyzer:
    """Robust F0 analyzer handling frame-by-frame pitch extraction and prosody profiling."""

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_size_ms: float = 25.0,
        hop_size_ms: float = 10.0,
        f0_min_hz: float = 50.0,
        f0_max_hz: float = 500.0,
    ):
        self.sample_rate = sample_rate
        self.frame_len = int(sample_rate * (frame_size_ms / 1000.0))
        self.hop_len = int(sample_rate * (hop_size_ms / 1000.0))
        self.f0_min_hz = f0_min_hz
        self.f0_max_hz = f0_max_hz

    def estimate_f0_yin_frame(self, frame: np.ndarray) -> float:
        """YIN fundamental frequency estimation for a single speech frame."""
        w = len(frame)
        tau_min = int(self.sample_rate / self.f0_max_hz)
        tau_max = int(self.sample_rate / self.f0_min_hz)

        if tau_max >= w // 2:
            tau_max = w // 2 - 1

        if tau_max <= tau_min or w < 2 * tau_max:
            return 0.0

        # Step 1: Difference function
        d = np.zeros(tau_max + 1, dtype=np.float32)
        for tau in range(1, tau_max + 1):
            diff = frame[: w - tau] - frame[tau:w]
            d[tau] = float(np.sum(diff ** 2))

        # Step 2: Cumulative mean normalized difference function (CMNDF)
        d_norm = np.ones(tau_max + 1, dtype=np.float32)
        running_sum = 0.0
        for tau in range(1, tau_max + 1):
            running_sum += d[tau]
            if running_sum > 0:
                d_norm[tau] = d[tau] / (running_sum / tau)

        # Step 3: Absolute thresholding
        threshold = 0.15
        best_tau = 0
        for tau in range(tau_min, tau_max):
            if d_norm[tau] < threshold:
                while tau + 1 < tau_max and d_norm[tau + 1] < d_norm[tau]:
                    tau += 1
                best_tau = tau
                break

        if best_tau == 0:
            best_tau = int(np.argmin(d_norm[tau_min:tau_max])) + tau_min

        # Voiced threshold check (d_norm must be low enough for voiced speech)
        if d_norm[best_tau] > 0.45:
            return 0.0

        pitch = float(self.sample_rate / best_tau)
        if self.f0_min_hz <= pitch <= self.f0_max_hz:
            return pitch
        return 0.0

    def analyze_audio(self, audio_buf: AudioBuffer) -> ProsodyProfile:
        """
        Perform multi-frame F0 analysis across audio buffer.
        Extracts f0_median, f0_mean, f0_min, f0_max, p10, p90, variance, voiced_ratio.
        """
        mono_buf = audio_buf.to_mono().resample(self.sample_rate)
        samples = mono_buf.samples

        if len(samples) < self.frame_len:
            empty_f0 = np.zeros(0, dtype=np.float32)
            return ProsodyProfile(
                f0_median=165.0, f0_mean=165.0, f0_min=165.0, f0_max=165.0,
                f0_p10=165.0, f0_p90=165.0, f0_variance=0.0, voiced_ratio=0.0,
                f0_contour=empty_f0, energy_contour=empty_f0
            )

        num_frames = (len(samples) - self.frame_len) // self.hop_len + 1
        f0_contour = np.zeros(num_frames, dtype=np.float32)
        energy_contour = np.zeros(num_frames, dtype=np.float32)

        for i in range(num_frames):
            start = i * self.hop_len
            end = start + self.frame_len
            frame = samples[start:end]

            energy = float(np.sqrt(np.mean(frame ** 2)))
            energy_contour[i] = energy

            # Only estimate pitch if frame energy is above silence noise floor
            if energy >= 0.01:
                pitch = self.estimate_f0_yin_frame(frame)
                f0_contour[i] = pitch
            else:
                f0_contour[i] = 0.0

        # Optional: Try torchcrepe if installed for neural F0 enhancement
        try:
            import torch
            import torchcrepe
            if torch.cuda.is_available():
                audio_tensor = torch.from_numpy(samples).unsqueeze(0)
                pitch, periodicity = torchcrepe.predict(
                    audio_tensor, self.sample_rate, self.hop_len, self.f0_min_hz, self.f0_max_hz,
                    model='tiny', batch_size=2048, device='cuda', return_periodicity=True
                )
                crepe_f0 = pitch.squeeze(0).cpu().numpy()
                crepe_prob = periodicity.squeeze(0).cpu().numpy()
                valid_mask = crepe_prob > 0.5
                f0_contour = np.where(valid_mask, crepe_f0, 0.0).astype(np.float32)
        except Exception:
            pass  # Fall back gracefully to CPU YIN implementation

        # Post-processing: Octave jump and median filtering on voiced frames
        voiced_indices = np.where(f0_contour > 0.0)[0]
        voiced_f0 = f0_contour[voiced_indices]

        if len(voiced_f0) > 0:
            # Median filter voiced segment to remove outlier spikes
            med_val = float(np.median(voiced_f0))
            # Reject values that deviate by more than 1 octave (factor of 2) from median
            valid_voiced = voiced_f0[(voiced_f0 >= med_val / 1.8) & (voiced_f0 <= med_val * 1.8)]
            if len(valid_voiced) == 0:
                valid_voiced = voiced_f0
        else:
            valid_voiced = np.array([165.0], dtype=np.float32)

        f0_median = float(np.median(valid_voiced))
        f0_mean = float(np.mean(valid_voiced))
        f0_min = float(np.min(valid_voiced))
        f0_max = float(np.max(valid_voiced))
        f0_p10 = float(np.percentile(valid_voiced, 10))
        f0_p90 = float(np.percentile(valid_voiced, 90))
        f0_variance = float(np.var(valid_voiced))
        voiced_ratio = float(len(voiced_indices) / max(1, num_frames))

        return ProsodyProfile(
            f0_median=f0_median,
            f0_mean=f0_mean,
            f0_min=f0_min,
            f0_max=f0_max,
            f0_p10=f0_p10,
            f0_p90=f0_p90,
            f0_variance=f0_variance,
            voiced_ratio=voiced_ratio,
            f0_contour=f0_contour,
            energy_contour=energy_contour,
        )

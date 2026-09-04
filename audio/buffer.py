"""
Canonical AudioBuffer representation for DubStream v2.0.

Provides a unified internal representation of audio samples (float32 numpy array,
range -1.0 to 1.0) along with metadata (sample_rate, channels, duration),
and explicit methods for resampling, mono conversion, and format serialization.
"""
from dataclasses import dataclass
import io
import wave
import numpy as np


@dataclass
class AudioBuffer:
    """
    Canonical internal audio container.

    Attributes:
        samples: 1D (mono) or 2D (channels, samples) numpy float32 array in range [-1.0, 1.0].
        sample_rate: Audio sampling frequency in Hz (default 24000 Hz).
        channels: Number of audio channels (1 for mono, 2 for stereo).
    """
    samples: np.ndarray
    sample_rate: int = 24000
    channels: int = 1

    def __post_init__(self):
        # Ensure float32 dtype
        if self.samples.dtype != np.float32:
            self.samples = self.samples.astype(np.float32)

        # Handle 1D vs 2D shape
        if self.samples.ndim == 1:
            self.channels = 1
        elif self.samples.ndim == 2:
            self.channels = self.samples.shape[0]

    @property
    def duration(self) -> float:
        """Calculate duration in seconds."""
        num_samples = self.samples.shape[-1] if self.samples.ndim > 0 else 0
        return float(num_samples) / float(self.sample_rate) if self.sample_rate > 0 else 0.0

    def to_mono(self) -> "AudioBuffer":
        """Convert multi-channel audio to mono by averaging channels."""
        if self.channels == 1 or self.samples.ndim == 1:
            return AudioBuffer(samples=self.samples.copy(), sample_rate=self.sample_rate, channels=1)

        mono_samples = np.mean(self.samples, axis=0, dtype=np.float32)
        return AudioBuffer(samples=mono_samples, sample_rate=self.sample_rate, channels=1)

    def resample(self, target_rate: int) -> "AudioBuffer":
        """
        Resample audio to target_rate using linear interpolation or scipy/torchaudio if available.
        Documented resampling operation.
        """
        if target_rate == self.sample_rate or len(self.samples) == 0:
            return AudioBuffer(samples=self.samples.copy(), sample_rate=self.sample_rate, channels=self.channels)

        num_orig_samples = self.samples.shape[-1]
        num_target_samples = int(round(num_orig_samples * (float(target_rate) / float(self.sample_rate))))

        if num_target_samples == 0:
            return AudioBuffer(samples=np.zeros(0, dtype=np.float32), sample_rate=target_rate, channels=self.channels)

        # Attempt scipy.signal.resample if available, otherwise numpy interpolation
        try:
            from scipy import signal
            if self.samples.ndim == 1:
                resampled_samples = signal.resample(self.samples, num_target_samples).astype(np.float32)
            else:
                resampled_samples = signal.resample(self.samples, num_target_samples, axis=1).astype(np.float32)
        except ImportError:
            orig_indices = np.linspace(0, num_orig_samples - 1, num_orig_samples)
            target_indices = np.linspace(0, num_orig_samples - 1, num_target_samples)

            if self.samples.ndim == 1:
                resampled_samples = np.interp(target_indices, orig_indices, self.samples).astype(np.float32)
            else:
                channels_list = []
                for ch in range(self.channels):
                    ch_resampled = np.interp(target_indices, orig_indices, self.samples[ch])
                    channels_list.append(ch_resampled)
                resampled_samples = np.stack(channels_list, axis=0).astype(np.float32)

        return AudioBuffer(samples=resampled_samples, sample_rate=target_rate, channels=self.channels)

    def to_pcm16_bytes(self) -> bytes:
        """Convert float32 audio samples [-1.0, 1.0] to 16-bit PCM bytes."""
        clipped = np.clip(self.samples, -1.0, 1.0)
        int16_samples = (clipped * 32767.0).astype(np.int16)
        return int16_samples.tobytes()

    @classmethod
    def from_pcm16_bytes(cls, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1) -> "AudioBuffer":
        """Create AudioBuffer from raw 16-bit signed PCM bytes."""
        if not pcm_data:
            return cls(samples=np.zeros(0, dtype=np.float32), sample_rate=sample_rate, channels=channels)

        int16_samples = np.frombuffer(pcm_data, dtype=np.int16)
        float32_samples = int16_samples.astype(np.float32) / 32768.0

        if channels > 1 and len(float32_samples) % channels == 0:
            float32_samples = float32_samples.reshape(-1, channels).T

        return cls(samples=float32_samples, sample_rate=sample_rate, channels=channels)

    def to_wav_bytes(self) -> bytes:
        """Export AudioBuffer as in-memory WAV file bytes (16-bit PCM)."""
        mono_buf = self.to_mono()
        pcm_bytes = mono_buf.to_pcm16_bytes()

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm_bytes)
        return buf.getvalue()

    @classmethod
    def from_wav_bytes(cls, wav_bytes: bytes) -> "AudioBuffer":
        """Read AudioBuffer from in-memory WAV bytes."""
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            sampwidth = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

        if sampwidth == 2:
            int_samples = np.frombuffer(frames, dtype=np.int16)
            float_samples = int_samples.astype(np.float32) / 32768.0
        elif sampwidth == 4:
            int_samples = np.frombuffer(frames, dtype=np.int32)
            float_samples = int_samples.astype(np.float32) / 2147483648.0
        else:
            raise ValueError(f"Unsupported WAV sample width: {sampwidth}")

        if channels > 1 and len(float_samples) % channels == 0:
            float_samples = float_samples.reshape(-1, channels).T

        return cls(samples=float_samples, sample_rate=sample_rate, channels=channels)

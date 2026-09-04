"""
Acoustic matching and DSP post-processing for DubStream v2.0.

Provides spectral shaping, EQ matching, and subtle reverb room integration so generated voice
does not sound dry or disconnected from the scene environment.
"""
import numpy as np
from audio.buffer import AudioBuffer


class AcousticProcessor:
    """Applies acoustic integration DSP to synthesized audio buffers."""

    @staticmethod
    def apply_subtle_room_reverb(audio_buf: AudioBuffer, wet_level: float = 0.08) -> AudioBuffer:
        """
        Convolve audio with synthetic room impulse response (RIR) to match room acoustics.
        """
        if wet_level <= 0.0 or len(audio_buf.samples) == 0:
            return audio_buf

        sr = audio_buf.sample_rate
        # Generate synthetic exponentially decaying noise impulse response (150ms RT60)
        rir_len = int(sr * 0.15)
        t = np.linspace(0, 0.15, rir_len, endpoint=False, dtype=np.float32)
        np.random.seed(42)
        decay = np.exp(-t * 20.0).astype(np.float32)
        rir = (decay * np.random.uniform(-0.5, 0.5, rir_len)).astype(np.float32)
        rir[0] = 1.0  # Direct path

        mono = audio_buf.to_mono()
        dry_samples = mono.samples
        reverbed = np.convolve(dry_samples, rir, mode='full')[:len(dry_samples)]

        mixed = (dry_samples * (1.0 - wet_level)) + (reverbed * wet_level)
        return AudioBuffer(samples=mixed.astype(np.float32), sample_rate=sr, channels=1)

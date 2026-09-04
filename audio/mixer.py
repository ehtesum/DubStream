"""
Background audio mixer and ducking engine for DubStream v2.0.

Mixes dubbed Finnish dialogue with background BGM/SFX audio stems, applying smooth gain envelopes
and dynamic ducking whenever dialogue is active.
"""
from dataclasses import dataclass
import numpy as np

from audio.buffer import AudioBuffer
from audio.loudness import LoudnessManager


@dataclass
class MixConfig:
    dub_volume: float = 1.0
    background_volume: float = 0.6
    ducking_enabled: bool = True
    duck_db: float = -6.0
    attack_ms: float = 50.0
    release_ms: float = 150.0


class AudioMixer:
    """Combines dubbed dialogue and background soundtrack with envelope ducking."""

    def __init__(self, config: MixConfig = None):
        self.config = config or MixConfig()
        self.loudness_manager = LoudnessManager(target_lufs=-24.0)

    def mix(self, dubbed_dialogue: AudioBuffer, background_stem: AudioBuffer) -> AudioBuffer:
        """
        Mix dubbed dialogue with background audio stem.
        Applies smooth ducking attenuation to background stem when dialogue energy is present.
        """
        # Ensure sample rates match
        target_sr = dubbed_dialogue.sample_rate
        bg_buf = background_stem.resample(target_sr).to_mono()
        dub_buf = dubbed_dialogue.to_mono()

        max_len = max(len(dub_buf.samples), len(bg_buf.samples))
        if max_len == 0:
            return dubbed_dialogue

        dub_padded = np.zeros(max_len, dtype=np.float32)
        dub_padded[:len(dub_buf.samples)] = dub_buf.samples

        bg_padded = np.zeros(max_len, dtype=np.float32)
        bg_padded[:len(bg_buf.samples)] = bg_buf.samples

        # Apply BGM Ducking if enabled
        if self.config.ducking_enabled:
            duck_linear = 10.0 ** (self.config.duck_db / 20.0)
            frame_len = int(target_sr * 0.01)  # 10ms frame
            energy_thresh = 0.01

            duck_gain = np.ones(max_len, dtype=np.float32)
            num_frames = max_len // frame_len

            for i in range(num_frames):
                start = i * frame_len
                end = start + frame_len
                frame_rms = float(np.sqrt(np.mean(dub_padded[start:end] ** 2)))
                if frame_rms > energy_thresh:
                    duck_gain[start:end] = duck_linear

            # Smooth gain envelope (moving average filter)
            smooth_win = int(target_sr * (self.config.release_ms / 1000.0))
            if smooth_win > 1 and len(duck_gain) >= smooth_win:
                duck_gain = np.convolve(duck_gain, np.ones(smooth_win) / smooth_win, mode='same')

            bg_padded = bg_padded * duck_gain

        # Scale volumes
        dub_scaled = dub_padded * self.config.dub_volume
        bg_scaled = bg_padded * self.config.background_volume

        mixed_samples = dub_scaled + bg_scaled
        mixed_buf = AudioBuffer(samples=mixed_samples, sample_rate=target_sr, channels=1)

        # Normalize final mix
        return self.loudness_manager.normalize(mixed_buf)

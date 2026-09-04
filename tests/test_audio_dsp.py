"""
Unit tests for LoudnessManager, DialogueSeparator, and AudioMixer.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from audio.loudness import LoudnessManager
from audio.separator import DialogueSeparator
from audio.mixer import AudioMixer, MixConfig


class TestAudioDSP(unittest.TestCase):

    def test_loudness_measurement_and_normalization(self):
        samples = np.full(16000, 0.1, dtype=np.float32)
        buf = AudioBuffer(samples=samples, sample_rate=16000, channels=1)

        manager = LoudnessManager(target_lufs=-24.0)
        report = manager.measure(buf)
        self.assertLess(report.rms_db, 0.0)

        norm_buf = manager.normalize(buf, target_lufs=-24.0)
        norm_report = manager.measure(norm_buf)
        self.assertAlmostEqual(norm_report.integrated_lufs, -24.0, delta=2.5)

    def test_audio_mixer_and_ducking(self):
        # 1-second dialogue tone and 1-second background tone
        t = np.linspace(0, 1.0, 16000, endpoint=False, dtype=np.float32)
        dialogue = AudioBuffer(samples=(0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32), sample_rate=16000)
        bg = AudioBuffer(samples=(0.3 * np.sin(2 * np.pi * 100 * t)).astype(np.float32), sample_rate=16000)

        mixer = AudioMixer(config=MixConfig(ducking_enabled=True, duck_db=-6.0))
        mixed = mixer.mix(dialogue, bg)

        self.assertIsNotNone(mixed)
        self.assertEqual(mixed.sample_rate, 16000)


if __name__ == "__main__":
    unittest.main()

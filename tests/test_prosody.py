"""
Unit tests for robust F0 analysis and prosody profiling.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from speech.prosody import PitchAnalyzer, ProsodyProfile


class TestProsodyAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = PitchAnalyzer(sample_rate=16000)

    def test_sine_wave_pitch_estimation(self):
        # 1-second 220 Hz sine wave (A3 note)
        t = np.linspace(0, 1.0, 16000, endpoint=False, dtype=np.float32)
        sine_220 = (0.5 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)

        buf = AudioBuffer(samples=sine_220, sample_rate=16000, channels=1)
        profile = self.analyzer.analyze_audio(buf)

        self.assertIsInstance(profile, ProsodyProfile)
        self.assertAlmostEqual(profile.f0_median, 220.0, delta=10.0)
        self.assertGreater(profile.voiced_ratio, 0.8)

    def test_silence_prosody(self):
        silence = np.zeros(16000, dtype=np.float32)
        buf = AudioBuffer(samples=silence, sample_rate=16000, channels=1)
        profile = self.analyzer.analyze_audio(buf)

        self.assertEqual(profile.voiced_ratio, 0.0)

    def test_prosody_profile_to_dict(self):
        t = np.linspace(0, 1.0, 16000, endpoint=False, dtype=np.float32)
        sine = (0.4 * np.sin(2 * np.pi * 150.0 * t)).astype(np.float32)
        buf = AudioBuffer(samples=sine, sample_rate=16000, channels=1)
        profile = self.analyzer.analyze_audio(buf)

        p_dict = profile.to_dict()
        self.assertIn("f0_median", p_dict)
        self.assertIn("f0_p10", p_dict)
        self.assertIn("f0_p90", p_dict)
        self.assertIn("voiced_ratio", p_dict)


if __name__ == "__main__":
    unittest.main()

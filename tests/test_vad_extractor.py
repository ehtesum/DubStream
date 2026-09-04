"""
Unit tests for Speech Quality Analyzer and Speaker Reference Extractor.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from audio.vad import SpeechQualityAnalyzer
from audio.extractor import SpeakerReferenceExtractor


class TestSpeechQualityAndExtractor(unittest.TestCase):

    def setUp(self):
        self.analyzer = SpeechQualityAnalyzer()
        self.extractor = SpeakerReferenceExtractor(target_sample_rate=16000)

    def test_clipping_ratio(self):
        clean = np.full(1000, 0.5, dtype=np.float32)
        clipped = np.array([0.99, -0.99, 1.0, -1.0] + [0.1] * 996, dtype=np.float32)

        self.assertEqual(self.analyzer.compute_clipping_ratio(clean), 0.0)
        self.assertAlmostEqual(self.analyzer.compute_clipping_ratio(clipped), 4 / 1000, places=4)

    def test_spectral_flatness(self):
        # White noise has high spectral flatness (~0.8-1.0)
        np.random.seed(42)
        noise = np.random.uniform(-0.5, 0.5, 2048).astype(np.float32)

        # Pure tone has low spectral flatness (~0.0)
        t = np.linspace(0, 0.1, 2048, endpoint=False, dtype=np.float32)
        pure_tone = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        noise_flatness = self.analyzer.compute_spectral_flatness(noise)
        tone_flatness = self.analyzer.compute_spectral_flatness(pure_tone)

        self.assertGreater(noise_flatness, tone_flatness)

    def test_select_best_speech_reference(self):
        # Create audio buffer with 5s silence/noise followed by 5s high SNR clean tone
        np.random.seed(42)
        noisy_part = np.random.uniform(-0.9, 0.9, 80000).astype(np.float32)  # 5s clipped noisy

        t = np.linspace(0, 5.0, 80000, endpoint=False, dtype=np.float32)
        clean_speech_sim = (0.3 * np.sin(2 * np.pi * 220 * t) + 0.1 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        combined = np.concatenate([noisy_part, clean_speech_sim])
        full_buf = AudioBuffer(samples=combined, sample_rate=16000, channels=1)

        ref_buf, metrics = self.extractor.extract_best_reference(full_buf, target_duration=5.0, max_search_sec=10.0)
        self.assertIsNotNone(ref_buf)
        self.assertGreater(metrics["quality_score"], 0.0)
        # Verify the selected segment is the clean part (starts near 5.0s)
        self.assertGreaterEqual(metrics["start_time"], 4.0)


if __name__ == "__main__":
    unittest.main()

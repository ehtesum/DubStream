"""
Unit tests for pitch-preserving TimeStretcher and UtteranceDurationMatcher.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from sync.timestretch import TimeStretcher
from sync.duration import UtteranceDurationMatcher, FinnishTextContractor


class TestSync(unittest.TestCase):

    def test_wsola_time_stretcher(self):
        stretcher = TimeStretcher()
        t = np.linspace(0, 1.0, 16000, endpoint=False, dtype=np.float32)
        sine = (0.5 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
        buf = AudioBuffer(samples=sine, sample_rate=16000, channels=1)

        stretched_buf = stretcher.stretch_audio_buffer(buf, target_duration=0.8)
        self.assertAlmostEqual(stretched_buf.duration, 0.8, delta=0.08)

    def test_text_contractor(self):
        contractor = FinnishTextContractor()
        long_text = "Minun mielestäni tämä on hienoa, mikäli se on mahdollista."
        short_text = contractor.shorten(long_text)
        self.assertIn("mun mielestä", short_text)
        self.assertIn("jos käy", short_text)

    def test_duration_matching_tier_hierarchy(self):
        matcher = UtteranceDurationMatcher()
        samples = np.zeros(16000, dtype=np.float32)
        buf = AudioBuffer(samples=samples, sample_rate=16000, channels=1)  # 1.0s

        # Tier 1 (0-5%)
        _, _, tier1 = matcher.process_utterance(buf, target_duration=1.02)
        self.assertEqual(tier1, "tier1_no_change")

        # Tier 2 (5-12%)
        _, _, tier2 = matcher.process_utterance(buf, target_duration=1.08)
        self.assertEqual(tier2, "tier2_wsola_mild")

        # Tier 3 (12-20%)
        _, _, tier3 = matcher.process_utterance(buf, target_duration=1.15)
        self.assertEqual(tier3, "tier3_wsola_moderate")


if __name__ == "__main__":
    unittest.main()

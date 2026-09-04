"""
Unit tests for TTS Engine cascading fallback architecture.
"""
import unittest
from tts_engine import TTSEngine


class TestTTSFallback(unittest.TestCase):

    def setUp(self):
        self.tts = TTSEngine()

    def test_empty_text_returns_none(self):
        self.assertIsNone(self.tts.synthesize(""))

    def test_synthesize_returns_bytes_or_fallback(self):
        res = self.tts.synthesize("Terve maailma", lang="fi")
        self.assertIsNotNone(res)
        self.assertIsInstance(res, bytes)
        self.assertGreater(len(res), 0)

    def test_batch_synthesis_fallback(self):
        items = [("Mitä kuuluu?", "fi"), ("Kiitos hyvää.", "fi")]
        results = self.tts.synthesize_batch(items, pitch_str="+0Hz")
        self.assertEqual(len(results), 2)
        for res in results:
            self.assertIsNotNone(res)
            self.assertIsInstance(res, bytes)


if __name__ == "__main__":
    unittest.main()

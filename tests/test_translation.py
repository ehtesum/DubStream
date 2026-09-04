"""
Unit tests for translation pipeline and Finnish spoken dialogue rewriter.
"""
import unittest

from translation.finnish import FinnishDialogueTransformer
from translation.dialogue import RuleBasedDialogueRewriter
from translation.translator import ModularTranslator
from voices.profile import SpeakerProfile


class TestTranslationPipeline(unittest.TestCase):

    def setUp(self):
        self.transformer = FinnishDialogueTransformer()
        self.rewriter = RuleBasedDialogueRewriter()

    def test_puhekieli_transformations(self):
        text = "Minä olen iloinen. Sinä olet ystäväni. Hän on kotona."
        transformed = self.transformer.apply_puhekieli(text, formality=0.2)

        self.assertIn("Mä oon", transformed)
        self.assertIn("Sä oot", transformed)
        self.assertIn("Se on", transformed)

    def test_character_style_formality(self):
        profile_casual = SpeakerProfile(speaker_id="p1", style_metadata={"formality": 0.1, "slang_level": 0.8})
        profile_formal = SpeakerProfile(speaker_id="p2", style_metadata={"formality": 1.0, "slang_level": 0.0})

        text = "Minä olen täällä. Anteeksi todella paljon."
        casual_res = self.rewriter.rewrite(text, speaker_profile=profile_casual)
        formal_res = self.rewriter.rewrite(text, speaker_profile=profile_formal)

        self.assertIn("Mä oon", casual_res)
        self.assertIn("Sori", casual_res)
        self.assertIn("Minä olen", formal_res)

    def test_modular_translator_batch(self):
        translator = ModularTranslator()
        res = translator.translate_batch(["Hello world", "Good morning"])
        self.assertEqual(len(res), 2)
        for r in res:
            self.assertIsInstance(r, str)


if __name__ == "__main__":
    unittest.main()

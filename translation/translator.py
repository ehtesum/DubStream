"""
Translation engine for DubStream v2.0.

Pipelined architecture:
  Original English -> Semantic Translation -> DialogueRewriter (Puhekieli + Character Style)
"""
from translation.dialogue import DialogueRewriter, RuleBasedDialogueRewriter
from voices.profile import SpeakerProfile


class ModularTranslator:
    """Translates text and transforms output using DialogueRewriter."""

    def __init__(self, rewriter: DialogueRewriter = None):
        self.source_lang = "en"
        self.target_lang = "fi"
        self.rewriter = rewriter or RuleBasedDialogueRewriter()
        self._backend = None
        self._detect_backend()

    def _detect_backend(self):
        try:
            import argostranslate.translate
            self._backend = "argos"
            return
        except ImportError:
            pass

        try:
            from deep_translator import GoogleTranslator
            self._backend = "deep"
            return
        except ImportError:
            pass

        self._backend = "stub"

    def set_languages(self, source: str, target: str):
        self.source_lang = source
        self.target_lang = target

    def translate(self, text: str, speaker_profile: SpeakerProfile = None) -> str:
        if not text or not text.strip():
            return ""

        if self.source_lang == self.target_lang:
            return text

        if self._backend == "argos":
            raw_res = self._translate_argos(text)
        elif self._backend == "deep":
            raw_res = self._translate_deep(text)
        else:
            raw_res = text

        return self.rewriter.rewrite(raw_res, self.target_lang, speaker_profile)

    def translate_batch(self, texts: list[str], speaker_profile: SpeakerProfile = None) -> list[str]:
        if not texts:
            return []

        if self.source_lang == self.target_lang:
            return list(texts)

        if self._backend == "deep":
            try:
                from deep_translator import GoogleTranslator
                src = self.source_lang if self.source_lang != "auto" else "auto"
                translated = GoogleTranslator(source=src, target=self.target_lang).translate_batch(texts)
                raw_res = [t if t else orig for t, orig in zip(translated, texts)]
            except Exception:
                raw_res = [self._translate_deep(t) for t in texts]
        else:
            raw_res = [self.translate(t, speaker_profile=speaker_profile) for t in texts]

        return [self.rewriter.rewrite(t, self.target_lang, speaker_profile) for t in raw_res]

    def _translate_argos(self, text: str) -> str:
        import argostranslate.translate
        translated = argostranslate.translate.translate(text, self.source_lang, self.target_lang)
        return translated or text

    def _translate_deep(self, text: str) -> str:
        from deep_translator import GoogleTranslator
        src = self.source_lang if self.source_lang != "auto" else "auto"
        result = GoogleTranslator(source=src, target=self.target_lang).translate(text)
        return result or text

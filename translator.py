"""
Translation module supporting multiple backends.

Priority order:
  1. argos-translate (fully offline, no API key)
  2. deep-translator with GoogleTranslator (online, free)
  3. Stub fallback that returns the original text
"""


class Translator:
    """Translates text between languages with automatic backend selection."""

    def __init__(self):
        self.source_lang = "en"
        self.target_lang = "fi"
        self._backend = None
        self._detect_backend()

    def _detect_backend(self):
        # Try argos-translate first (offline)
        try:
            import argostranslate.package
            import argostranslate.translate
            self._backend = "argos"
            return
        except ImportError:
            pass

        # Try deep-translator (online)
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

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        if self.source_lang == self.target_lang:
            return text

        if self._backend == "argos":
            res = self._translate_argos(text)
        elif self._backend == "deep":
            res = self._translate_deep(text)
        else:
            res = text

        if self.target_lang == "fi":
            return self._to_puhekieli(res)
        return res

    def translate_batch(self, texts: list[str]) -> list[str]:
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
                raw_res = [self.translate(t) for t in texts]
        else:
            raw_res = [self.translate(t) for t in texts]

        if self.target_lang == "fi":
            return [self._to_puhekieli(t) for t in raw_res]
        return raw_res

    def _to_puhekieli(self, text: str) -> str:
        """Transform formal textbook Finnish into natural conversational movie dialogue (puhekieli)."""
        import re

        if not text:
            return text

        rules = [
            (r'\bMinä olen\b', 'Mä oon'), (r'\bminä olen\b', 'mä oon'),
            (r'\bMinä\b', 'Mä'), (r'\bminä\b', 'mä'),
            (r'\bSinä olet\b', 'Sä oot'), (r'\bsinä olet\b', 'sä oot'),
            (r'\bSinä\b', 'Sä'), (r'\bsinä\b', 'sä'),
            (r'\bHän on\b', 'Se on'), (r'\bhän on\b', 'se on'),
            (r'\bHän\b', 'Se'), (r'\bhän\b', 'se'),
            (r'\bMe olemme\b', 'Me ollaan'), (r'\bme olemme\b', 'me ollaan'),
            (r'\bMe menemme\b', 'Me meennään'), (r'\bme menemme\b', 'me meennään'),
            (r'\bHe ovat\b', 'Ne on'), (r'\bhe ovat\b', 'ne on'),
            (r'\bHe\b', 'Ne'), (r'\bhe\b', 'ne'),
            (r'\bei ole\b', 'ei oo'), (r'\bEi ole\b', 'Ei oo'),
            (r'\bonko\b', 'onks'), (r'\bOnko\b', 'Onks'),
            (r'\bmitä sinä\b', 'mitä sä'), (r'\bMitä sinä\b', 'Mitä sä'),
            (r'\bkuinka sinä\b', 'kuinka sä'), (r'\bKuinka sinä\b', 'Kuinka sä'),
            (r'\banteeksi\b', 'sori'), (r'\bAnteeksi\b', 'Sori'),
        ]

        res = text
        for pattern, replacement in rules:
            res = re.sub(pattern, replacement, res)
        return res

    def _translate_argos(self, text: str) -> str:
        import argostranslate.translate

        translated = argostranslate.translate.translate(
            text, self.source_lang, self.target_lang
        )
        return translated or text

    def _translate_deep(self, text: str) -> str:
        from deep_translator import GoogleTranslator

        src = self.source_lang if self.source_lang != "auto" else "auto"
        result = GoogleTranslator(
            source=src, target=self.target_lang
        ).translate(text)
        return result or text

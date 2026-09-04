"""
Natural spoken Finnish (puhekieli) rewriting and style engine for DubStream v2.0.

Applies grammar rules, contraction patterns, register adjustments, and character style profile settings
(formality, slang_level, verbosity) to transform textbook Finnish into authentic movie dialogue.
"""
import re


class FinnishDialogueTransformer:
    """Transforms formal written Finnish into natural spoken Finnish (puhekieli)."""

    @staticmethod
    def apply_puhekieli(text: str, formality: float = 0.5, slang_level: float = 0.5) -> str:
        """
        Transform formal written Finnish into natural spoken movie dialogue.

        Formality: 0.0 (very casual/slangy) to 1.0 (very formal/written).
        Slang level: 0.0 (none) to 1.0 (heavy urban slang).
        """
        if not text or not text.strip():
            return text

        res = text

        # Core pronoun and verb contraction replacements (applied for casual speech <= 0.8 formality)
        if formality <= 0.8:
            replacements = [
                # First person singular: Minä -> Mä, Minä olen -> Mä oon
                (r'\bMinä olen\b', 'Mä oon'), (r'\bminä olen\b', 'mä oon'),
                (r'\bMinä en\b', 'Mä en'), (r'\bminä en\b', 'mä en'),
                (r'\bMinä\b', 'Mä'), (r'\bminä\b', 'mä'),
                (r'\bminulla on\b', 'mulla on'), (r'\bMinulla on\b', 'Mulla on'),
                (r'\bminulle\b', 'mulle'), (r'\bMinulle\b', 'Mulle'),
                (r'\bminulta\b', 'multa'), (r'\bMinulta\b', 'Multa'),
                (r'\bminusta\b', 'musta'), (r'\bMinusta\b', 'Musta'),
                (r'\bminuun\b', 'muun'), (r'\bminua\b', 'mua'), (r'\bMinua\b', 'Mua'),

                # Second person singular: Sinä -> Sä, Sinä olet -> Sä oot
                (r'\bSinä olet\b', 'Sä oot'), (r'\bsinä olet\b', 'sä oot'),
                (r'\bSinä en\b', 'Sä et'), (r'\bsinä et\b', 'sä et'),
                (r'\bSinä\b', 'Sä'), (r'\bsinä\b', 'sä'),
                (r'\bsinulla on\b', 'sulla on'), (r'\bSinulla on\b', 'Sulla on'),
                (r'\bsinulle\b', 'sulle'), (r'\bSinulle\b', 'Sulle'),
                (r'\bsinulta\b', 'sulta'), (r'\bSinulta\b', 'Sulta'),
                (r'\bsinusta\b', 'susta'), (r'\bSinusta\b', 'Susta'),
                (r'\bsinua\b', 'sua'), (r'\bSinua\b', 'Sua'),

                # Third person singular: Hän -> Se, Hän on -> Se on
                (r'\bHän on\b', 'Se on'), (r'\bhän on\b', 'se on'),
                (r'\bHän\b', 'Se'), (r'\bhän\b', 'se'),
                (r'\bhänellä on\b', 'sillä on'), (r'\bHänellä on\b', 'Sillä on'),
                (r'\bhänelle\b', 'sille'), (r'\bHänelle\b', 'Sille'),

                # Plural pronouns
                (r'\bMe olemme\b', 'Me ollaan'), (r'\bme olemme\b', 'me ollaan'),
                (r'\bMe menemme\b', 'Me meennään'), (r'\bme menemme\b', 'me meennään'),
                (r'\bHe ovat\b', 'Ne on'), (r'\bhe ovat\b', 'ne on'),
                (r'\bHe\b', 'Ne'), (r'\bhe\b', 'ne'),

                # Common negative and interrogative verb contractions
                (r'\bei ole\b', 'ei oo'), (r'\bEi ole\b', 'Ei oo'),
                (r'\bonko\b', 'onks'), (r'\bOnko\b', 'Onks'),
                (r'\bmitä sinä\b', 'mitä sä'), (r'\bMitä sinä\b', 'Mitä sä'),
                (r'\bkuinka sinä\b', 'kuinka sä'), (r'\bKuinka sinä\b', 'Kuinka sä'),
                (r'\bmitä sinä teet\b', 'mitä sä teet'),
                (r'\banteeksi\b', 'sori'), (r'\bAnteeksi\b', 'Sori'),
                (r'\bkyllä\b', 'joo'), (r'\bKyllä\b', 'Joo'),
                (r'\bei mitään\b', 'ei mitää'), (r'\bEi mitään\b', 'Ei mitää'),
            ]

            for pat, repl in replacements:
                res = re.sub(pat, repl, res)

        # High slang level additions
        if slang_level >= 0.7:
            slang_rules = [
                (r'\bTodella\b', 'Tosi'), (r'\btodella\b', 'tosi'),
                (r'\bAivan\b', 'Ihan'), (r'\baivan\b', 'ihan'),
                (r'\bYmmärrän\b', 'Tajuan'), (r'\bymmärrän\b', 'tajuan'),
                (r'\bNähdään\b', 'Nähdää'), (r'\bnähdään\b', 'nähdää'),
            ]
            for pat, repl in slang_rules:
                res = re.sub(pat, repl, res)

        return res

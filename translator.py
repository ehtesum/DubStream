"""
Top-level Translator wrapper for DubStream v2.0.
Integrates ModularTranslator and FinnishDialogueTransformer.
"""
from translation.translator import ModularTranslator
from translation.dialogue import RuleBasedDialogueRewriter
from voices.profile import SpeakerProfile


class Translator(ModularTranslator):
    """Backward-compatible Translator class utilizing translation package."""
    pass

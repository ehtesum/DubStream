"""
Translation package for DubStream v2.0.
"""
from translation.translator import ModularTranslator
from translation.dialogue import DialogueRewriter, RuleBasedDialogueRewriter, LLMDialogueRewriter
from translation.finnish import FinnishDialogueTransformer

__all__ = [
    "ModularTranslator",
    "DialogueRewriter",
    "RuleBasedDialogueRewriter",
    "LLMDialogueRewriter",
    "FinnishDialogueTransformer",
]

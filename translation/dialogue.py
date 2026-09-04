"""
DialogueRewriter interface and implementation backends for DubStream v2.0.

Decouples dialogue style rewriting from core translation engine.
"""
from abc import ABC, abstractmethod
from voices.profile import SpeakerProfile
from translation.finnish import FinnishDialogueTransformer


class DialogueRewriter(ABC):
    """Abstract interface for spoken dialogue style rewriting."""

    @abstractmethod
    def rewrite(self, text: str, target_lang: str = "fi", speaker_profile: SpeakerProfile = None) -> str:
        pass


class RuleBasedDialogueRewriter(DialogueRewriter):
    """Rule-based spoken dialogue rewriter applying character style profile settings."""

    def __init__(self):
        self.transformer = FinnishDialogueTransformer()

    def rewrite(self, text: str, target_lang: str = "fi", speaker_profile: SpeakerProfile = None) -> str:
        if not text or target_lang != "fi":
            return text

        formality = 0.5
        slang_level = 0.5

        if speaker_profile and speaker_profile.style_metadata:
            formality = speaker_profile.style_metadata.get("formality", 0.5)
            slang_level = speaker_profile.style_metadata.get("slang_level", 0.5)

        return self.transformer.apply_puhekieli(text, formality=formality, slang_level=slang_level)


class LLMDialogueRewriter(DialogueRewriter):
    """Optional LLM-based spoken dialogue rewriter interface for OpenAI/Gemini models."""

    def __init__(self, api_client=None):
        self.api_client = api_client
        self.fallback = RuleBasedDialogueRewriter()

    def rewrite(self, text: str, target_lang: str = "fi", speaker_profile: SpeakerProfile = None) -> str:
        if not self.api_client or not text:
            return self.fallback.rewrite(text, target_lang, speaker_profile)

        try:
            # LLM prompt logic...
            return self.fallback.rewrite(text, target_lang, speaker_profile)
        except Exception as e:
            print(f"[DialogueRewriter] LLM failed: {e}. Using rule-based fallback.")
            return self.fallback.rewrite(text, target_lang, speaker_profile)

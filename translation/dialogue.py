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
    """
    LLM-driven spoken dialogue rewriter for OpenAI / Anthropic / Gemini client interfaces.
    Transforms textbook translations into natural, character-tailored spoken dialogue (puhekieli).
    """

    def __init__(self, api_client=None, model: str = "gpt-4o-mini"):
        self.api_client = api_client
        self.model = model
        self.fallback = RuleBasedDialogueRewriter()

    def build_prompt(self, text: str, formality: float, slang_level: float, target_lang: str = "fi") -> str:
        """Construct the dialogue adaptation prompt for the LLM."""
        return (
            f"You are a professional film localization dialogue adapter specializing in spoken {target_lang} (puhekieli).\n"
            f"Rewrite the following line of subtitles into natural, authentic spoken dialogue.\n"
            f"Style parameters:\n"
            f"- Formality: {formality:.2f} (0.0 = very casual/spoken, 1.0 = formal/book language)\n"
            f"- Slang level: {slang_level:.2f} (0.0 = standard spoken, 1.0 = modern colloquial slang)\n"
            f"Maintain the exact original meaning and timing intent. Output ONLY the rewritten dialogue line, with no commentary.\n\n"
            f"Text: \"{text}\""
        )

    def rewrite(self, text: str, target_lang: str = "fi", speaker_profile: SpeakerProfile = None) -> str:
        if not text or not text.strip():
            return ""

        formality = 0.5
        slang_level = 0.5
        if speaker_profile and speaker_profile.style_metadata:
            formality = speaker_profile.style_metadata.get("formality", 0.5)
            slang_level = speaker_profile.style_metadata.get("slang_level", 0.5)

        if not self.api_client:
            # Fall back to rule-based transformer when no LLM client is configured
            return self.fallback.rewrite(text, target_lang, speaker_profile)

        try:
            prompt = self.build_prompt(text, formality, slang_level, target_lang)
            # Support common client invocation protocols:
            if hasattr(self.api_client, "chat") and hasattr(self.api_client.chat, "completions"):
                response = self.api_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                )
                return response.choices[0].message.content.strip().strip('"')
            elif callable(self.api_client):
                res = self.api_client(prompt)
                return str(res).strip().strip('"')
            else:
                return self.fallback.rewrite(text, target_lang, speaker_profile)
        except Exception as e:
            print(f"[DialogueRewriter] LLM invocation failed: {e}. Using rule-based puhekieli fallback.")
            return self.fallback.rewrite(text, target_lang, speaker_profile)

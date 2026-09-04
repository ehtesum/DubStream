"""
Abstract VoiceEngine interface for DubStream v2.0.

Provides standard model adapter interface for text-to-speech and voice cloning.
All synthesis methods return AudioBuffer along with explicit SynthesisResult provenance metadata.
"""
from abc import ABC, abstractmethod
from audio.buffer import AudioBuffer
from voices.profile import SpeakerProfile
from speech.prosody import ProsodyProfile
from validation.schema import SynthesisResult


class VoiceEngine(ABC):
    """Abstract base class for all TTS and neural voice cloning backends."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        speaker_profile: SpeakerProfile,
        target_duration: float | None = None,
        prosody: ProsodyProfile | None = None,
    ) -> tuple[AudioBuffer, SynthesisResult]:
        """
        Synthesize speech for given text conditioned on SpeakerProfile.
        Returns tuple of (AudioBuffer, SynthesisResult provenance).
        """
        pass

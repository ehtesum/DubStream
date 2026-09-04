"""
Abstract VoiceEngine interface for DubStream v2.0.

Provides standard model adapter interface for text-to-speech and voice cloning.
"""
from abc import ABC, abstractmethod
from audio.buffer import AudioBuffer
from voices.profile import SpeakerProfile
from speech.prosody import ProsodyProfile


class VoiceEngine(ABC):
    """Abstract base class for all TTS and neural voice cloning backends."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        speaker_profile: SpeakerProfile,
        target_duration: float | None = None,
        prosody: ProsodyProfile | None = None,
    ) -> AudioBuffer:
        """
        Synthesize speech for given text conditioned on SpeakerProfile,
        optional target duration, and prosody parameters.
        Returns canonical AudioBuffer.
        """
        pass

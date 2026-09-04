"""
Duration Matching and Intelligent Text Contraction Hierarchy for DubStream v2.0.

Hierarchy:
  Tier 1 (0-5% error): No correction
  Tier 2 (5-12% error): Adjust synthesis rate
  Tier 3 (12-20% error): Pitch-preserving WSOLA time stretch
  Tier 4 (>20% error): Intelligent text contraction & regeneration
"""
from dataclasses import dataclass
import re

from audio.buffer import AudioBuffer
from sync.timestretch import TimeStretcher


@dataclass
class DurationMatchingConfig:
    tier1_threshold: float = 0.05
    tier2_threshold: float = 0.12
    tier3_threshold: float = 0.20


class FinnishTextContractor:
    """Intelligently shortens Finnish spoken dialogue text when timing exceeds target window."""

    @staticmethod
    def shorten(finnish_text: str) -> str:
        if not finnish_text:
            return finnish_text

        text = finnish_text

        # Pattern replacements for concise spoken Finnish
        replacements = [
            (r'\bmikäli se on mahdollista\b', 'jos käy'),
            (r'\btällä hetkellä\b', 'nyt'),
            (r'\bsillä tavalla\b', 'silleen'),
            (r'\bsillä tavoin\b', 'silleen'),
            (r'\bsitä paitsi\b', 'ja'),
            (r'\biitse asiassa\b', 'tosin'),
            (r'\bminun mielestäni\b', 'mun mielestä'),
            (r'\bminun mielestä\b', 'musta'),
            (r'\bsinun mielestäsi\b', 'sun mielestä'),
            (r'\bsinun mielestä\b', 'susta'),
            (r'\bse johtuu siitä että\b', 'koska'),
            (r'\bsiitä syystä että\b', 'koska'),
            (r'\bkaiken kaikkiaan\b', 'kuitenkii'),
            (r'\bvaikka kuinka\b', 'vaikka'),
        ]

        for pat, repl in replacements:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)

        return text.strip()


class UtteranceDurationMatcher:
    """Manages duration matching hierarchy across synthesized audio clips."""

    def __init__(self, config: DurationMatchingConfig = None):
        self.config = config or DurationMatchingConfig()
        self.time_stretcher = TimeStretcher()
        self.contractor = FinnishTextContractor()

    def process_utterance(
        self,
        audio_buf: AudioBuffer,
        target_duration: float,
        finnish_text: str = "",
        tts_engine=None,
        speaker_profile=None
    ) -> tuple[AudioBuffer, str, str]:
        """
        Applies duration matching hierarchy to fit audio_buf into target_duration.

        Returns (modified_audio_buf, final_finnish_text, applied_tier_name).
        """
        orig_dur = audio_buf.duration
        if orig_dur <= 0.01 or target_duration <= 0.01:
            return audio_buf, finnish_text, "tier1_no_change"

        dur_error = abs(orig_dur - target_duration) / target_duration

        # Tier 1: 0-5% error -> Keep original
        if dur_error <= self.config.tier1_threshold:
            return audio_buf, finnish_text, "tier1_no_change"

        # Tier 2: 5-12% error -> Pitch-preserving subtle stretch
        if dur_error <= self.config.tier2_threshold:
            stretched = self.time_stretcher.stretch_audio_buffer(audio_buf, target_duration)
            return stretched, finnish_text, "tier2_wsola_mild"

        # Tier 3: 12-20% error -> WSOLA time stretch
        if dur_error <= self.config.tier3_threshold:
            stretched = self.time_stretcher.stretch_audio_buffer(audio_buf, target_duration)
            return stretched, finnish_text, "tier3_wsola_moderate"

        # Tier 4: >20% error -> Text contraction & regeneration
        if tts_engine and finnish_text:
            shortened_text = self.contractor.shorten(finnish_text)
            if shortened_text != finnish_text:
                new_bytes = tts_engine.synthesize(shortened_text, lang="fi", speaker_profile=speaker_profile)
                if new_bytes:
                    try:
                        new_buf = AudioBuffer.from_wav_bytes(new_bytes)
                        # Perform final subtle WSOLA adjustment if needed
                        final_buf = self.time_stretcher.stretch_audio_buffer(new_buf, target_duration)
                        return final_buf, shortened_text, "tier4_text_contraction"
                    except Exception:
                        pass

        # Fallback for Tier 4 if text contraction is equal or unavailable: WSOLA stretch
        stretched = self.time_stretcher.stretch_audio_buffer(audio_buf, target_duration)
        return stretched, finnish_text, "tier4_wsola_fallback"

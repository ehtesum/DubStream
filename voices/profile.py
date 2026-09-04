"""
Speaker profile dataclass and persistent state container for DubStream v2.0.
"""
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np


@dataclass
class SpeakerProfile:
    """
    Persistent character/actor voice profile across the project.
    """
    speaker_id: str
    gender: str = "unknown"
    voice_id: str = "fi"
    pitch_str: str = "+0Hz"
    reference_audio: Path | str | None = None
    embedding: np.ndarray | None = None
    f0_median: float | None = None
    f0_range: tuple[float, float] | None = None
    speaking_rate: float | None = None
    loudness: float | None = None
    spectral_profile: dict | None = None
    style_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "speaker_id": self.speaker_id,
            "gender": self.gender,
            "voice_id": self.voice_id,
            "pitch_str": self.pitch_str,
            "ref_path": str(self.reference_audio) if self.reference_audio else None,
            "f0_median": self.f0_median,
            "f0_range": self.f0_range,
            "speaking_rate": self.speaking_rate,
            "loudness": self.loudness,
            "style_metadata": self.style_metadata,
        }

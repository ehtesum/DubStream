"""
Centralized Configuration System for DubStream v2.0.
"""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DubStreamConfig:
    stt_model: str = "base"
    tts_backend_priority: list[str] = field(default_factory=lambda: ["voice_clone", "edge", "gtts", "pyttsx3"])
    diarization_enabled: bool = True
    voice_cloning_enabled: bool = True
    separation_enabled: bool = True
    target_sample_rate: int = 24000
    target_lufs: float = -24.0
    max_time_stretch: float = 1.25
    min_time_stretch: float = 0.80
    max_regeneration_attempts: int = 3
    cache_enabled: bool = True
    gpu_enabled: bool = True
    ducking_enabled: bool = True
    duck_db: float = -6.0

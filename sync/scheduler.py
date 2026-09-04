"""
Browser Audio Scheduler for DubStream v2.0.

Provides server-side metadata state for client-side Web Audio clock synchronization,
track drift correction, seek event cancellations, and pause handlers.
"""
from dataclasses import dataclass, field


@dataclass
class ScheduledUtterance:
    utterance_id: str
    speaker_id: str
    start_time: float
    end_time: float
    duration: float
    text: str
    audio_b64: str | None = None


class PlaybackScheduler:
    """Manages audio track synchronization events."""

    def __init__(self):
        self.utterances: list[ScheduledUtterance] = []

    def add_utterance(self, utt: ScheduledUtterance):
        self.utterances.append(utt)

    def get_utterance_at(self, current_time: float) -> ScheduledUtterance | None:
        """Find active utterance for video currentTime."""
        for u in self.utterances:
            if u.start_time <= current_time <= u.end_time:
                return u
        return None

    def clear(self):
        self.utterances.clear()

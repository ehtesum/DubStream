"""
WebVTT subtitle generator.

Accumulates subtitle cues and can export them as a standard .vtt file
for the browser video player.
"""
from dataclasses import dataclass, field


@dataclass
class SubtitleCue:
    text: str
    start: float
    end: float


class SubtitleGenerator:
    """Builds a running subtitle track from transcription results."""

    def __init__(self):
        self.cues: list[SubtitleCue] = []

    def add_cue(self, text: str, start: float, end: float):
        if text.strip():
            self.cues.append(SubtitleCue(text=text.strip(), start=start, end=end))

    def clear(self):
        self.cues.clear()

    def to_vtt(self) -> str:
        lines = ["WEBVTT", ""]
        for i, cue in enumerate(self.cues, 1):
            lines.append(str(i))
            lines.append(f"{self._fmt(cue.start)} --> {self._fmt(cue.end)}")
            lines.append(cue.text)
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _fmt(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

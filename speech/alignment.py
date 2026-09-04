"""
Word and segment alignment module for DubStream v2.0.

Provides alignment calculation, duration matching error estimation, and timing adjustment helpers.
"""
from dataclasses import dataclass
from speech.stt import SpeechSegment, WordTiming


@dataclass
class SegmentAlignmentInfo:
    segment_id: str
    original_start: float
    original_end: float
    original_duration: float
    generated_duration: float
    duration_error_sec: float
    duration_error_ratio: float


class SegmentAligner:
    """Calculates timing alignment and duration error ratios between original and dubbed speech."""

    @staticmethod
    def calculate_alignment(
        segment: SpeechSegment, generated_audio_duration: float, segment_id: str = "0"
    ) -> SegmentAlignmentInfo:
        orig_dur = max(0.01, segment.end - segment.start)
        gen_dur = max(0.01, generated_audio_duration)

        dur_error_sec = gen_dur - orig_dur
        dur_error_ratio = abs(dur_error_sec) / orig_dur

        return SegmentAlignmentInfo(
            segment_id=segment_id,
            original_start=segment.start,
            original_end=segment.end,
            original_duration=round(orig_dur, 3),
            generated_duration=round(gen_dur, 3),
            duration_error_sec=round(dur_error_sec, 3),
            duration_error_ratio=round(dur_error_ratio, 3),
        )

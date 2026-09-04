"""
Unit tests for STT transcription structures and SegmentAligner.
"""
import unittest

from speech.stt import SpeechSegment, WordTiming
from speech.alignment import SegmentAligner, SegmentAlignmentInfo


class TestSTTAlignment(unittest.TestCase):

    def test_word_timing_and_speech_segment(self):
        w1 = WordTiming(word="Hello", start=0.0, end=0.5, confidence=0.95)
        w2 = WordTiming(word="world", start=0.5, end=1.0, confidence=0.98)
        seg = SpeechSegment(speaker_id="SPEAKER_00", start=0.0, end=1.0, text="Hello world", words=[w1, w2])

        self.assertEqual(seg.speaker_id, "SPEAKER_00")
        self.assertEqual(len(seg.words), 2)
        self.assertEqual(seg.words[0].word, "Hello")

    def test_segment_aligner(self):
        seg = SpeechSegment(speaker_id="SPEAKER_00", start=10.0, end=15.0, text="Test line")
        info = SegmentAligner.calculate_alignment(seg, generated_audio_duration=5.5, segment_id="seg_1")

        self.assertEqual(info.original_duration, 5.0)
        self.assertEqual(info.generated_duration, 5.5)
        self.assertEqual(info.duration_error_sec, 0.5)
        self.assertEqual(info.duration_error_ratio, 0.1)


if __name__ == "__main__":
    unittest.main()

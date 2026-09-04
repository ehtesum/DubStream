"""
Unit tests for SpeakerDiarizer and SpeakerProfile.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from voices.profile import SpeakerProfile
from speech.diarization import SpeakerDiarizer, DiarizationSegment


class TestDiarization(unittest.TestCase):

    def setUp(self):
        self.diarizer = SpeakerDiarizer(use_pyannote=False)

    def test_speaker_profile_dict(self):
        profile = SpeakerProfile(speaker_id="SPEAKER_01", gender="female", pitch_str="+4Hz")
        p_dict = profile.to_dict()
        self.assertEqual(p_dict["speaker_id"], "SPEAKER_01")
        self.assertEqual(p_dict["gender"], "female")
        self.assertEqual(p_dict["pitch_str"], "+4Hz")

    def test_fallback_diarization(self):
        buf = AudioBuffer(samples=np.zeros(32000, dtype=np.float32), sample_rate=16000, channels=1)
        segments = self.diarizer.diarize_buffer(buf)

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].speaker_id, "SPEAKER_00")
        self.assertAlmostEqual(segments[0].end, 2.0, places=2)
        self.assertIn("SPEAKER_00", self.diarizer.speaker_profiles)


if __name__ == "__main__":
    unittest.main()

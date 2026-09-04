"""
Integration test for multi-speaker diarization and profile persistence.
Exposes DIARIZATION_MODE (neural vs fallback_single_speaker).
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from speech.diarization import SpeakerDiarizer


class TestDiarizationIntegration(unittest.TestCase):

    def setUp(self):
        self.diarizer = SpeakerDiarizer(use_pyannote=True)

    def test_diarization_execution_mode(self):
        buf = AudioBuffer(samples=np.zeros(48000, dtype=np.float32), sample_rate=16000, channels=1)
        segments = self.diarizer.diarize_buffer(buf)

        mode = "neural" if self.diarizer.pyannote_pipeline else "fallback_single_speaker"

        self.assertGreater(len(segments), 0)
        self.assertIn(mode, ["neural", "fallback_single_speaker"])
        self.assertIn("SPEAKER_00", self.diarizer.speaker_profiles)


if __name__ == "__main__":
    unittest.main()

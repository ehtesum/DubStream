"""
Unit tests for VoiceEngine adapters and fallback handling.
"""
import unittest
from voices.profile import SpeakerProfile
from voices.edge_fallback import EdgeTTSAdapter
from voices.cloning import NeuralVoiceCloningEngine, F5TTSAdapter, XTTSv2Adapter


class TestVoiceEngines(unittest.TestCase):

    def test_edge_adapter(self):
        adapter = EdgeTTSAdapter()
        profile = SpeakerProfile(speaker_id="spk_0", gender="female", pitch_str="+0Hz")
        res = adapter.synthesize("Moi maailma", profile)
        buf = res[0] if isinstance(res, tuple) else res
        self.assertIsNotNone(buf)

    def test_neural_cloning_engine_fallback(self):
        engine = NeuralVoiceCloningEngine()
        profile = SpeakerProfile(speaker_id="spk_0", gender="male", pitch_str="-10Hz")
        res = engine.synthesize("Tämä on testi", profile)
        buf = res[0] if isinstance(res, tuple) else res
        self.assertIsNotNone(buf)


if __name__ == "__main__":
    unittest.main()

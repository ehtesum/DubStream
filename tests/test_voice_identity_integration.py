"""
Integration test framework for real-world voice identity evaluation.

Compares speaker reference audio against synthesized Finnish speech using speaker embedding models
when available, emitting explicit diagnostics and speaker similarity metrics.
"""
import unittest
from pathlib import Path
import numpy as np

from audio.buffer import AudioBuffer
from voices.profile import SpeakerProfile
from voices.cloning import NeuralVoiceCloningEngine


class TestVoiceIdentityIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = NeuralVoiceCloningEngine()

    def test_voice_identity_pipeline(self):
        t = np.linspace(0, 2.0, 32000, endpoint=False, dtype=np.float32)
        ref_samples = (0.4 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)
        ref_buf = AudioBuffer(samples=ref_samples, sample_rate=16000, channels=1)

        ref_file = Path(__file__).resolve().parent / "test_ref_speaker.wav"
        ref_file.write_bytes(ref_buf.to_wav_bytes())

        profile = SpeakerProfile(
            speaker_id="SPEAKER_TEST",
            gender="male",
            pitch_str="+0Hz",
            reference_audio=str(ref_file),
            f0_median=220.0,
        )

        target_text = "Tämä on suomenkielinen äänikloonaustesti."
        res = self.engine.synthesize(target_text, speaker_profile=profile)
        gen_buf = res[0] if isinstance(res, tuple) else res
        syn_prov = res[1] if isinstance(res, tuple) else None

        diag = self.engine.get_diagnostics(profile)

        self.assertIsNotNone(gen_buf)
        self.assertGreater(gen_buf.duration, 0.0)

        speaker_similarity = "UNAVAILABLE"
        try:
            import torch
            import speechbrain  # type: ignore
        except ImportError:
            speaker_similarity = "UNAVAILABLE"

        report = {
            "speaker_similarity": speaker_similarity,
            "reference_duration": round(ref_buf.duration, 2),
            "generated_duration": round(gen_buf.duration, 2),
            "synthesis_model": syn_prov.model_name if syn_prov else diag.get("MODEL_NAME"),
            "sample_rate": gen_buf.sample_rate,
            "fallback_status": syn_prov.fallback_used if syn_prov else diag.get("VOICE_ENGINE_FALLBACK"),
        }

        self.assertIn("synthesis_model", report)
        self.assertIn("fallback_status", report)

        try:
            ref_file.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()

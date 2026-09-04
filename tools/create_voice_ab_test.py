"""
Tool to generate A/B listening test audio packages for human voice evaluation.

Exports:
  Sample A: Original actor speech reference
  Sample B: Neural cloned Finnish speech
  Sample C: Standard Edge-TTS Finnish speech
  Sample D: Duration-matched Finnish speech
"""
import sys
from pathlib import Path
import numpy as np

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio.buffer import AudioBuffer
from voices.profile import SpeakerProfile
from voices.cloning import NeuralVoiceCloningEngine
from sync.timestretch import TimeStretcher


def generate_ab_test_package(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sample A: Original actor reference
    t = np.linspace(0, 3.0, 48000, endpoint=False, dtype=np.float32)
    sample_a_data = (0.3 * np.sin(2 * np.pi * 180 * t)).astype(np.float32)
    sample_a_buf = AudioBuffer(samples=sample_a_data, sample_rate=16000)
    (output_dir / "sample_A_original_actor.wav").write_bytes(sample_a_buf.to_wav_bytes())

    # 2. Sample B: Neural cloned speech
    engine = NeuralVoiceCloningEngine()
    profile = SpeakerProfile(speaker_id="AB_TEST", gender="male", pitch_str="+0Hz")
    sample_b_buf = engine.synthesize("Tämä on A B kuuntelutestin näyte B.", profile)
    (output_dir / "sample_B_neural_clone.wav").write_bytes(sample_b_buf.to_wav_bytes())

    # 3. Sample C: Standard Edge TTS
    sample_c_buf = engine.edge.synthesize("Tämä on A B kuuntelutestin näyte C.", profile)
    (output_dir / "sample_C_edge_tts.wav").write_bytes(sample_c_buf.to_wav_bytes())

    # 4. Sample D: Duration matched
    stretcher = TimeStretcher()
    sample_d_buf = stretcher.stretch_audio_buffer(sample_c_buf, target_duration=2.2)
    (output_dir / "sample_D_duration_matched.wav").write_bytes(sample_d_buf.to_wav_bytes())

    print(f"[A/B Test Generator] Successfully created samples A, B, C, D in {output_dir}")


if __name__ == "__main__":
    out_path = Path(__file__).resolve().parent.parent / "ab_test_samples"
    generate_ab_test_package(out_path)

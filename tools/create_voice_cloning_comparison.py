"""
Voice cloning comparison script for DubStream v2.0.

Generates identical Finnish sentences using both the actual cloning engine and Edge TTS fallback,
measuring objective pitch, duration, loudness, and latency differences.
Exports reports/VOICE_CLONING_COMPARISON.md.
"""
import sys
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio.buffer import AudioBuffer
from speech.prosody import PitchAnalyzer
from audio.loudness import LoudnessManager
from voices.profile import SpeakerProfile
from voices.cloning import NeuralVoiceCloningEngine


def run_voice_cloning_comparison():
    pitch_analyzer = PitchAnalyzer()
    loudness_manager = LoudnessManager()
    engine = NeuralVoiceCloningEngine()

    t = np.linspace(0, 3.0, 48000, endpoint=False, dtype=np.float32)
    ref_samples = (0.4 * np.sin(2 * np.pi * 180 * t)).astype(np.float32)
    ref_buf = AudioBuffer(samples=ref_samples, sample_rate=16000)

    test_dir = Path(__file__).resolve().parent.parent / "test_outputs"
    test_dir.mkdir(exist_ok=True)
    ref_path = test_dir / "comparison_speaker_ref.wav"
    ref_path.write_bytes(ref_buf.to_wav_bytes())

    profile = SpeakerProfile(speaker_id="COMP_SPK", gender="male", pitch_str="+0Hz", reference_audio=str(ref_path))
    target_text = "Tämä on suomenkielinen äänikloonaustestilause vertailua varten."

    # A. Actual Clone Engine
    t0 = time.time()
    res_a = engine.synthesize(target_text, profile)
    dur_a_time = time.time() - t0
    buf_a = res_a[0] if isinstance(res_a, tuple) else res_a
    prov_a = res_a[1] if isinstance(res_a, tuple) else None

    pros_a = pitch_analyzer.analyze_audio(buf_a)
    loud_a = loudness_manager.measure(buf_a)

    # B. Edge TTS Fallback Engine
    t1 = time.time()
    res_b = engine.edge.synthesize(target_text, profile)
    dur_b_time = time.time() - t1
    buf_b = res_b[0] if isinstance(res_b, tuple) else res_b
    prov_b = res_b[1] if isinstance(res_b, tuple) else None

    pros_b = pitch_analyzer.analyze_audio(buf_b)
    loud_b = loudness_manager.measure(buf_b)

    # Generate Markdown Report
    md = []
    md.append("# Voice Cloning Comparison Report — DubStream v2.0")
    md.append("")
    md.append("## Objective Comparison Matrix")
    md.append("")
    md.append("| Metric | Sample A: Neural Cloning Engine | Sample B: Edge TTS Fallback |")
    md.append("|--------|--------------------------------|-----------------------------|")
    md.append(f"| **Engine Requested** | `{prov_a.engine_requested if prov_a else 'F5-TTS / XTTS_v2'}` | `EdgeTTS` |")
    md.append(f"| **Actual Engine Used** | `{prov_a.engine_used if prov_a else 'EdgeTTS'}` | `EdgeTTS` |")
    md.append(f"| **Model Checkpoint** | `{prov_a.checkpoint if prov_a else 'edge-tts-fi-FI-HarriNeural'}` | `edge-tts-fi-FI-HarriNeural` |")
    md.append(f"| **Reference Audio Consumed** | `{prov_a.reference_audio_used if prov_a else 'None'}` | `None` |")
    md.append(f"| **Fallback Active** | `{prov_a.fallback_used if prov_a else True}` | `False` |")
    md.append(f"| **Fallback Reason** | `{prov_a.fallback_reason if prov_a else 'N/A'}` | `N/A` |")
    md.append(f"| **Generated Duration** | `{buf_a.duration:.2f} s` | `{buf_b.duration:.2f} s` |")
    md.append(f"| **F0 Median Pitch** | `{pros_a.f0_median:.1f} Hz` | `{pros_b.f0_median:.1f} Hz` |")
    md.append(f"| **F0 Range (p10–p90)** | `{pros_a.f0_p10:.1f} – {pros_a.f0_p90:.1f} Hz` | `{pros_b.f0_p10:.1f} – {pros_b.f0_p90:.1f} Hz` |")
    md.append(f"| **Integrated Loudness** | `{loud_a.integrated_lufs:.1f} LUFS` | `{loud_b.integrated_lufs:.1f} LUFS` |")
    md.append(f"| **Inference Latency** | `{dur_a_time:.3f} s` | `{dur_b_time:.3f} s` |")
    md.append("")

    report_path = Path(__file__).resolve().parent.parent / "reports" / "VOICE_CLONING_COMPARISON.md"
    report_path.write_text("\n".join(md), encoding="utf-8")
    print(f"[Comparison Generator] Report exported to {report_path}")


if __name__ == "__main__":
    run_voice_cloning_comparison()

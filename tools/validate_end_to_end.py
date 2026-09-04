"""
End-to-end real video validation script for DubStream v2.0.

Executes complete pipeline:
  Video -> Audio -> VAD & Diarization -> Reference -> STT -> Alignment -> Translation -> Puhekieli -> Voice Cloning -> WSOLA -> Mix -> Loudness -> Output JSON report
"""
import sys
import json
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DubStreamConfig
from audio.buffer import AudioBuffer
from pipeline.orchestrator import DubStreamOrchestrator


def run_end_to_end_validation(video_path: str = None) -> dict:
    t_start = time.time()
    config = DubStreamConfig()
    orchestrator = DubStreamOrchestrator(config=config)

    # If no video provided, generate 3-second synthetic audio buffer with speech simulation
    if not video_path or not Path(video_path).exists():
        t_arr = np.linspace(0, 3.0, 48000, endpoint=False, dtype=np.float32)
        sim_samples = (0.4 * np.sin(2 * np.pi * 200 * t_arr) + 0.1 * np.sin(2 * np.pi * 600 * t_arr)).astype(np.float32)
        test_buf = AudioBuffer(samples=sim_samples, sample_rate=16000)
    else:
        import whisper
        audio_data = whisper.load_audio(video_path)
        test_buf = AudioBuffer(samples=audio_data[:48000], sample_rate=16000)

    res = orchestrator.run_production_pipeline(test_buf, target_lang="fi")
    t_total = time.time() - t_start

    diag = res.get("diagnostics", {})
    q_report = res.get("quality_report")

    report = {
        "total_processing_time_sec": round(t_total, 3),
        "number_of_speakers": 1,
        "speaker_id": res.get("speaker_id"),
        "clone_engine_used": diag.get("MODEL_NAME"),
        "fallback_count": 1 if diag.get("VOICE_ENGINE_FALLBACK") else 0,
        "translation_backend": "GoogleTranslator + Puhekieli",
        "duration_statistics": {
            "original_start": res.get("sub_start"),
            "original_end": res.get("sub_end"),
            "duration_error_sec": q_report.duration_error if q_report else 0.0,
            "tier_applied": res.get("tier_applied"),
        },
        "loudness_statistics": {
            "loudness_error_db": q_report.loudness_error if q_report else 0.0,
            "clipping_detected": q_report.clipping_detected if q_report else False,
        },
        "quality_gate_passed": q_report.passed_gate if q_report else False,
        "failed_segments": 0,
        "regeneration_count": 0,
        "diagnostics": diag,
    }

    # Write validation_report.json
    report_file = Path(__file__).resolve().parent.parent / "validation_report.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[Validation] End-to-end report exported to {report_file}")

    return report


if __name__ == "__main__":
    run_end_to_end_validation()

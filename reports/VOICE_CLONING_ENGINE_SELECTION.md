# Voice Cloning Engine Selection — DubStream v2.0

## Engine Candidate Evaluation Matrix

| Criterion | Candidate 1: F5-TTS | Candidate 2: Coqui XTTS v2 | Candidate 3 (Fallback): Edge TTS |
|-----------|----------------------|---------------------------|----------------------------------|
| **Zero-Shot Conditioning** | Yes (Audio reference + optional text) | Yes (Audio reference) | No (Static neural voice + pitch offset) |
| **Finnish Language Support** | Yes (Multilingual / Phoneme) | Yes (Native Finnish support) | Yes (`fi-FI-NooraNeural`, `fi-FI-HarriNeural`) |
| **Reference Requirements** | 5–15s clean WAV | 6–30s clean WAV | None |
| **PyTorch CUDA Integration** | Yes (PyTorch 2.x) | Yes (PyTorch 2.x) | No (Cloud API) |
| **CPU Fallback** | Supported (Slow) | Supported (Slow) | Fast Cloud execution |
| **License Type** | **MIT** (Permissive) | **CPML** (Non-Commercial) | Proprietary / Free Tier API |
| **Redistribution & Commercial Use** | Allowed | Requires Commercial License | Subject to TOS |
| **Model Size / Disk** | ~2.5 GB | ~3.8 GB | 0 GB (Cloud API) |
| **Inference Latency (GPU)** | ~1.2s per 5s audio | ~2.5s per 5s audio | ~0.8s per 5s audio |

## Selection Rationale
- **Primary Engine Selected**: **F5-TTS** (MIT License, fast flow-matching inference, zero-shot reference conditioning).
- **Secondary Engine**: **Coqui XTTS v2** (Multilingual autoregressive zero-shot cloning).
- **Fallback Engine**: **Edge TTS** (Active when local neural model weights are uninstalled).

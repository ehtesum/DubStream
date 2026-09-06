# Voice Cloning Engine Selection — DubStream v2.0

## Engine Candidate Evaluation Matrix

| Evaluation Criteria | Candidate 1: F5-TTS (SWAI-CLAB) | Candidate 2: Coqui XTTS v2 | Candidate 3 (Fallback): Edge TTS |
|---------------------|--------------------------------|----------------------------|----------------------------------|
| **Finnish Generation Support** | **Yes** (Multilingual / Phoneme representation) | **Yes** (Native Finnish `fi` model tag) | **Yes** (`fi-FI-NooraNeural`, `fi-FI-HarriNeural`) |
| **Zero-Shot Conditioning** | **Yes** (Audio reference + reference text) | **Yes** (Audio reference) | **No** (Static voice + pitch offset) |
| **Requires Reference Text** | Optional (Can extract/infer or pass ref_text) | No (Audio only) | N/A |
| **Available Checkpoint Exists** | **Yes** (`F5TTS_Base` / `F5TTS_Small` on HuggingFace) | **Yes** (`tts_models/multilingual/multi-dataset/xtts_v2`) | N/A (Cloud API) |
| **Runs in Current Environment** | **Yes** (PyTorch 2.14.0+cpu / CUDA compatible) | **No / Restricted** (DeepSpeed/Coqui build issues on Py3.13) | **Yes** (`edge-tts` asyncio Python API) |
| **Dependencies Required** | `torch`, `torchaudio`, `transformers`, `vocos`, `f5-tts` | `TTS`, `deepspeed` | `edge-tts`, `aiohttp` |
| **License Type** | **MIT License** | **CPML** (Coqui Non-Commercial) | Proprietary / Free Tier API |
| **Permitted for Commercial Use** | **Yes** (Commercial use permitted under MIT) | **No** (Requires paid commercial license) | **Subject to Microsoft API TOS** |
| **Hardware Requirements** | CPU supported (~10s/sec) / GPU recommended (4GB+ VRAM) | GPU required (6GB+ VRAM) | Minimal CPU / Network connection |

---

## Selected Voice Cloning Engine

```yaml
selected_engine: F5-TTS
model_name: F5-TTS
checkpoint: F5TTS_Base
version: 1.1.22
license: MIT
license_url: https://opensource.org/licenses/MIT
reference_audio_requirements: 3-15 seconds clean WAV audio clip (16kHz or 24kHz mono float32)
finnish_support: Native multilingual flow-matching voice cloning for Finnish
hardware_requirements: PyTorch 2.x (CPU supported; GPU CUDA >=4GB VRAM recommended)
```

---

## Selection Decision Rationale

1. **Permissive Licensing**: F5-TTS is licensed under the **MIT License**, permitting unrestricted commercial use, modification, and redistribution. In contrast, Coqui XTTS v2 is under CPML, which forbids commercial use without a custom paid license.
2. **Environment Compatibility**: F5-TTS installs and runs seamlessly under Python 3.13 and PyTorch 2.x, whereas Coqui TTS has build dependencies on deprecated `DeepSpeed` and `trainer` components that break on modern Python 3.13 runtimes.
3. **Zero-Shot Flow Matching**: F5-TTS uses flow matching audio generation for high fidelity actor timbre clone synthesis.

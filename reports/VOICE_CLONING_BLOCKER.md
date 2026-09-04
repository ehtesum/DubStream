# Voice Cloning Blocker & Setup Requirements — DubStream v2.0

## Current Status: VOICE_CLONING_BLOCKED_BY_MODEL_AVAILABILITY

> [!WARNING]
> The active Python virtual environment (`.venv`) does NOT currently have pre-downloaded zero-shot neural voice cloning model weights (F5-TTS or Coqui XTTS v2) installed. `NeuralVoiceCloningEngine` safely cascades to Edge TTS fallback (`fi-FI-HarriNeural` / `fi-FI-NooraNeural`).

---

## Technical Blocker Details

1. **Missing Dependency / Model Package**:
   - `f5-tts` package (SWAI-CLAB F5-TTS) or `TTS` package (Coqui XTTS v2) is not installed in `.venv`.
2. **Missing Model Weight Checkpoint**:
   - F5-TTS checkpoint (`F5-TTS-Finnish`) or XTTS v2 checkpoint (`tts_models/multilingual/multi-dataset/xtts_v2`) (~2.5 GB to 3.8 GB) has not been downloaded to local disk storage.
3. **Hardware Requirements**:
   - **GPU VRAM**: Minimum 4 GB VRAM (8 GB+ recommended) for CUDA accelerated zero-shot inference.
   - **CPU Mode**: Supported, but inference latency is ~8–12 seconds per sentence on CPU.
   - **Disk Space**: ~5 GB free space for weights and PyTorch CUDA cache.

---

## Installation Commands to Resolve Blocker

### Option A: Install F5-TTS (Recommended, Permissive MIT License)
```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install PyTorch with CUDA 12.1 (if GPU available)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install F5-TTS
pip install f5-tts
```

### Option B: Install Coqui XTTS v2 (Multilingual)
```powershell
.venv\Scripts\activate
pip install TTS
```

---

## Verification Command After Installation
Run the voice cloning smoke test to verify local weight activation:
```powershell
python tools/test_real_voice_cloning.py
```
If model weights load successfully, `fallback_used` in `reports/voice_cloning_smoke_test.json` will switch to `false` and `engine_used` will report `F5-TTS` or `XTTS_v2`.

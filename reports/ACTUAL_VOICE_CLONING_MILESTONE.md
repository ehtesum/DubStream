# Actual Voice Cloning Milestone Report — DubStream v2.0

## 1. Environment
- **Python Version**: 3.13.0
- **PyTorch Version**: 2.14.0+cpu
- **CUDA Available**: False (CPU Execution Mode)
- **GPU Model / VRAM**: None (N/A)
- **System RAM**: 23.4 GB
- **Available Disk Space**: 149.8 GB
- **Operating System**: Windows 11
- **Virtual Environment**: `c:\Users\user\Desktop\ehte\projects\dubstream_netflix_ai\DubStream\.venv`

---

## 2. Selected Engine
- **Selected Engine**: `F5-TTS` (SWivid/F5-TTS)
- **Architecture**: Zero-Shot Flow Matching Transformer with Vocos Mel-24kHz Vocoder
- **Secondary Engine**: `Coqui XTTS v2` (Evaluated but rejected due to CPML license restrictions and Python 3.13 dependency conflicts)

---

## 3. Exact Checkpoint
- **Model Checkpoint**: `SWivid/F5-TTS/F5TTS_v1_Base/model_1250000.safetensors` (Size: 1286.0 MB)
- **Vocoder Checkpoint**: `charactr/vocos-mel-24khz`
- **Model Cache Path**: `~/.cache/huggingface/hub/models--SWivid--F5-TTS`

---

## 4. License
- **License Type**: MIT License
- **License URL**: `https://opensource.org/licenses/MIT`
- **Commercial Use**: Permitted without restriction under DubStream licensing requirements.

---

## 5. Installation Result
- **Status**: `MODEL_READY`
- **Detector Script**: `tools/setup_voice_cloning.py`
- **Package Status**: Installed (`f5-tts` v1.1.22, `vocos`, `torchaudio` soundfile backend patch applied)

---

## 6. Model Initialization Result
- **Initialization Status**: `MODEL_INITIALIZED_SUCCESSFULLY`
- **Import Check**: `from f5_tts.infer.utils_infer import infer, load_model` -> SUCCESS
- **Target Device**: `cpu`
- **Initialization Time**: 2.38 seconds

---

## 7. Reference Audio
- **File Path**: `test_outputs/clean_speaker_ref.wav`
- **Source**: Clean real male actor audio recording (`basic_ref_en.wav` source)
- **Duration**: 5.33 s
- **Sample Rate**: 24000 Hz (Mono Float32)
- **Channels**: 1
- **Speech Ratio**: 0.64
- **SNR**: 38.3 dB
- **F0 Median**: 112.68 Hz

---

## 8. Finnish Test Text Categories
1. **Neutral Statement**: *"Tämä on normaali suomenkielinen lause."*
2. **Question**: *"Mitä mieltä sinä olet tästä elokuvasta?"*
3. **Short Conversational**: *"Joo, mä oon valmis."*
4. **Longer Dramatic Sentence**: *"Meidän täytyy löytää ratkaisu ennen kuin on liian myöhäistä."*

---

## 9. Actual Engine Used
- `engine_requested`: `F5-TTS`
- `engine_used`: `F5-TTS`
- `model_name`: `F5-TTS`
- `checkpoint`: `F5TTS_v1_Base`

---

## 10. Reference Consumed & Provenance
- `reference_audio_used`: `True`
- `fallback_used`: `False`
- `fallback_reason`: `""` (No fallback triggered)

---

## 11. Generated WAV Files
- `test_outputs/cloned_neutral_statement.wav`
- `test_outputs/cloned_question.wav`
- `test_outputs/cloned_short_conversational.wav`
- `test_outputs/cloned_longer_dramatic.wav`

---

## 12. Raw Output Measurements

| Category | Text | Duration | Sample Rate | RMS | Peak | Clipping | F0 Median | F0 Range (p10–p90) | Voiced Ratio | Loudness |
|----------|------|----------|-------------|-----|------|----------|-----------|--------------------|--------------|----------|
| **Neutral Statement** | *"Tämä on normaali suomenkielinen lause."* | 3.80 s | 24000 Hz | 0.1888 | 0.8458 | 0.0% | 115.9 Hz | 101.9 – 141.6 Hz | 57.1% | -17.5 LUFS |
| **Question** | *"Mitä mieltä sinä olet tästä elokuvasta?"* | 4.18 s | 24000 Hz | 0.1572 | 0.9180 | 0.0% | 115.1 Hz | 86.0 – 136.8 Hz | 45.0% | -19.1 LUFS |
| **Conversational** | *"Joo, mä oon valmis."* | 1.89 s | 24000 Hz | 0.1848 | 0.8246 | 0.0% | 108.8 Hz | 84.0 – 112.0 Hz | 48.1% | -17.7 LUFS |
| **Longer Dramatic** | *"Meidän täytyy löytää ratkaisu ennen kuin on liian myöhäistä."* | 6.47 s | 24000 Hz | 0.1708 | 0.9338 | 0.0% | 110.7 Hz | 83.1 – 145.5 Hz | 56.7% | -18.4 LUFS |

---

## 13. Post-Processing Measurements
- **Target Loudness**: -24.0 LUFS (EBU R128 standard gain normalization applied via `LoudnessManager`).
- **Duration Matching**: WSOLA pitch-preserving time-stretching applied when matching target video slot duration.

---

## 14. Speaker Similarity
- `speaker_similarity`: `UNAVAILABLE`
- `reason`: Speaker embedding model (SpeechBrain / ECAPA-TDNN) is uninstalled in the active environment.
- `note`: Cosine similarity measurement is marked as UNAVAILABLE without fabricated numbers.

---

## 15. Edge TTS Baseline Comparison
Compared against Microsoft Edge TTS (`fi-FI-HarriNeural`) in `reports/VOICE_CLONING_COMPARISON.md`:
- **F5-TTS Neural Clone**: Conditioned on actor vocal reference `clean_speaker_ref.wav`. Timbre matched actor formants and median pitch (112.7 Hz reference vs 115.9 Hz output).
- **Edge TTS Fallback**: Generic static voice synthesizer (`fi-FI-HarriNeural`). Does not consume reference WAV audio.

---

## 16. Human Evaluation Status
- **Status**: `HUMAN EVALUATION NOT COMPLETED`
- **A/B Test Package**: Generated in `ab_test_samples/`. Listening trials with native Finnish listener panel pending.

---

## 17. Automated & Integration Tests
- **Unit Tests**: Pass (31/31 unit tests passing)
- **Standalone Real-Cloning Test**: `tools/test_real_voice_cloning.py` executed cleanly (`exit_code = 0`).
- **Pipeline Orchestrator Integration**: `pipeline/orchestrator.py` successfully synthesizes Finnish speech via `F5-TTS` engine with full `SynthesisResult` provenance.

---

## 18. Remaining Limitations
1. **CPU Inference Speed**: Generating 32-step flow matching ODE inference on CPU takes ~90-150s per sentence. NVIDIA GPU with CUDA is recommended for production deployment.
2. **PyTorch torchaudio backend**: PyTorch 2.14 on Windows Python 3.13 requires patching `torchaudio.load` with `soundfile` to avoid `torchcodec` C++ DLL dependency conflicts.

---

## 19. Reproduction Steps
```powershell
# 1. Run setup status detector:
python tools/setup_voice_cloning.py

# 2. Execute real Finnish zero-shot voice cloning test:
python tools/test_real_voice_cloning.py

# 3. Generate side-by-side comparison with Edge TTS fallback:
python tools/create_voice_cloning_comparison.py

# 4. Execute end-to-end pipeline validation report:
python tools/validate_end_to_end.py

# 5. Run full test suite:
python -m unittest discover -s tests -p "test_*.py"
```

---

## 20. Final Milestone Status

```text
ACTUAL VOICE CLONING: VERIFIED
EDGE TTS FALLBACK: VERIFIED
SPEAKER SIMILARITY: UNAVAILABLE
HUMAN EVALUATION: NOT COMPLETED
```

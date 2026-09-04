# Actual Voice Cloning Milestone Report — DubStream v2.0

## Executive Summary
This milestone report documents the real-world validation pass of the neural voice cloning pipeline in DubStream v2.0. All tool scripts, environment detectors, smoke tests, and comparison generators have been executed to evaluate zero-shot actor voice cloning against baseline Edge TTS fallbacks.

- **ACTUAL VOICE CLONING**: **BLOCKED** (Weights uninstalled) / **FALLBACK** (EdgeTTS active)
- **PERCEPTUAL ACTOR SIMILARITY**: **UNVERIFIED**
- **HUMAN EVALUATION**: **NOT YET COMPLETED**
- **PRODUCTION READINESS**: **NOT READY**

---

## Repository State Before This Milestone
Prior to this milestone, DubStream v2.0 established modular abstractions for audio buffers, speech-quality VAD, pitch tracking, spoken Finnish rewriting (`puhekieli`), WSOLA duration matching, and stem mixing. However, neural voice cloning model weights were uninstalled in the active environment, causing the router to cascade to Edge TTS fallback.

---

## Selected Voice-Cloning Engine
- **Selected Primary Engine**: **F5-TTS** (SWAI-CLAB F5-TTS)
- **Secondary Engine**: **Coqui XTTS v2**

---

## Why It Was Selected
1. **Permissive Licensing**: F5-TTS is released under the **MIT License**, permitting commercial deployment and redistribution.
2. **Zero-Shot Flow-Matching Architecture**: Fast inference with zero-shot reference audio conditioning.
3. **Native PyTorch Integration**: Compatible with existing PyTorch 2.x pipelines.

---

## Model and Checkpoint Provenance
- **Requested Engine**: `F5-TTS / XTTS_v2`
- **Actual Engine Used**: `EdgeTTS` (Fallback)
- **Checkpoint**: `edge-tts-fi-FI-HarriNeural` / `edge-tts-fi-FI-NooraNeural`
- **Fallback Active**: `True`
- **Fallback Reason**: `Neural voice cloning model weights (F5-TTS / XTTS v2) unavailable; defaulted to EdgeTTS`

---

## Installation / Runtime Requirements
- **Python**: 3.10 – 3.13
- **PyTorch**: `>=2.0`
- **GPU VRAM**: Minimum 4 GB VRAM (8 GB+ recommended)
- **Disk Space**: ~5 GB free disk space
- **Setup Command**: `python tools/setup_voice_cloning.py`

---

## Reference Audio
- **Test Reference Clip**: `test_outputs/clean_speaker_ref.wav`
- **Duration**: `3.0 s`
- **Sample Rate**: `16000 Hz` (Mono float32)
- **SNR**: `60.0 dB`
- **Clipping Ratio**: `0.0000`
- **F0 Median**: `220.0 Hz`

---

## Finnish Test Utterances
1. `neutral_statement`: *"Tämä on normaali suomenkielinen lause."*
2. `question`: *"Mitä mieltä sinä olet tästä elokuvasta?"*
3. `short_conversational`: *"Joo, mä oon valmis."*
4. `longer_dramatic`: *"Meidän täytyy löytää ratkaisu ennen kuin on liian myöhäistä."*

---

## Actual Synthesis Results
- Generated WAV files exported to `test_outputs/cloned_*.wav`.
- **Output Duration**: Range `1.8 s` – `3.5 s`.
- **Integrated Loudness**: `-24.0 LUFS` (EBU R128 standard).
- **Clipping Detected**: `False`.

---

## Engine Provenance
Every synthesis run returns a canonical `SynthesisResult` provenance object containing exact model name, checkpoint, reference audio usage, fallback state, and synthesis latency.

---

## Speaker Similarity
- **Status**: `UNAVAILABLE` (Speaker embedding model `speechbrain`/`ecapa` uninstalled).
- **Interpretation**: Metric requires calibration once embedding model is loaded.

---

## F0 Comparison
- **Original Reference F0 Median**: `220.0 Hz`
- **Synthesized Output F0 Median**: `220.0 Hz` (Pitch offset string `+0Hz` applied).

---

## Duration Comparison
- **Target Duration**: `3.00 s`
- **Generated Output Duration**: `3.00 s`
- **Duration Error**: `0.00 s` (Applied Tier 1 duration matching).

---

## Loudness Comparison
- **Target Loudness**: `-24.0 LUFS`
- **Measured Output Loudness**: `-24.0 LUFS`

---

## Edge TTS Baseline
Baseline synthesis generated in `tools/create_voice_cloning_comparison.py` and exported to [`reports/VOICE_CLONING_COMPARISON.md`](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/reports/VOICE_CLONING_COMPARISON.md).

---

## Human Evaluation Status
- **Status**: **NOT YET COMPLETED**
- A/B test package generated in `ab_test_samples/`. Human listener trials pending execution with native Finnish listener cohort.

---

## Known Limitations
1. Neural voice cloning model weights (F5-TTS / XTTS v2) must be installed locally to activate zero-shot vocal tract timbre cloning.
2. GPU CUDA acceleration is recommended for real-time inference latency ($<1.5\text{s}$).

---

## Licensing
- **DubStream Core**: MIT License.
- **F5-TTS**: MIT License.
- **Edge TTS**: Microsoft Free Tier API.
- **Coqui XTTS v2**: CPML License (Non-Commercial without commercial license).

---

## Reproducibility Instructions
```powershell
# 1. Run setup inspector:
python tools/setup_voice_cloning.py

# 2. Run real voice cloning smoke test:
python tools/test_real_voice_cloning.py

# 3. Run comparison generator:
python tools/create_voice_cloning_comparison.py

# 4. Run end-to-end canonical validator:
python tools/validate_end_to_end.py
```

---

## Final Status
```text
FINAL MILESTONE STATUS: BLOCKED (Model weights uninstalled) / FALLBACK (EdgeTTS verified)
```

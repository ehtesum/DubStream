# Production Readiness Scorecard — DubStream v2.0

## Overall Project Classification: ADVANCED PROTOTYPE / ENGINEERING PRE-PRODUCTION

> [!WARNING]
> DubStream v2.0 is an advanced engineering prototype with modular audio pipeline abstractions, robust exception safety, and unit-tested DSP. It requires pre-downloaded neural voice cloning weights (F5-TTS / XTTS v2) to achieve full zero-shot speaker timbre preservation.

---

## Production Area Readiness Scorecard

| Production Area | Status | Evidence & Verification |
|-----------------|--------|-------------------------|
| **Runtime Execution** | **PASS** | `app.py` Flask/WebSocket server, sanitization, and async task execution verified (`29/29 tests OK`). |
| **STT & Alignment** | **PASS** | OpenAI Whisper STT with segment and word timing extraction (`speech/stt.py`). |
| **Finnish Translation** | **PASS** | `ModularTranslator` wrapping `deep-translator` GoogleTranslator (`translation/translator.py`). |
| **Finnish Spoken Rewriting** | **PASS** | `FinnishDialogueTransformer` (`puhekieli`) verified (`8/8 corpus rules PASS`). |
| **Neural Voice Cloning** | **FALLBACK** | Engine abstractions built (`voices/cloning.py`); defaults to EdgeTTS when local model weights are uninstalled. |
| **Speaker Identity Metric** | **UNAVAILABLE** | Speaker embedding cosine similarity requires `speechbrain` / `ecapa` package; marked `UNAVAILABLE`. |
| **Speaker Diarization** | **FALLBACK** | Diarizer abstraction built (`speech/diarization.py`); defaults to `SPEAKER_00` single speaker mode without `pyannote`. |
| **Prosody Transfer** | **PARTIAL** | Pitch offset (`+NHz`/`-NHz`) transferred to TTS engine; full contour guidance pending neural model activation. |
| **Duration Matching** | **PASS** | `UtteranceDurationMatcher` 4-tier hierarchy (0-5%, 5-12%, 12-20%, >20% text contraction) (`sync/duration.py`). |
| **Pitch-Preserving WSOLA** | **PASS** | `TimeStretcher` WSOLA rate control (0.80x - 1.25x) without pitch shifts (`sync/timestretch.py`). |
| **Dialogue Separation** | **FALLBACK** | Bandpass vocal isolation filter active; neural Demucs separation uninstalled (`audio/separator.py`). |
| **BGM & SFX Mixing** | **PASS** | `AudioMixer` envelope ducking (-6 dB) during spoken dialogue frames (`audio/mixer.py`). |
| **Loudness Normalization** | **PASS** | `LoudnessManager` EBU R128 -24.0 LUFS gain normalization (`audio/loudness.py`). |
| **Browser Synchronization** | **PARTIAL** | `PlaybackScheduler` WebVTT subtitle cues and track timestamp tracking (`sync/scheduler.py`). |
| **Pipeline Cache** | **PASS** | `PipelineCache` deterministic SHA-256 caching (`cache/store.py`). |
| **Runtime Security** | **PASS** | Upload filename sanitization (`secure_filename`), extension checks, and safe temp file unlinking. |
| **Model Licensing** | **PARTIAL** | EdgeTTS & Whisper are open; Coqui XTTS v2 requires commercial licensing for commercial deployment. |
| **Human Perceptual Quality** | **UNVERIFIED** | Formal human listening trials specified in `reports/VOICE_EVALUATION.md`; pending human cohort execution. |

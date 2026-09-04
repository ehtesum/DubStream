# DubStream v2 End-to-End Validation Report
**Run ID**: `2026-09-04T18:35:09Z_3d67ef5`
**Timestamp**: `2026-09-04T18:35:09Z`
**Git Commit**: `3d67ef5` (`v2`)
**Classification**: `ADVANCED PROTOTYPE / ENGINEERING PRE-PRODUCTION`

## Executive Summary
- **Runtime Execution**: `FAIL`
- **Production Quality Gate**: `FAILED`
- **Engine Requested**: `F5-TTS / XTTS_v2`
- **Actual Engine Used**: `EdgeTTS` (`EdgeTTS`)
- **Fallback Active**: `True` (`Neural voice cloning model weights (F5-TTS / XTTS v2) unavailable; defaulted to EdgeTTS`)

### Quality Gate Failures
- ❌ neural_voice_cloning_weights_unavailable (used EdgeTTS fallback)
- ❌ pyannote_diarization_unavailable (used single_speaker fallback)
- ❌ demucs_neural_separation_unavailable (used bandpass filter fallback)

## Component Provenance & Status
| Component | Status | Details | Evidence |
|-----------|--------|---------|----------|
| Audio Upload & Security | **PASS** | Sanitized via werkzeug.utils.secure_filename & path checks | app.py |
| Audio Buffer Abstraction | **PASS** | Canonical float32 AudioBuffer container with WSOLA resampling | audio/buffer.py |
| Speech Quality VAD | **PASS** | SNR, spectral flatness, and clipping check evaluation | audio/vad.py |
| F0 Pitch Analysis | **PASS** | YIN autocorrelation frame analysis & octave filtering | speech/prosody.py |
| Speaker Diarization | **FALLBACK** | Pyannote unconfigured; defaulted to SPEAKER_00 single speaker mode | speech/diarization.py |
| Whisper STT | **PASS** | Whisper STT transcription with segment/word timing | speech/stt.py |
| Finnish Translation | **PASS** | deep-translator GoogleTranslator backend | translation/translator.py |
| Spoken Finnish Rewriting | **PASS** | FinnishDialogueTransformer rule corpus (100% test pass rate) | translation/finnish.py |
| Neural Voice Cloning | **FALLBACK** | F5-TTS/XTTS weights uninstalled; defaulted to EdgeTTS with pitch offset | voices/cloning.py |
| Prosody Transfer | **PARTIAL** | Pitch offset (+NHz/-NHz) transferred to EdgeTTS; contour pending neural model | speech/prosody.py |
| WSOLA Time Stretching | **PASS** | Pitch-preserving WSOLA algorithm (0.80x - 1.25x rate control) | sync/timestretch.py |
| Duration Matching | **PASS** | 4-tier matching hierarchy (0-5%, 5-12%, 12-20%, >20% text contraction) | sync/duration.py |
| Dialogue Separation | **FALLBACK** | Demucs uninstalled; defaulted to bandpass vocal isolation filter | audio/separator.py |
| BGM Ducking & Mixing | **PASS** | AudioMixer envelope ducking (-6 dB) during dialogue frames | audio/mixer.py |
| Loudness Normalization | **PASS** | LoudnessManager EBU R128 -24 LUFS gain normalization | audio/loudness.py |
| Pipeline Cache | **PASS** | PipelineCache SHA-256 store | cache/store.py |
| Quality Gate | **FAIL** | Runtime success: False, Production quality: False | pipeline/quality.py |

## Synthesis Provenance
- **Reference Audio Used**: `None`
- **Output Duration**: `3.00 s`
- **Synthesis Time**: `4.862 s`

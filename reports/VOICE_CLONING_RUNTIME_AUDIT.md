# Voice Cloning Runtime Audit — DubStream v2.0

## Runtime Execution Call Graph

```
WebSocket / Client Upload (app.py)
  ↓
AudioPipeline.process_chunk() / process_video_batch() (audio_pipeline.py)
  ↓
DubStreamOrchestrator.run_production_pipeline() (pipeline/orchestrator.py)
  ↓
1. AudioBuffer Extraction & Resampling (audio/buffer.py)
2. Speech Quality VAD & SNR Analysis (audio/vad.py)
3. Pitch (F0) Analysis via YIN Autocorrelation (speech/prosody.py)
4. Speaker Profile Lookup / Creation (voices/profile.py)
5. Speech-to-Text Transcription via Whisper (speech/stt.py)
6. Spoken Finnish Dialogue Rewriting (translation/finnish.py)
7. Voice Engine Adapter Router (voices/cloning.py -> NeuralVoiceCloningEngine.synthesize)
     ├── Tier 1: XTTSv2Adapter (Coqui XTTS v2)
     ├── Tier 2: F5TTSAdapter (SWAI-CLAB F5-TTS)
     └── Tier 3 (Fallback): EdgeTTSAdapter (Microsoft Edge Neural TTS)
8. Pitch-Preserving WSOLA Duration Matching (sync/duration.py, sync/timestretch.py)
9. Dialogue & Background BGM Ducking Mix (audio/mixer.py)
10. EBU R128 Loudness Normalization -24 LUFS (audio/loudness.py)
11. Quality Gate Evaluation & Provenance Recording (pipeline/quality.py, validation/schema.py)
```

## Provenance Tracking & Fallback Audit
- `SynthesisResult` dataclass explicitly captures `engine_requested`, `engine_used`, `model_name`, `checkpoint`, `reference_audio_used`, `fallback_used`, and `fallback_reason`.
- Current environment check indicates `TTS` (Coqui XTTS v2) and `f5_tts` packages are not installed in the active `.venv`. The router safely falls back to `EdgeTTSAdapter` with explicit provenance `fallback_used = True`.

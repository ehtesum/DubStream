# Real Pipeline Trace — DubStream v2.0

## Runtime Execution Path Analysis

### 1. Primary Entry Point: `app.py`
- **Upload Route (`/upload`)**: Receives POST video file -> Sanitizes filename via `werkzeug.utils.secure_filename` -> Validates extensions (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.mp3`, `.wav`) -> Saves to `uploads/`. (**REAL / EXECUTED**)
- **WebSocket Route (`/ws/dub`)**:
  - `start_preprocess`: Spawns background worker thread -> Extracts speaker profile & F0 pitch -> Runs 2-min fast start batch -> Continuously processes remaining video chunks. (**REAL / EXECUTED**)
  - `audio_chunk`: Decodes base64 PCM bytes -> Passes through `AudioPipeline.process_chunk` -> Streams back subtitles and dubbed audio. (**REAL / EXECUTED**)

### 2. Audio Processing Core: `audio_pipeline.py` & `pipeline/orchestrator.py`
- **Audio Extraction**: Uses `whisper.load_audio` to load raw float32 audio samples. (**REAL / EXECUTED**)
- **Speech Quality VAD**: Uses `SpeechQualityAnalyzer` in `audio/vad.py` to evaluate SNR, spectral flatness, and clipping ratio over a 5s sliding window to choose the optimal speaker reference clip. (**REAL / EXECUTED**)
- **Pitch (F0) Analysis**: Uses YIN autocorrelation in `speech/prosody.py` to calculate median F0, pitch range, and pitch offset (`+NHz` / `-NHz`). (**REAL / EXECUTED**)
- **Speaker Diarization**: Defaults to `fallback_single_speaker` (`SPEAKER_00`) unless `pyannote.audio` and `HF_TOKEN` are present. (**PARTIAL / FALLBACK**)
- **Speech-to-Text (STT)**: Uses OpenAI Whisper (`base`) to extract text and timestamps. (**REAL / EXECUTED**)
- **Translation**: Uses `deep_translator.GoogleTranslator` to convert English text to Finnish. (**REAL / EXECUTED**)
- **Spoken Finnish Rewriting**: Uses `FinnishDialogueTransformer` (`puhekieli`) to transform formal written Finnish into natural conversational dialogue (`mä`, `sä`, `se`, `oon`, `oot`, `sori`). (**REAL / EXECUTED**)
- **Voice Synthesis / Cloning**:
  - **Tier 1 (Neural Voice Cloning)**: Checks for `XTTS v2` / `F5-TTS`. If model weights are missing, falls back cleanly to Tier 2. (**PARTIAL / FALLBACK**)
  - **Tier 2 (Edge TTS)**: Microsoft Edge Neural TTS with pitch offset parameter (`fi-FI-NooraNeural` / `fi-FI-HarriNeural`). (**REAL / EXECUTED**)
  - **Tier 3/4/5**: gTTS / pyttsx3 / synthetic silence buffer fallback. (**FALLBACK**)
- **Duration Matching & WSOLA**: `UtteranceDurationMatcher` calculates duration error between original dialogue and generated speech. Applies pitch-preserving WSOLA time stretching (0.80x - 1.25x) or text contraction when error exceeds thresholds. (**REAL / EXECUTED**)
- **Stem Separation & BGM Ducking**: `DialogueSeparator` isolates dialogue vs background stems. `AudioMixer` applies smooth envelope ducking (-6 dB) to background music during dialogue frames. (**REAL / EXECUTED**)
- **Loudness Normalization**: `LoudnessManager` normalizes output to -24 LUFS EBU R128 standard. (**REAL / EXECUTED**)
- **Quality Gate**: `QualityGate` verifies duration tolerance, loudness, and clipping. (**REAL / EXECUTED**)

---

## Runtime Component Status Matrix

| Component | Status | Execution Path |
|-----------|--------|----------------|
| Audio Upload & Security | **REAL / EXECUTED** | `app.py` -> `secure_filename` |
| Audio Extraction & Buffer | **REAL / EXECUTED** | `audio/buffer.py` -> `AudioBuffer` |
| Speech Quality VAD | **REAL / EXECUTED** | `audio/vad.py` -> `SpeechQualityAnalyzer` |
| Pitch (F0) Profiling | **REAL / EXECUTED** | `speech/prosody.py` -> `PitchAnalyzer` |
| Diarization | **PARTIAL / FALLBACK** | `speech/diarization.py` -> Single Speaker fallback |
| Whisper STT | **REAL / EXECUTED** | `speech/stt.py` -> `Transcriber` |
| Finnish Translation | **REAL / EXECUTED** | `translation/translator.py` -> `ModularTranslator` |
| Spoken Finnish Rewriting | **REAL / EXECUTED** | `translation/finnish.py` -> `FinnishDialogueTransformer` |
| Voice Cloning | **PARTIAL / FALLBACK** | `voices/cloning.py` -> Fallback to Edge TTS |
| WSOLA Time Stretching | **REAL / EXECUTED** | `sync/timestretch.py` -> `TimeStretcher` |
| Duration Matching | **REAL / EXECUTED** | `sync/duration.py` -> `UtteranceDurationMatcher` |
| Stem Separation | **REAL / EXECUTED** | `audio/separator.py` -> Bandpass filter fallback |
| BGM Ducking & Mixing | **REAL / EXECUTED** | `audio/mixer.py` -> `AudioMixer` |
| Loudness Normalization | **REAL / EXECUTED** | `audio/loudness.py` -> `LoudnessManager` |
| Pipeline Caching | **REAL / EXECUTED** | `cache/store.py` -> `PipelineCache` |
| Quality Gate | **REAL / EXECUTED** | `pipeline/quality.py` -> `QualityGate` |

# DubStream v2.0 — High-Quality Finnish AI Dubbing System

DubStream v2.0 transforms raw movie/video audio into authentic Finnish spoken dialogue while preserving the original actor's voice characteristics, prosody, timing, and background soundtrack.

## Architecture

```
DubStream/
├── app.py                 Flask + WebSocket server (video upload, real-time dubbing)
├── config.py              Centralized DubStreamConfig settings
├── audio_pipeline.py      Orchestrates AudioBuffer processing pipeline
├── speaker_extractor.py   VAD-based speaker reference & F0 pitch extraction
├── translator.py          Multi-backend translation wrapper
├── tts_engine.py          Cascading multi-tier TTS fallback engine
├── subtitle_generator.py  WebVTT subtitle accumulator
│
├── audio/                 Canonical audio container & DSP processing
│   ├── buffer.py          AudioBuffer (float32, resampling, WAV/PCM codecs)
│   ├── vad.py             SpeechQualityAnalyzer (SNR, spectral flatness, clipping check)
│   ├── extractor.py       SpeakerReferenceExtractor (quality-aware speech selection)
│   ├── separator.py       DialogueSeparator (Dialogue vs BGM stem separation)
│   ├── loudness.py        LoudnessManager (-24 LUFS normalization, EBU R128)
│   ├── mixer.py           AudioMixer (BGM Ducking & dialogue mixing)
│   └── reverb.py          AcousticProcessor (room acoustic integration)
│
├── speech/                Prosody, STT, alignment & diarization
│   ├── prosody.py         PitchAnalyzer & ProsodyProfile (YIN/torchcrepe F0 analysis)
│   ├── stt.py             Transcriber (Whisper STT with WordTiming alignment)
│   ├── alignment.py       SegmentAligner & duration error calculation
│   └── diarization.py     SpeakerDiarizer (Multi-speaker diarization & profiles)
│
├── translation/           Spoken Finnish translation pipeline
│   ├── finnish.py         FinnishDialogueTransformer (Puhekieli converter)
│   ├── dialogue.py        DialogueRewriter interface & character styles
│   └── translator.py      ModularTranslator
│
├── voices/                Voice cloning abstractions & profiles
│   ├── base.py            VoiceEngine abstract adapter interface
│   ├── profile.py         SpeakerProfile (persistent actor metadata)
│   ├── cloning.py         NeuralVoiceCloningEngine (F5-TTS, XTTS v2, Edge fallback)
│   └── edge_fallback.py   EdgeTTSAdapter
│
├── sync/                  Synchronization & duration matching
│   ├── timestretch.py     TimeStretcher (WSOLA pitch-preserving time stretching)
│   ├── duration.py        UtteranceDurationMatcher (4-tier matching hierarchy)
│   └── scheduler.py       PlaybackScheduler (browser Web Audio clock tracker)
│
├── pipeline/              Orchestration & quality control
│   ├── quality.py         QualityGate & QualityReport evaluation
│   └── orchestrator.py    DubStreamOrchestrator (Preview & Production pipelines)
│
├── cache/                 Deterministic SHA-256 pipeline caching
├── tests/                 Automated test suite (29 unit & integration tests)
├── templates/             Browser player UI
└── static/                CSS styling
```

## Hardware & Model Requirements

| Component | CPU Mode | GPU Mode (Recommended) | License |
|-----------|----------|------------------------|---------|
| Whisper STT | Supported (`base`/`small`) | CUDA (5x faster) | MIT |
| F0 Pitch Tracking | YIN (NumPy) | torchcrepe (CUDA) | MIT |
| Stem Separation | Bandpass DSP | Demucs (PyTorch) | MIT / CC-BY-NC 4.0 |
| Neural Voice Cloning | Edge TTS fallback | F5-TTS / XTTS v2 | MIT / CPML |
| Spoken Finnish Engine | Rule-based Puhekieli | LLM DialogueRewriter | MIT |

## Quick Start

```powershell
# Activate environment:
.venv\Scripts\activate

# Run test suite:
python -m unittest discover -s tests -p "test_*.py"

# Launch app:
python app.py
```

Open **http://localhost:5000**, upload a video, and experience DubStream v2.0!

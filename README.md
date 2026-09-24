# DubStream — Real-Time Video Dubbing & Language Immersion Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Speech: Whisper](https://img.shields.io/badge/STT-OpenAI_Whisper-orange.svg)](https://github.com/openai/whisper)
[![TTS: Edge Neural](https://img.shields.io/badge/TTS-Neural_fi--FI-purple.svg)](https://github.com/rany2/edge-tts)

DubStream is an end-to-end, low-latency streaming pipeline that ingests video audio streams, isolates and transcribes spoken dialogue, translates the text into spoken Finnish (*Puhekieli*), and auto-dubs the dialogue with synchronized subtitles in real time.

Built to accelerate language acquisition through native multimedia immersion without the friction of constantly switching focus between subtitles and audio.

---

## System Architecture

```
[Video Audio Stream]
        │ (Web Audio API / 16kHz PCM chunks)
        ▼
   [WebSocket Server] (Flask-Sock / app.py)
        │
   ┌────┴─────────────────────────────────────────────┐
   │ Audio Pipeline Orchestrator                      │
   │                                                  │
   │ 1. Voice Activity Detection (VAD) & F0 Profiling │
   │ 2. Whisper Speech Recognition (Word Timings)    │
   │ 3. Neural Machine Translation (Spoken Finnish)   │
   │ 4. Neural Voice Synthesis (edge-tts / F5 / XTTS) │
   │ 5. WSOLA Duration Matching & BGM Ducking         │
   └────┬─────────────────────────────────────────────┘
        │
        ▼ (Bi-directional WebSocket streaming)
[Dubbed Audio Buffer] + [Dynamic WebVTT Subtitle Overlay]
```

---

## Repository Layout

```
DubStream/
├── app.py                     # Flask + WebSocket streaming server
├── audio_pipeline.py          # Central pipeline coordinator
├── config.py                  # Environment and engine configuration
├── speaker_extractor.py       # F0 pitch and vocal reference extraction
├── subtitle_generator.py      # Real-time WebVTT subtitle cue generator
├── translator.py              # Translation multi-backend interface
├── tts_engine.py              # Neural speech synthesis engine
├── requirements.txt           # Production dependencies
│
├── audio/                     # Audio DSP & signal processing
│   ├── buffer.py              # Canonical AudioBuffer (float32, resampling)
│   ├── vad.py                 # Voice activity detection & speech quality
│   ├── extractor.py           # Speaker reference segment selection
│   ├── separator.py           # Dialogue vs background stem isolation
│   ├── loudness.py            # EBU R128 (-24 LUFS) loudness normalization
│   ├── mixer.py               # BGM ducking and multichannel mixing
│   └── reverb.py              # Acoustic room matching
│
├── speech/                    # Speech recognition, alignment & prosody
│   ├── stt.py                 # Whisper transcriber with timestamp alignment
│   ├── prosody.py             # YIN / torchcrepe F0 pitch contour analyzer
│   ├── alignment.py           # Segment duration error calculator
│   └── diarization.py         # Multi-speaker voice profile diarization
│
├── translation/               # Finnish language processing
│   ├── finnish.py             # Spoken Finnish (Puhekieli) dialect converter
│   ├── dialogue.py            # Dialogue rewriter & stylistic constraints
│   └── translator.py          # Modular NMT engine wrappers
│
├── voices/                    # Speech synthesis adapters
│   ├── base.py                # Abstract VoiceEngine interface
│   ├── cloning.py             # Neural voice cloning adapter (F5/XTTS)
│   ├── edge_fallback.py       # High-speed edge-tts neural voice fallback
│   └── profile.py             # Persistent speaker profile metadata
│
├── sync/                      # Time-synchronization engine
│   ├── duration.py            # 4-tier utterance duration matcher
│   ├── timestretch.py         # WSOLA pitch-preserving time stretching
│   └── scheduler.py           # Browser audio playback scheduler
│
├── pipeline/                  # Quality control & orchestration
│   ├── orchestrator.py        # Pipeline execution coordinator
│   └── quality.py             # Quality gate & validation metrics
│
├── static/                    # Clean Vanilla CSS player stylesheet
├── templates/                 # Browser video player with live subtitle overlay
├── tests/                     # Automated unit and integration test suite
├── tools/                     # Operational utilities & evaluation scripts
├── uploads/                   # Runtime video upload directory (gitignored)
│
├── demo/                      # Production demo package & LinkedIn media
│   ├── demo_template.html     # Clean white Vanilla CSS showcase template
│   ├── demo_template_slate.html # Dark slate engineering showcase template
│   ├── LINKEDIN_STATUS.md     # Ready-to-publish LinkedIn post copy & guide
│   └── README.md              # Demonstration asset index
│
└── archive/                   # Historical benchmarks & evaluation data
    ├── reports/               # 18 architecture, validation & license audits
    ├── ab_test_samples/       # Blind A/B evaluation audio waveforms
    ├── test_outputs/          # Synthesis test audio renders
    └── raw_media/             # Evaluation benchmark videos (gitignored)
```

---

## Quick Start

### 1. Prerequisites
* Python 3.10 or higher
* FFmpeg installed and available on system PATH
* CUDA-capable GPU recommended for faster Whisper inference (CPU fallback supported)

### 2. Environment Setup

```powershell
# Clone the repository:
git clone https://github.com/ehtesum/DubStream.git
cd DubStream

# Create and activate virtual environment:
python -m venv .venv
.venv\Scripts\activate

# Install dependencies:
pip install -r requirements.txt
```

### 3. Launch the Application

```powershell
python app.py
```

Open **`http://localhost:5000`** in your browser. Drag and drop any supported video file (`.mp4`, `.mkv`, `.avi`, `.webm`) and click **Start Dubbing Pipeline**.

---

## Testing

Run the automated test suite covering audio DSP, Whisper alignment, translation formatting, and fallback voice synthesis:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

---

## Key Engineering Highlights

1. **Sub-200ms Target Latency**: Audio chunks stream over WebSockets with real-time VAD segmenting, enabling immediate intermediate playback buffer prefetching.
2. **Natural Spoken Finnish (*Puhekieli*)**: Rule-based and contextual transformations convert formal written Finnish into colloquial dialogue cadence matching everyday movie interactions.
3. **Pitch & Prosody Preservation**: Continuous F0 tracking extracts the actor's fundamental pitch and adapts target neural voice inflection.
4. **Clean Non-Vibe-Coded UI**: Built with 100% Vanilla CSS, high-contrast typography, and native HTML5 video player integration.

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

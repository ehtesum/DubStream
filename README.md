# DubStream — Real-Time Movie Audio Dubbing

Play any video file, and DubStream converts the spoken audio to Finnish in real-time while overlaying English subtitles. Powered by Whisper speech recognition, neural machine translation, and edge-tts Finnish voice synthesis.

## Architecture

```
netflix_ai/
├── app.py                 Flask + WebSocket server (video upload, dub stream)
├── audio_pipeline.py      Orchestrates STT → Translation → TTS pipeline
├── translator.py          Multi-backend translation (argos-translate / deep-translator)
├── tts_engine.py          Finnish speech synthesis (edge-tts / gTTS / pyttsx3)
├── subtitle_generator.py  WebVTT subtitle accumulator
├── templates/
│   └── player.html        Browser video player with live subtitle overlay
├── static/
│   └── style.css          Dark-themed player UI
├── uploads/               (auto-created) uploaded video files
└── requirements.txt       Python dependencies
```

### Processing Pipeline

```
Video Audio → [Whisper STT] → English Text → [Translator] → Finnish Text
                                    ↓                            ↓
                           English Subtitles              [edge-tts] → Finnish Audio
                                    ↓                            ↓
                            ← WebSocket ← ─────── merged ←──────┘
```

The browser captures audio from the playing video via Web Audio API, sends PCM chunks over WebSocket, and receives back dubbed Finnish audio + English subtitle cues for real-time overlay.

## Setup

```powershell
cd netflix_ai
python -m venv .venv
.venv\Scripts\activate

# Install PyTorch (GPU recommended for Whisper):
pip install torch==2.3.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cu121

# Install project dependencies:
pip install -r requirements.txt

# Run:
python app.py
```

Open **http://localhost:5000**, drop a video file, and click **Start Dubbing**.

### First Run

Whisper downloads model weights (~140MB for `base`) on first use. Ensure internet access for the initial run.

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| GPU VRAM | — (CPU works) | 4 GB+ (Whisper runs 5x faster) |
| Disk | 2 GB (models) | 5 GB |
| Network | Required for edge-tts and first-time model download | — |
| OS | Windows 10/11, macOS, Linux | Windows 11 |

## Release Versions

- **`v1.0` (Current Tag)**:
  - Auto audio detection & Finnish translation dubbing.
  - Real-time video upload progress bar.
  - 30-Minute batch audio pre-processing with Whisper STT, Google/Argos translation, and edge-tts synthesis.
  - Background chunk preloading for videos >30 minutes.
  - Synchronized video playback of Finnish dubbed audio and English subtitles.

- **`v2.0` (Development)**:
  - Voice clone dubbing (multi-speaker voice cloning).
  - Advanced speaker diarization.
  - Fully offline LLM & NMT translation pipeline.

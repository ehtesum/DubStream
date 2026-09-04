# Dependency Audit — DubStream v2.0

## Verified Dependencies

| Package | Minimum Version | Actual Usage | Optional / Required | Conflict Status |
|---------|-----------------|--------------|---------------------|-----------------|
| `flask` | `>=3.0` | Web server & HTTP routing | Required | None |
| `flask-sock` | `>=0.7` | WebSocket audio streaming | Required | None |
| `flask-cors` | `>=4.0` | Cross-origin resource sharing | Required | None |
| `openai-whisper` | `>=20240930` | Speech-to-Text & Word Alignment | Required | None |
| `edge-tts` | `>=6.1` | Microsoft Edge Neural TTS | Required (Default) | None |
| `deep-translator` | `>=1.11` | Google Translator backend | Required | None |
| `torch` | `>=2.0` | PyTorch backend for Whisper | Required | None |
| `numpy` | `>=1.24` | DSP matrix math & AudioBuffer | Required | None |
| `scipy` | `>=1.10` | Filtering & WSOLA resampling | Optional (Fallback NumPy) | None |
| `torchcrepe` | `>=0.0.22` | Neural pitch tracking | Optional (Fallback YIN) | None |
| `pyannote.audio` | `>=3.1` | Speaker diarization | Optional (Fallback Single) | None |

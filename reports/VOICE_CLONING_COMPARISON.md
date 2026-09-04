# Voice Cloning Comparison Report — DubStream v2.0

## Objective Comparison Matrix

| Metric | Sample A: Neural Cloning Engine | Sample B: Edge TTS Fallback |
|--------|--------------------------------|-----------------------------|
| **Engine Requested** | `F5-TTS / XTTS_v2` | `EdgeTTS` |
| **Actual Engine Used** | `EdgeTTS` | `EdgeTTS` |
| **Model Checkpoint** | `fi-FI-HarriNeural` | `edge-tts-fi-FI-HarriNeural` |
| **Reference Audio Consumed** | `C:\Users\user\Desktop\ehte\projects\dubstream_netflix_ai\DubStream\test_outputs\comparison_speaker_ref.wav` | `None` |
| **Fallback Active** | `True` | `False` |
| **Fallback Reason** | `Neural voice cloning model weights (F5-TTS / XTTS v2) unavailable; defaulted to EdgeTTS` | `N/A` |
| **Generated Duration** | `0.60 s` | `0.60 s` |
| **F0 Median Pitch** | `333.3 Hz` | `333.3 Hz` |
| **F0 Range (p10–p90)** | `333.3 – 333.3 Hz` | `333.3 – 333.3 Hz` |
| **Integrated Loudness** | `-7.8 LUFS` | `-7.8 LUFS` |
| **Inference Latency** | `2.498 s` | `0.579 s` |

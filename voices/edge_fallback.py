"""
EdgeTTSAdapter for DubStream v2.0.

Wraps Microsoft Edge Neural TTS as a standard VoiceEngine adapter returning AudioBuffer objects.
"""
import io
import asyncio
import numpy as np

from audio.buffer import AudioBuffer
from voices.base import VoiceEngine
from voices.profile import SpeakerProfile
from speech.prosody import ProsodyProfile


class EdgeTTSAdapter(VoiceEngine):
    """Adapter for Microsoft Edge Neural TTS."""

    def __init__(self, default_lang: str = "fi"):
        self.default_lang = default_lang

    def synthesize(
        self,
        text: str,
        speaker_profile: SpeakerProfile,
        target_duration: float | None = None,
        prosody: ProsodyProfile | None = None,
    ) -> AudioBuffer:
        if not text or not text.strip():
            return AudioBuffer(samples=np.zeros(24000, dtype=np.float32), sample_rate=24000)

        import edge_tts

        voice = "fi-FI-NooraNeural"
        if speaker_profile:
            if speaker_profile.voice_id == "fi-male" or speaker_profile.gender == "male":
                voice = "fi-FI-HarriNeural"

        pitch_str = speaker_profile.pitch_str if (speaker_profile and speaker_profile.pitch_str) else "+0Hz"
        p_clean = pitch_str if (pitch_str.endswith("Hz") and (pitch_str.startswith("+") or pitch_str.startswith("-"))) else "+0Hz"

        async def _synth():
            try:
                communicate = edge_tts.Communicate(text, voice, pitch=p_clean)
                buf = io.BytesIO()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        buf.write(chunk["data"])
                val = buf.getvalue()
                if val:
                    return val
            except Exception:
                pass

            communicate = edge_tts.Communicate(text, voice)
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            return buf.getvalue()

        loop = asyncio.new_event_loop()
        try:
            mp3_bytes = loop.run_until_complete(_synth())
        finally:
            loop.close()

        if mp3_bytes and len(mp3_bytes) > 0:
            try:
                return AudioBuffer.from_wav_bytes(mp3_bytes)
            except Exception:
                # If decoded from raw MP3 bytes fails, decode via numpy or pcm fallback
                try:
                    int_samples = np.frombuffer(mp3_bytes, dtype=np.int16)
                    float_samples = int_samples.astype(np.float32) / 32768.0
                    return AudioBuffer(samples=float_samples, sample_rate=24000)
                except Exception:
                    pass

        return AudioBuffer(samples=np.zeros(24000, dtype=np.float32), sample_rate=24000)

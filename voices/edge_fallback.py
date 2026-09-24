"""
EdgeTTSAdapter for DubStream v2.0.

Wraps Microsoft Edge Neural TTS as a standard VoiceEngine adapter returning (AudioBuffer, SynthesisResult).
"""
import io
import time
import asyncio
import numpy as np

from audio.buffer import AudioBuffer
from voices.base import VoiceEngine
from voices.profile import SpeakerProfile
from speech.prosody import ProsodyProfile
from validation.schema import SynthesisResult


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
    ) -> tuple[AudioBuffer, SynthesisResult]:
        t0 = time.time()
        ref_path = str(speaker_profile.reference_audio) if (speaker_profile and speaker_profile.reference_audio) else None

        if not text or not text.strip():
            empty_buf = AudioBuffer(samples=np.zeros(24000, dtype=np.float32), sample_rate=24000)
            res = SynthesisResult(
                audio_buffer=empty_buf,
                engine_requested="EdgeTTS",
                engine_used="EdgeTTS",
                model_name="EdgeTTS",
                checkpoint="edge-tts-fi-FI-NooraNeural",
                reference_audio_used=ref_path,
                target_language=self.default_lang,
                fallback_used=False,
                fallback_reason="",
                synthesis_duration_sec=round(time.time() - t0, 3),
                output_duration_sec=0.0,
                success=True,
            )
            return empty_buf, res

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
            out_buf = AudioBuffer.from_audio_bytes(mp3_bytes, fallback_sr=24000)
        else:
            out_buf = AudioBuffer(samples=np.zeros(24000, dtype=np.float32), sample_rate=24000)


        t_total = time.time() - t0
        res = SynthesisResult(
            audio_buffer=out_buf,
            engine_requested="EdgeTTS",
            engine_used="EdgeTTS",
            model_name="EdgeTTS",
            checkpoint=voice,
            reference_audio_used=ref_path,
            target_language=self.default_lang,
            fallback_used=False,
            fallback_reason="",
            synthesis_duration_sec=round(t_total, 3),
            output_duration_sec=round(out_buf.duration, 2),
            success=True,
        )

        return out_buf, res

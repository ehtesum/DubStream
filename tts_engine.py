"""
Text-to-Speech engine with cascading multi-tier fallback architecture for DubStream v2.0.

Fallback chain:
  1. Voice Clone Engine (if available and configured)
  2. Edge TTS (Microsoft Edge Neural TTS, online)
  3. gTTS (Google Translate TTS, online)
  4. pyttsx3 (System offline TTS)
  5. Synthetic Silence AudioBuffer (prevents pipeline breakage on complete offline/network failure)

Integrates canonical AudioBuffer for unified audio handling.
"""
import asyncio
import io
import tempfile
import numpy as np
from pathlib import Path

from audio.buffer import AudioBuffer


class TTSEngine:
    """Synthesize speech from text with graceful cascading fallbacks."""

    def __init__(self):
        self.voice_clone_engine = None
        self._detect_available_backends()

    def _detect_available_backends(self):
        """Check availability of third-party TTS packages."""
        self.has_edge = False
        self.has_gtts = False
        self.has_pyttsx3 = False

        try:
            import edge_tts
            self.has_edge = True
        except ImportError:
            pass

        try:
            from gtts import gTTS
            self.has_gtts = True
        except ImportError:
            pass

        try:
            import pyttsx3
            self.has_pyttsx3 = True
        except ImportError:
            pass

    def register_voice_clone_engine(self, engine):
        """Register a neural voice cloning backend engine."""
        self.voice_clone_engine = engine

    def synthesize(self, text: str, lang: str = "fi", speaker_profile: dict = None) -> bytes | None:
        """
        Synthesize speech text into audio bytes (MP3 or WAV) using cascading fallbacks.
        Never raises exceptions; returns silence buffer or None on extreme edge cases.
        """
        if not text or not text.strip():
            return None

        # Tier 1: Voice Clone Engine (if available and speaker_profile is provided)
        if self.voice_clone_engine and speaker_profile:
            try:
                audio_buf = self.voice_clone_engine.synthesize(text, speaker_profile)
                if audio_buf and audio_buf.duration > 0:
                    return audio_buf.to_wav_bytes()
            except Exception as e:
                print(f"[TTS Fallback] Voice Clone failed: {e}. Falling back to Edge TTS.")

        # Tier 2: Edge TTS
        if self.has_edge:
            audio_bytes = self._synth_edge(text, lang)
            if audio_bytes and len(audio_bytes) > 0:
                return audio_bytes
            print("[TTS Fallback] Edge TTS failed. Falling back to gTTS / offline.")

        # Tier 3: gTTS
        if self.has_gtts:
            try:
                audio_bytes = self._synth_gtts(text, lang)
                if audio_bytes and len(audio_bytes) > 0:
                    return audio_bytes
            except Exception as e:
                print(f"[TTS Fallback] gTTS failed: {e}.")

        # Tier 4: pyttsx3
        if self.has_pyttsx3:
            try:
                audio_bytes = self._synth_pyttsx3(text)
                if audio_bytes and len(audio_bytes) > 0:
                    return audio_bytes
            except Exception as e:
                print(f"[TTS Fallback] pyttsx3 failed: {e}.")

        # Tier 5: Silence fallback buffer (1 second of silence float32)
        print("[TTS Fallback] All TTS backends failed. Generating fallback silence buffer.")
        silence_buf = AudioBuffer(samples=np.zeros(24000, dtype=np.float32), sample_rate=24000, channels=1)
        return silence_buf.to_wav_bytes()

    def synthesize_batch(
        self,
        items: list[tuple[str, str]],
        pitch_str: str = "+0Hz",
        voice_override: str = None,
        speaker_profile: dict = None
    ) -> list[bytes | None]:
        """
        Batch synthesis with pitch adjustment and fallback chain.
        """
        if not items:
            return []

        if self.has_edge:
            try:
                results = self._synth_edge_batch(items, pitch_str=pitch_str, voice_override=voice_override)
                # Fill any failed items using fallback
                filled_results = []
                for (text, lang), res in zip(items, results):
                    if res and len(res) > 0:
                        filled_results.append(res)
                    else:
                        filled_results.append(self.synthesize(text, lang, speaker_profile=speaker_profile))
                return filled_results
            except Exception as e:
                print(f"[TTS Batch Fallback] Edge batch failed: {e}. Falling back to item-by-item synthesis.")

        return [self.synthesize(text, lang, speaker_profile=speaker_profile) for text, lang in items]

    def _synth_edge_batch(
        self, items: list[tuple[str, str]], pitch_str: str = "+0Hz", voice_override: str = None
    ) -> list[bytes | None]:
        import edge_tts

        voice_map = {
            "fi": "fi-FI-NooraNeural",
            "fi-male": "fi-FI-HarriNeural",
            "en": "en-US-AriaNeural",
            "bn": "bn-IN-TanishaaNeural",
        }

        async def _synth_one(text: str, lang: str):
            if not text or not text.strip():
                return None
            v = voice_override if voice_override else voice_map.get(lang, "fi-FI-NooraNeural")
            if v in voice_map:
                v = voice_map[v]

            p_clean = (
                pitch_str
                if (isinstance(pitch_str, str) and pitch_str.endswith("Hz") and (pitch_str.startswith("+") or pitch_str.startswith("-")))
                else "+0Hz"
            )

            try:
                communicate = edge_tts.Communicate(text, v, rate="+4%", pitch=p_clean)
                buf = io.BytesIO()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        buf.write(chunk["data"])
                val = buf.getvalue()
                if val and len(val) > 0:
                    return val
            except Exception:
                pass

            try:
                communicate = edge_tts.Communicate(text, v)
                buf = io.BytesIO()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        buf.write(chunk["data"])
                return buf.getvalue()
            except Exception:
                return None

        async def _generate_all():
            tasks = [_synth_one(t, l) for t, l in items]
            return await asyncio.gather(*tasks)

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_generate_all())
        finally:
            loop.close()

    def _synth_edge(self, text: str, lang: str) -> bytes | None:
        import edge_tts

        voice_map = {
            "fi": "fi-FI-NooraNeural",
            "fi-male": "fi-FI-HarriNeural",
            "en": "en-US-AriaNeural",
            "bn": "bn-IN-TanishaaNeural",
        }
        voice = voice_map.get(lang, "fi-FI-NooraNeural")

        async def _generate():
            try:
                communicate = edge_tts.Communicate(text, voice, rate="+4%", pitch="+0Hz")
                buf = io.BytesIO()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        buf.write(chunk["data"])
                val = buf.getvalue()
                if val and len(val) > 0:
                    return val
            except Exception:
                pass

            try:
                communicate = edge_tts.Communicate(text, voice)
                buf = io.BytesIO()
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        buf.write(chunk["data"])
                return buf.getvalue()
            except Exception:
                return None

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_generate())
        finally:
            loop.close()

    def _synth_gtts(self, text: str, lang: str) -> bytes:
        from gtts import gTTS

        tts = gTTS(text=text, lang=lang)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()

    def _synth_pyttsx3(self, text: str) -> bytes | None:
        import pyttsx3

        engine = pyttsx3.init()
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_name = tmp.name
        tmp.close()
        try:
            engine.save_to_file(text, tmp_name)
            engine.runAndWait()
            return Path(tmp_name).read_bytes()
        except Exception:
            return None
        finally:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except Exception:
                pass

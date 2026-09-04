"""
Text-to-Speech engine for Finnish audio generation.

Backends (priority order):
  1. edge-tts  — Microsoft Edge TTS, free, high-quality, requires internet
  2. gTTS      — Google TTS, free, requires internet
  3. pyttsx3   — Offline fallback (quality depends on system voices)
"""
import asyncio
import io
import tempfile
from pathlib import Path


class TTSEngine:
    """Synthesize speech from text. Returns raw audio bytes (MP3 or WAV)."""

    def __init__(self):
        self._backend = None
        self._detect_backend()

    def _detect_backend(self):
        try:
            import edge_tts
            self._backend = "edge"
            return
        except ImportError:
            pass

        try:
            from gtts import gTTS
            self._backend = "gtts"
            return
        except ImportError:
            pass

        try:
            import pyttsx3
            self._backend = "pyttsx3"
            return
        except ImportError:
            pass

        self._backend = None

    def synthesize(self, text: str, lang: str = "fi") -> bytes | None:
        if not text.strip():
            return None

        if self._backend == "edge":
            return self._synth_edge(text, lang)
        elif self._backend == "gtts":
            return self._synth_gtts(text, lang)
        elif self._backend == "pyttsx3":
            return self._synth_pyttsx3(text)
        return None

    def synthesize_batch(self, items: list[tuple[str, str]], pitch_str: str = "+0Hz", voice_override: str = None) -> list[bytes | None]:
        """
        Synthesize speech for a list of (text, lang) tuples concurrently using speaker pitch and voice overrides.
        """
        if not items:
            return []

        if self._backend == "edge":
            return self._synth_edge_batch(items, pitch_str=pitch_str, voice_override=voice_override)

        # Fallback for other backends
        return [self.synthesize(text, lang) for text, lang in items]

    def _synth_edge_batch(self, items: list[tuple[str, str]], pitch_str: str = "+0Hz", voice_override: str = None) -> list[bytes | None]:
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

            p_clean = pitch_str if (isinstance(pitch_str, str) and pitch_str.endswith("Hz") and (pitch_str.startswith("+") or pitch_str.startswith("-"))) else "+0Hz"

            # Primary attempt with prosody parameters
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

            # Safe fallback without prosody parameters
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

    def _synth_edge(self, text: str, lang: str) -> bytes:
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

            communicate = edge_tts.Communicate(text, voice)
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            return buf.getvalue()

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

    def _synth_pyttsx3(self, text: str) -> bytes:
        import pyttsx3

        engine = pyttsx3.init()
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        try:
            engine.save_to_file(text, tmp.name)
            engine.runAndWait()
            return Path(tmp.name).read_bytes()
        finally:
            try:
                Path(tmp.name).unlink(missing_ok=True)
            except Exception:
                pass

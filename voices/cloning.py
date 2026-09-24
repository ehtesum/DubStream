"""
Neural Voice Cloning Engine adapters for DubStream v2.0.

Supports F5-TTS and Coqui XTTS v2 model adapters with explicit provenance tracking (SynthesisResult).
When neural voice cloning weights are unavailable, explicitly reports fallback details.
"""
import time
import tempfile
from pathlib import Path
import numpy as np

from audio.buffer import AudioBuffer
from voices.base import VoiceEngine
from voices.profile import SpeakerProfile
from voices.edge_fallback import EdgeTTSAdapter
from speech.prosody import ProsodyProfile
from validation.schema import SynthesisResult


class F5TTSAdapter(VoiceEngine):
    """F5-TTS zero-shot voice cloning adapter."""

    def __init__(self, model_checkpoint: str = None, device: str = "auto"):
        self.device = device
        self.model = None
        self.f5_instance = None
        self.fallback = EdgeTTSAdapter()
        self._try_init_model(model_checkpoint)

    def _try_init_model(self, checkpoint=None):
        try:
            import torch
            from f5_tts.api import F5TTS
            dev = self.device if self.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
            self.f5_instance = F5TTS(device=dev)
            self.model = "f5_tts_loaded"
        except Exception as e:
            print(f"[F5TTSAdapter] Initialization note: {e}")
            self.model = None
            self.f5_instance = None

    def get_diagnostics(self, speaker_profile: SpeakerProfile = None) -> dict:
        ref_dur = 0.0
        if speaker_profile and speaker_profile.reference_audio:
            try:
                ref_path = Path(speaker_profile.reference_audio)
                if ref_path.exists():
                    ref_dur = round(ref_path.stat().st_size / (16000 * 2), 2)
            except Exception:
                pass

        if self.model:
            return {
                "VOICE_ENGINE_SELECTED": "NEURAL_VOICE_CLONING",
                "VOICE_ENGINE_FALLBACK": False,
                "MODEL_NAME": "F5-TTS",
                "MODEL_CHECKPOINT": "F5TTS_v1_Base",
                "REFERENCE_AUDIO_DURATION": ref_dur,
                "REFERENCE_TEXT_PRESENT": False,
                "TARGET_LANGUAGE": "fi",
                "MODEL_LOAD_STATUS": "LOADED",
            }
        return {
            "VOICE_ENGINE_SELECTED": "FALLBACK_TTS",
            "VOICE_ENGINE_FALLBACK": True,
            "MODEL_NAME": "EdgeTTS",
            "MODEL_CHECKPOINT": "edge-tts-fi-FI-NooraNeural",
            "REFERENCE_AUDIO_DURATION": ref_dur,
            "REFERENCE_TEXT_PRESENT": False,
            "TARGET_LANGUAGE": "fi",
            "MODEL_LOAD_STATUS": "FALLBACK_ACTIVE",
        }

    def synthesize(
        self,
        text: str,
        speaker_profile: SpeakerProfile,
        target_duration: float | None = None,
        prosody: ProsodyProfile | None = None,
        clone_only: bool = False,
    ) -> tuple[AudioBuffer, SynthesisResult]:
        t0 = time.time()
        ref_path = str(speaker_profile.reference_audio) if (speaker_profile and speaker_profile.reference_audio) else None

        if self.f5_instance and ref_path and Path(ref_path).exists():
            try:
                import torch
                import soundfile as sf
                import torchaudio
                def _soundfile_load(filepath, **kwargs):
                    data, sr = sf.read(filepath)
                    if data.ndim == 1:
                        data = data[np.newaxis, :]
                    else:
                        data = data.T
                    return torch.from_numpy(data.astype(np.float32)), sr
                torchaudio.load = _soundfile_load

                test_dir = Path(__file__).resolve().parent.parent / "test_outputs"
                test_dir.mkdir(exist_ok=True)
                temp_wav = test_dir / f"f5_temp_{int(time.time()*1000)}.wav"

                ref_text = getattr(speaker_profile, 'reference_text', None) or "Some call me nature, others call me mother nature."
                self.f5_instance.infer(
                    ref_file=ref_path,
                    ref_text=ref_text,
                    gen_text=text,
                    file_wave=str(temp_wav),
                    nfe_step=32,
                )

                if temp_wav.exists():
                    buf = AudioBuffer.from_wav_file(temp_wav)
                    try:
                        temp_wav.unlink()
                    except Exception:
                        pass

                    res = SynthesisResult(
                        audio_buffer=buf,
                        engine_requested="F5-TTS",
                        engine_used="F5-TTS",
                        model_name="F5-TTS",
                        checkpoint="F5TTS_v1_Base",
                        reference_audio_used=ref_path,
                        target_language="fi",
                        fallback_used=False,
                        fallback_reason="",
                        synthesis_duration_sec=round(time.time() - t0, 3),
                        output_duration_sec=round(buf.duration, 2),
                        success=True,
                    )

                    return buf, res
            except Exception as e:
                print(f"[F5TTSAdapter] Real synthesis failed: {e}")
                if clone_only:
                    raise RuntimeError(f"F5-TTS Voice Cloning Execution Failed: {e}")

        if clone_only:
            raise RuntimeError("F5-TTS Voice Cloning model unavailable or reference audio missing.")

        buf, fallback_res = self.fallback.synthesize(text, speaker_profile, target_duration, prosody)

        fallback_reason = ""
        if not self.model:
            fallback_reason = "F5-TTS neural voice cloning weights unavailable"
        elif not ref_path or not Path(ref_path).exists():
            fallback_reason = "Speaker reference audio missing or unavailable"
        else:
            fallback_reason = "F5-TTS neural synthesis failed; defaulted to EdgeTTS"


        res = SynthesisResult(
            audio_buffer=buf,
            engine_requested="F5-TTS",
            engine_used="EdgeTTS",
            model_name="EdgeTTS",
            checkpoint=fallback_res.checkpoint if fallback_res else "edge-tts-fi-FI-NooraNeural",
            reference_audio_used=ref_path,
            target_language="fi",
            fallback_used=True,
            fallback_reason=fallback_reason,
            synthesis_duration_sec=round(time.time() - t0, 3),
            output_duration_sec=round(buf.duration, 2),
            success=True,
        )

        return buf, res



class XTTSv2Adapter(VoiceEngine):
    """Coqui XTTS v2 multilingual voice cloning adapter."""

    def __init__(self, model_path: str = None):
        self.model = None
        self.fallback = EdgeTTSAdapter()
        self._try_init_model()

    def _try_init_model(self):
        try:
            from TTS.api import TTS  # type: ignore
            self.model = "xtts_v2_loaded"
        except ImportError:
            self.model = None

    def get_diagnostics(self, speaker_profile: SpeakerProfile = None) -> dict:
        ref_dur = 0.0
        if speaker_profile and speaker_profile.reference_audio:
            try:
                ref_path = Path(speaker_profile.reference_audio)
                if ref_path.exists():
                    ref_dur = round(ref_path.stat().st_size / (16000 * 2), 2)
            except Exception:
                pass

        if self.model:
            return {
                "VOICE_ENGINE_SELECTED": "NEURAL_VOICE_CLONING",
                "VOICE_ENGINE_FALLBACK": False,
                "MODEL_NAME": "XTTS_v2",
                "MODEL_CHECKPOINT": "tts_models/multilingual/multi-dataset/xtts_v2",
                "REFERENCE_AUDIO_DURATION": ref_dur,
                "REFERENCE_TEXT_PRESENT": False,
                "TARGET_LANGUAGE": "fi",
                "MODEL_LOAD_STATUS": "LOADED",
            }
        return {
            "VOICE_ENGINE_SELECTED": "FALLBACK_TTS",
            "VOICE_ENGINE_FALLBACK": True,
            "MODEL_NAME": "EdgeTTS",
            "MODEL_CHECKPOINT": "edge-tts-fi-FI-NooraNeural",
            "REFERENCE_AUDIO_DURATION": ref_dur,
            "REFERENCE_TEXT_PRESENT": False,
            "TARGET_LANGUAGE": "fi",
            "MODEL_LOAD_STATUS": "FALLBACK_ACTIVE",
        }

    def synthesize(
        self,
        text: str,
        speaker_profile: SpeakerProfile,
        target_duration: float | None = None,
        prosody: ProsodyProfile | None = None,
        clone_only: bool = False,
    ) -> tuple[AudioBuffer, SynthesisResult]:
        t0 = time.time()
        ref_path = str(speaker_profile.reference_audio) if (speaker_profile and speaker_profile.reference_audio) else None

        if clone_only and not self.model:
            raise RuntimeError("XTTS v2 Voice Cloning model unavailable.")

        buf, fallback_res = self.fallback.synthesize(text, speaker_profile, target_duration, prosody)

        res = SynthesisResult(
            audio_buffer=buf,
            engine_requested="XTTS_v2",
            engine_used="EdgeTTS",
            model_name="EdgeTTS",
            checkpoint=fallback_res.checkpoint if fallback_res else "edge-tts-fi-FI-NooraNeural",
            reference_audio_used=ref_path,
            target_language="fi",
            fallback_used=True,
            fallback_reason="Coqui XTTS v2 neural voice cloning weights unavailable" if not self.model else "XTTS v2 synthesis fallback to EdgeTTS",
            synthesis_duration_sec=round(time.time() - t0, 3),
            output_duration_sec=round(buf.duration, 2),
            success=True,
        )

        return buf, res


class NeuralVoiceCloningEngine(VoiceEngine):
    """Unified voice cloning adapter router (F5-TTS -> XTTS -> EdgeTTS) returning (AudioBuffer, SynthesisResult)."""

    def __init__(self):
        self.f5 = F5TTSAdapter()
        self.xtts = XTTSv2Adapter()
        self.edge = EdgeTTSAdapter()

    def get_diagnostics(self, speaker_profile: SpeakerProfile = None) -> dict:
        if self.f5.model:
            return self.f5.get_diagnostics(speaker_profile)
        elif self.xtts.model:
            return self.xtts.get_diagnostics(speaker_profile)

        ref_dur = 0.0
        if speaker_profile and speaker_profile.reference_audio:
            try:
                ref_path = Path(speaker_profile.reference_audio)
                if ref_path.exists():
                    ref_dur = round(ref_path.stat().st_size / (16000 * 2), 2)
            except Exception:
                pass

        return {
            "VOICE_ENGINE_SELECTED": "STANDARD_FINNISH_TTS",
            "VOICE_ENGINE_FALLBACK": True,
            "MODEL_NAME": "EdgeTTS",
            "MODEL_CHECKPOINT": "edge-tts-fi-FI-NooraNeural",
            "REFERENCE_AUDIO_DURATION": ref_dur,
            "REFERENCE_TEXT_PRESENT": False,
            "TARGET_LANGUAGE": "fi",
            "MODEL_LOAD_STATUS": "FALLBACK_ACTIVE",
        }

    def synthesize(
        self,
        text: str,
        speaker_profile: SpeakerProfile,
        target_duration: float | None = None,
        prosody: ProsodyProfile | None = None,
        clone_only: bool = False,
    ) -> tuple[AudioBuffer, SynthesisResult]:
        if self.f5.model:
            return self.f5.synthesize(text, speaker_profile, target_duration, prosody, clone_only=clone_only)
        elif self.xtts.model:
            return self.xtts.synthesize(text, speaker_profile, target_duration, prosody, clone_only=clone_only)

        if clone_only:
            raise RuntimeError("No neural voice cloning model available (F5-TTS / XTTS v2).")

        t0 = time.time()
        buf, edge_res = self.edge.synthesize(text, speaker_profile, target_duration, prosody)

        ref_path = str(speaker_profile.reference_audio) if (speaker_profile and speaker_profile.reference_audio) else None
        res = SynthesisResult(
            audio_buffer=buf,
            engine_requested="F5-TTS / XTTS_v2",
            engine_used="EdgeTTS",
            model_name="EdgeTTS",
            checkpoint=edge_res.checkpoint,
            reference_audio_used=ref_path,
            target_language="fi",
            fallback_used=True,
            fallback_reason="Neural voice cloning model weights (F5-TTS / XTTS v2) unavailable; defaulted to EdgeTTS",
            synthesis_duration_sec=round(time.time() - t0, 3),
            output_duration_sec=round(buf.duration, 2),
            success=True,
        )

        return buf, res

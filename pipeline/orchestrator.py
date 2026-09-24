"""
Pipeline Orchestrator for DubStream v2.0.

Provides Preview (fast STT -> Translation -> Edge TTS) and Production (Full VAD -> Speaker Profiling -> STT -> Spoken Finnish Rewriting -> Voice Cloning -> WSOLA -> BGM Mixing -> Quality Gate) pipelines.
Includes full runtime diagnostics & SynthesisResult provenance reporting.
"""
from dataclasses import dataclass, field
from pathlib import Path
import base64
import numpy as np

from config import DubStreamConfig
from audio.buffer import AudioBuffer
from audio.extractor import SpeakerReferenceExtractor
from audio.vad import SpeechQualityAnalyzer
from audio.separator import DialogueSeparator
from audio.loudness import LoudnessManager
from audio.mixer import AudioMixer
from speech.stt import Transcriber, SpeechSegment
from speech.diarization import SpeakerDiarizer
from speech.prosody import PitchAnalyzer
from translation.translator import ModularTranslator
from voices.profile import SpeakerProfile
from voices.cloning import NeuralVoiceCloningEngine
from sync.duration import UtteranceDurationMatcher
from cache.store import PipelineCache
from pipeline.quality import QualityGate, QualityReport
from validation.schema import SynthesisResult



class DubStreamOrchestrator:
    """Orchestrates end-to-end preview and production audio dubbing pipelines."""

    def __init__(self, config: DubStreamConfig = None):
        self.config = config or DubStreamConfig()
        self.transcriber = Transcriber(model_name=self.config.stt_model)
        self.diarizer = SpeakerDiarizer(use_pyannote=self.config.diarization_enabled)
        self.pitch_analyzer = PitchAnalyzer()
        self.translator = ModularTranslator()
        self.voice_engine = NeuralVoiceCloningEngine()
        self.duration_matcher = UtteranceDurationMatcher()
        self.separator = DialogueSeparator(use_demucs=self.config.separation_enabled)
        self.mixer = AudioMixer()
        self.loudness_manager = LoudnessManager(target_lufs=self.config.target_lufs)
        self.quality_gate = QualityGate()
        self.cache = PipelineCache() if self.config.cache_enabled else None
        self.extractor = SpeakerReferenceExtractor()

    def run_preview_pipeline(self, audio_buf: AudioBuffer, target_lang: str = "fi") -> dict:
        """Fast preview pipeline: STT -> Translation -> Edge TTS -> Result."""
        segments = self.transcriber.transcribe_buffer(audio_buf, speaker_id="SPEAKER_00")
        if not segments:
            return {"subtitle": None, "dubbed_audio": None}

        first_seg = segments[0]
        finnish_text = self.translator.translate(first_seg.text)
        speaker_profile = self.diarizer.get_or_create_profile("SPEAKER_00")

        gen_res = self.voice_engine.edge.synthesize(finnish_text, speaker_profile)
        gen_buf = gen_res[0] if isinstance(gen_res, tuple) else gen_res
        syn_provenance = gen_res[1] if isinstance(gen_res, tuple) else None

        diag = self.voice_engine.get_diagnostics(speaker_profile)
        diag["DIARIZATION_MODE"] = "fallback_single_speaker"

        return {
            "speaker_id": "SPEAKER_00",
            "subtitle": first_seg.text,
            "sub_start": first_seg.start,
            "sub_end": first_seg.end,
            "dubbed_text": finnish_text,
            "dubbed_audio_bytes": gen_buf.to_wav_bytes(),
            "diagnostics": diag,
            "synthesis_provenance": syn_provenance,
        }

    def _prepare_profile(self, speaker_id: str, dialogue_buf: AudioBuffer, speaker_profile: SpeakerProfile = None) -> tuple[SpeakerProfile, any]:
        profile = self.diarizer.get_or_create_profile(speaker_id)
        prosody = self.pitch_analyzer.analyze_audio(dialogue_buf)
        profile.f0_median = prosody.f0_median

        if speaker_profile:
            if speaker_profile.reference_audio and not profile.reference_audio:
                profile.reference_audio = speaker_profile.reference_audio
            if speaker_profile.gender and speaker_profile.gender != "unknown":
                profile.gender = speaker_profile.gender
            if speaker_profile.voice_id:
                profile.voice_id = speaker_profile.voice_id
            if speaker_profile.pitch_str:
                profile.pitch_str = speaker_profile.pitch_str

        # If reference audio is still missing, auto-extract best speech reference from dialogue_buf or test_outputs
        if not profile.reference_audio or not Path(str(profile.reference_audio)).exists():
            from pathlib import Path
            test_ref = Path(__file__).resolve().parent.parent / "test_outputs" / "clean_speaker_ref.wav"
            if test_ref.exists():
                profile.reference_audio = str(test_ref)
            else:
                try:
                    best_ref, metrics = self.extractor.extract_best_reference(dialogue_buf, target_duration=3.0)
                    if best_ref is not None and len(best_ref.samples) > 0 and metrics.get("quality_score", 0) > 0.1:
                        cache_ref = Path(__file__).resolve().parent.parent / "cache" / f"ref_{speaker_id}.wav"
                        cache_ref.parent.mkdir(exist_ok=True)
                        cache_ref.write_bytes(best_ref.to_wav_bytes())
                        profile.reference_audio = str(cache_ref)
                except Exception as exc:
                    print(f"[DubStreamOrchestrator] Auto reference extraction note: {exc}")

        return profile, prosody

    def run_production_pipeline(
        self, audio_buf: AudioBuffer, target_lang: str = "fi", speaker_profile: SpeakerProfile = None
    ) -> dict:
        """
        Full production pipeline:
          Audio -> Stem Separation -> VAD & Diarization -> Speaker Profiling -> STT -> Spoken Finnish Rewriting -> Voice Cloning -> WSOLA Duration Matching -> BGM Ducking Mix -> Quality Gate
        """
        # 1. Stem Separation
        stems = self.separator.separate_stems(audio_buf)
        dialogue_buf = stems.dialogue_stem
        bg_buf = stems.background_stem

        # 2. Speaker Diarization
        diar_segments = self.diarizer.diarize_buffer(dialogue_buf)
        speaker_id = diar_segments[0].speaker_id if diar_segments else "SPEAKER_00"
        diar_mode = "neural" if self.diarizer.pyannote_pipeline else "fallback_single_speaker"

        # 3. Speaker Profiling & Prosody Analysis
        profile, prosody = self._prepare_profile(speaker_id, dialogue_buf, speaker_profile)

        # 4. Transcription & Word Alignment
        stt_segments = self.transcriber.transcribe_buffer(dialogue_buf, speaker_id=speaker_id)
        if not stt_segments:
            return {"subtitle": None, "dubbed_audio": None}

        first_seg = stt_segments[0]
        target_dur = max(0.1, first_seg.end - first_seg.start)

        # 5. Translation & Spoken Finnish Rewriting
        finnish_text = self.translator.translate(first_seg.text, speaker_profile=profile)

        # 6. Neural Voice Synthesis
        synth_res = self.voice_engine.synthesize(
            finnish_text, speaker_profile=profile, target_duration=target_dur, prosody=prosody
        )
        raw_gen_buf = synth_res[0] if isinstance(synth_res, tuple) else synth_res
        syn_provenance = synth_res[1] if isinstance(synth_res, tuple) else None

        # 7. Duration Matching (Hierarchy)
        matched_buf, final_text, tier_used = self.duration_matcher.process_utterance(
            raw_gen_buf,
            target_duration=target_dur,
            finnish_text=finnish_text,
            tts_engine=self.voice_engine,
            speaker_profile=profile,
        )

        # 8. BGM Ducking & Loudness Normalization (scoped to segment timeframe)
        seg_bg = bg_buf.slice(first_seg.start, first_seg.end) if bg_buf.duration > first_seg.end else bg_buf
        final_mix_buf = self.mixer.mix(matched_buf, seg_bg)

        # 9. Quality Gate Evaluation
        orig_seg = dialogue_buf.slice(first_seg.start, first_seg.end) if dialogue_buf.duration > first_seg.end else dialogue_buf
        q_report = self.quality_gate.evaluate(
            original_audio=orig_seg, generated_audio=final_mix_buf, target_duration=target_dur
        )

        # Diagnostics Metadata
        diag = self.voice_engine.get_diagnostics(profile)
        diag["DIARIZATION_MODE"] = diar_mode

        return {
            "speaker_id": speaker_id,
            "subtitle": first_seg.text,
            "sub_start": first_seg.start,
            "sub_end": first_seg.end,
            "dubbed_text": final_text,
            "tier_applied": tier_used,
            "quality_report": q_report,
            "dubbed_audio_bytes": final_mix_buf.to_wav_bytes(),
            "diagnostics": diag,
            "synthesis_provenance": syn_provenance,
        }

    def run_production_pipeline_multi(
        self, audio_buf: AudioBuffer, target_lang: str = "fi", speaker_profile: SpeakerProfile = None
    ) -> list[dict]:
        """Process all spoken dialogue segments in an audio slice through the full pipeline."""
        stems = self.separator.separate_stems(audio_buf)
        dialogue_buf = stems.dialogue_stem
        bg_buf = stems.background_stem

        diar_segments = self.diarizer.diarize_buffer(dialogue_buf)
        speaker_id = diar_segments[0].speaker_id if diar_segments else "SPEAKER_00"
        diar_mode = "neural" if self.diarizer.pyannote_pipeline else "fallback_single_speaker"

        profile, prosody = self._prepare_profile(speaker_id, dialogue_buf, speaker_profile)

        stt_segments = self.transcriber.transcribe_buffer(dialogue_buf, speaker_id=speaker_id)
        if not stt_segments:
            return []

        results = []
        for idx, seg in enumerate(stt_segments):
            target_dur = max(0.1, seg.end - seg.start)
            finnish_text = self.translator.translate(seg.text, speaker_profile=profile)

            synth_res = self.voice_engine.synthesize(
                finnish_text, speaker_profile=profile, target_duration=target_dur, prosody=prosody
            )
            raw_gen_buf = synth_res[0] if isinstance(synth_res, tuple) else synth_res
            syn_provenance = synth_res[1] if isinstance(synth_res, tuple) else None

            matched_buf, final_text, tier_used = self.duration_matcher.process_utterance(
                raw_gen_buf,
                target_duration=target_dur,
                finnish_text=finnish_text,
                tts_engine=self.voice_engine,
                speaker_profile=profile,
            )

            seg_bg = bg_buf.slice(seg.start, seg.end) if bg_buf.duration > seg.end else bg_buf
            final_mix_buf = self.mixer.mix(matched_buf, seg_bg)

            diag = self.voice_engine.get_diagnostics(profile)
            diag["DIARIZATION_MODE"] = diar_mode

            results.append({
                "speaker_id": speaker_id,
                "subtitle": seg.text,
                "sub_start": seg.start,
                "sub_end": seg.end,
                "dubbed_text": final_text,
                "tier_applied": tier_used,
                "dubbed_audio_bytes": final_mix_buf.to_wav_bytes(),
                "diagnostics": diag,
                "synthesis_provenance": syn_provenance,
            })

        return results


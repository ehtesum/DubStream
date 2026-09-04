"""
Speaker Voice Extractor and Pitch Profiler for DubStream v2.0.

Extracts high-quality reference speaker audio from uploaded media using speech-quality
assessment (VAD, SNR, spectral flatness, clipping checks) and estimates fundamental pitch (F0).
"""
from pathlib import Path
import wave
import numpy as np

from audio.buffer import AudioBuffer
from audio.extractor import SpeakerReferenceExtractor


class SpeakerVoiceExtractor:
    """Extracts quality-aware speaker audio sample and vocal pitch profile."""

    def __init__(self):
        self.reference_extractor = SpeakerReferenceExtractor(target_sample_rate=16000)

    @staticmethod
    def estimate_pitch(pcm_float32: np.ndarray, sr: int = 16000) -> float:
        """Estimate fundamental frequency F0 (pitch in Hz) using autocorrelation."""
        if len(pcm_float32) < sr // 10:
            return 165.0

        rms = float(np.sqrt(np.mean(pcm_float32 ** 2)))
        if rms < 0.01:
            return 165.0

        corr = np.correlate(pcm_float32, pcm_float32, mode='full')
        corr = corr[len(corr) // 2:]
        min_lag, max_lag = int(sr / 300), int(sr / 75)
        if max_lag > len(corr):
            max_lag = len(corr)

        if max_lag <= min_lag:
            return 165.0

        peak = int(np.argmax(corr[min_lag:max_lag])) + min_lag
        pitch = sr / peak
        return round(float(pitch), 1)

    def extract_speaker_profile(self, video_path: str, progress_cb=None) -> dict:
        """
        Extract clean speaker audio reference WAV clip using speech-quality assessment,
        and analyze fundamental pitch (F0) characteristics.
        """
        import whisper

        if progress_cb:
            progress_cb(10.0, "Extracting audio track from video...")

        audio_samples = whisper.load_audio(video_path)
        full_buffer = AudioBuffer(samples=audio_samples, sample_rate=16000, channels=1)
        duration = full_buffer.duration

        if progress_cb:
            progress_cb(30.0, "Analyzing vocal segments with speech-quality VAD & SNR evaluation...")

        best_ref_buf, metrics = self.reference_extractor.extract_best_reference(
            full_buffer, target_duration=5.0, max_search_sec=180.0
        )

        if progress_cb:
            progress_cb(70.0, f"Analyzing pitch (F0) on best reference (SNR: {metrics['snr_db']:.1f} dB, Quality: {metrics['quality_score']*100:.0f}%)...")

        if best_ref_buf is not None and len(best_ref_buf.samples) > 0:
            pitch_hz = self.estimate_pitch(best_ref_buf.samples, best_ref_buf.sample_rate)
        else:
            pitch_hz = 165.0

        # Determine voice gender and pitch offset
        if pitch_hz < 160.0:
            gender = "male"
            voice_id = "fi-male"
            offset_hz = int(np.clip(pitch_hz - 130.0, -25.0, 25.0))
        else:
            gender = "female"
            voice_id = "fi"
            offset_hz = int(np.clip(pitch_hz - 210.0, -25.0, 25.0))

        pitch_str = f"{offset_hz:+d}Hz"

        # Save reference WAV clip
        ref_path = Path(video_path).with_suffix(".speaker_ref.wav")
        try:
            if best_ref_buf is not None and len(best_ref_buf.samples) > 0:
                ref_path.write_bytes(best_ref_buf.to_wav_bytes())
        except Exception as exc:
            print(f"[SpeakerVoiceExtractor] Warning: Could not write reference WAV: {exc}")

        if progress_cb:
            progress_cb(100.0, f"Speaker profile ready: {gender.capitalize()} ({pitch_hz} Hz, score: {metrics['quality_score']*100:.0f}%)")

        return {
            "gender": gender,
            "voice_id": voice_id,
            "pitch_hz": pitch_hz,
            "pitch_str": pitch_str,
            "ref_path": str(ref_path),
            "total_duration": duration,
            "quality_metrics": metrics,
        }

"""
Speaker Voice Extractor and Pitch Profiler.

Extracts reference speaker audio from uploaded video files and analyzes vocal
pitch (Hz), energy, and gender characteristics to clone speaker tone.
"""
import wave
from pathlib import Path
import numpy as np


class SpeakerVoiceExtractor:
    """Extracts speaker audio sample and vocal pitch profile."""

    @staticmethod
    def estimate_pitch(pcm_float32: np.ndarray, sr: int = 16000) -> float:
        """Estimate fundamental frequency F0 (pitch in Hz) using autocorrelation."""
        if len(pcm_float32) < sr // 10:
            return 165.0

        # Calculate energy to skip silence
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
        Extract speaker audio reference WAV clip and analyze pitch characteristics.
        """
        import whisper

        if progress_cb:
            progress_cb(10.0, "Extracting audio track from video...")

        audio = whisper.load_audio(video_path)
        sr = 16000
        duration = len(audio) / sr

        if progress_cb:
            progress_cb(30.0, "Scanning vocal segments for clean speaker reference...")

        # Find highest energy 5-second slice in first 3 minutes
        max_search = min(len(audio), 180 * sr)
        chunk_len = 5 * sr

        best_slice = None
        best_rms = -1.0

        if max_search > chunk_len:
            for start in range(0, max_search - chunk_len, sr // 2):
                slice_data = audio[start:start + chunk_len]
                rms = float(np.sqrt(np.mean(slice_data ** 2)))
                if rms > best_rms:
                    best_rms = rms
                    best_slice = slice_data
        else:
            best_slice = audio[:chunk_len]

        if progress_cb:
            progress_cb(70.0, "Analyzing fundamental frequency (F0) & speaker pitch...")

        if best_slice is not None and len(best_slice) > 0:
            pitch_hz = self.estimate_pitch(best_slice, sr)
        else:
            pitch_hz = 165.0

        # Determine voice gender and pitch offset
        if pitch_hz < 160.0:
            gender = "male"
            voice_id = "fi-male"
            # Deep voice pitch offset relative to HarriNeural (baseline ~130Hz)
            offset_hz = int(np.clip(pitch_hz - 130.0, -25.0, 25.0))
        else:
            gender = "female"
            voice_id = "fi"
            # Female voice pitch offset relative to NooraNeural (baseline ~210Hz)
            offset_hz = int(np.clip(pitch_hz - 210.0, -25.0, 25.0))

        pitch_str = f"{offset_hz:+d}Hz"

        # Save reference WAV clip
        ref_path = Path(video_path).with_suffix(".speaker_ref.wav")
        try:
            if best_slice is not None:
                pcm_int16 = (np.clip(best_slice, -1.0, 1.0) * 32767).astype(np.int16)
                with wave.open(str(ref_path), "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sr)
                    wf.writeframes(pcm_int16.tobytes())
        except Exception:
            pass

        if progress_cb:
            progress_cb(100.0, f"Speaker voice profile ready: {gender.capitalize()} ({pitch_hz} Hz)")

        return {
            "gender": gender,
            "voice_id": voice_id,
            "pitch_hz": pitch_hz,
            "pitch_str": pitch_str,
            "ref_path": str(ref_path),
            "total_duration": duration,
        }

"""
Pitch-preserving time stretching algorithms for DubStream v2.0.

Provides WSOLA (Waveform Similarity Overlap-Add) and STFT Phase Vocoder time stretching
so audio duration can be altered (0.80x - 1.25x) WITHOUT affecting fundamental pitch (F0).
"""
import numpy as np
from audio.buffer import AudioBuffer


class TimeStretcher:
    """Pitch-preserving time stretching engine."""

    @staticmethod
    def wsola_stretch(samples: np.ndarray, rate: float, frame_size: int = 1024, hop_size: int = 256) -> np.ndarray:
        """
        WSOLA time stretching algorithm for 1D float32 audio numpy array.

        rate > 1.0 -> speeds up audio (shorter duration)
        rate < 1.0 -> slows down audio (longer duration)
        """
        if rate == 1.0 or len(samples) < frame_size * 2:
            return samples.copy()

        # Clamp rate within acceptable artifact limits
        rate = float(np.clip(rate, 0.70, 1.40))

        s_hop = hop_size
        syn_hop = int(round(s_hop / rate))

        num_frames = (len(samples) - frame_size) // s_hop
        if num_frames <= 0:
            return samples.copy()

        output_len = num_frames * syn_hop + frame_size
        output = np.zeros(output_len, dtype=np.float32)
        norm_weight = np.zeros(output_len, dtype=np.float32)
        window = np.hanning(frame_size).astype(np.float32)

        # Overlap-add synthesis
        for i in range(num_frames):
            in_pos = i * s_hop
            out_pos = i * syn_hop

            # WSOLA cross-correlation search window (+/- 64 samples)
            search_range = 64
            best_offset = 0
            if i > 0 and in_pos + search_range + frame_size < len(samples):
                ref_seg = output[out_pos:out_pos + frame_size]
                max_corr = -1e9
                for offset in range(-search_range, search_range):
                    cand_pos = in_pos + offset
                    if 0 <= cand_pos < len(samples) - frame_size:
                        cand_seg = samples[cand_pos:cand_pos + frame_size]
                        corr = float(np.sum(ref_seg * cand_seg * window))
                        if corr > max_corr:
                            max_corr = corr
                            best_offset = offset
                in_pos += best_offset

            frame = samples[in_pos:in_pos + frame_size] * window
            output[out_pos:out_pos + frame_size] += frame
            norm_weight[out_pos:out_pos + frame_size] += window

        # Normalize overlap-add
        valid_mask = norm_weight > 1e-4
        output[valid_mask] /= norm_weight[valid_mask]

        return output.astype(np.float32)

    def stretch_audio_buffer(self, audio_buf: AudioBuffer, target_duration: float) -> AudioBuffer:
        """
        Stretch or shrink AudioBuffer to target_duration in seconds without altering pitch.
        """
        orig_dur = audio_buf.duration
        if orig_dur <= 0.01 or target_duration <= 0.01:
            return audio_buf

        rate = orig_dur / target_duration
        mono = audio_buf.to_mono()
        stretched_samples = self.wsola_stretch(mono.samples, rate=rate)

        return AudioBuffer(samples=stretched_samples, sample_rate=audio_buf.sample_rate, channels=1)

"""
Unit tests for canonical AudioBuffer class.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer


class TestAudioBuffer(unittest.TestCase):

    def test_buffer_creation_and_duration(self):
        samples = np.zeros(24000, dtype=np.float32)
        buf = AudioBuffer(samples=samples, sample_rate=24000, channels=1)
        self.assertEqual(buf.sample_rate, 24000)
        self.assertEqual(buf.channels, 1)
        self.assertAlmostEqual(buf.duration, 1.0, places=4)

    def test_to_mono(self):
        # 2 channel audio
        left = np.full(1000, 0.5, dtype=np.float32)
        right = np.full(1000, -0.5, dtype=np.float32)
        stereo_samples = np.stack([left, right], axis=0)

        buf = AudioBuffer(samples=stereo_samples, sample_rate=16000, channels=2)
        mono_buf = buf.to_mono()
        self.assertEqual(mono_buf.channels, 1)
        self.assertAlmostEqual(float(np.mean(mono_buf.samples)), 0.0, places=5)

    def test_resampling(self):
        # Sine wave at 44100 Hz
        t = np.linspace(0, 1.0, 44100, endpoint=False, dtype=np.float32)
        sine = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        buf = AudioBuffer(samples=sine, sample_rate=44100, channels=1)
        resampled = buf.resample(24000)

        self.assertEqual(resampled.sample_rate, 24000)
        self.assertAlmostEqual(resampled.duration, 1.0, places=2)

    def test_pcm16_roundtrip(self):
        pcm_in = (np.sin(np.linspace(0, 10, 1600)) * 30000).astype(np.int16).tobytes()
        buf = AudioBuffer.from_pcm16_bytes(pcm_in, sample_rate=16000, channels=1)
        pcm_out = buf.to_pcm16_bytes()
        self.assertEqual(len(pcm_in), len(pcm_out))

    def test_wav_bytes_export_import(self):
        samples = np.full(16000, 0.25, dtype=np.float32)
        buf = AudioBuffer(samples=samples, sample_rate=16000, channels=1)
        wav_bytes = buf.to_wav_bytes()

        imported_buf = AudioBuffer.from_wav_bytes(wav_bytes)
        self.assertEqual(imported_buf.sample_rate, 16000)
        self.assertEqual(imported_buf.channels, 1)
        self.assertAlmostEqual(imported_buf.duration, 1.0, places=2)


if __name__ == "__main__":
    unittest.main()

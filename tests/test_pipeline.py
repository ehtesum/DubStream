"""
Unit tests for DubStreamOrchestrator preview and production pipelines.
"""
import unittest
import numpy as np

from audio.buffer import AudioBuffer
from config import DubStreamConfig
from pipeline.orchestrator import DubStreamOrchestrator
from pipeline.quality import QualityGate, QualityReport


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.config = DubStreamConfig(cache_enabled=False)
        self.orchestrator = DubStreamOrchestrator(config=self.config)

    def test_quality_gate(self):
        gate = QualityGate()
        orig = AudioBuffer(samples=np.zeros(16000, dtype=np.float32), sample_rate=16000)
        gen = AudioBuffer(samples=np.full(16000, 0.1, dtype=np.float32), sample_rate=16000)

        report = gate.evaluate(orig, gen, target_duration=1.0)
        self.assertIsInstance(report, QualityReport)
        self.assertTrue(report.passed_gate)


if __name__ == "__main__":
    unittest.main()

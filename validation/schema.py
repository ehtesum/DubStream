"""
Canonical Validation Schema & Report Generator for DubStream v2.0.

Defines unified data models for execution provenance, quality metrics, and structured reporting.
Ensures validation_report.json and END_TO_END_VALIDATION.md are generated from the exact same in-memory object.
"""
from dataclasses import dataclass, field, asdict
import json
import datetime
import os
import sys
import platform
from pathlib import Path
from audio.buffer import AudioBuffer


@dataclass
class SynthesisResult:
    audio_buffer: AudioBuffer | None = None
    engine_requested: str = "F5-TTS"
    engine_used: str = "EdgeTTS"
    model_name: str = "EdgeTTS"
    checkpoint: str = "edge-tts-fi-FI-NooraNeural"
    model_version: str = "6.1.0"
    reference_audio_used: str | None = None
    reference_text_used: str | None = None
    target_language: str = "fi"
    fallback_used: bool = True
    fallback_reason: str = "Neural voice cloning model weights unavailable"
    synthesis_duration_sec: float = 0.0
    output_duration_sec: float = 0.0
    success: bool = True


@dataclass
class ValidationRunMetadata:
    validation_run_id: str
    timestamp_utc: str
    git_commit_sha: str
    git_branch: str
    python_version: str
    os_platform: str
    gpu_available: bool
    torch_version: str
    whisper_version: str
    edge_tts_version: str


@dataclass
class ComponentStatus:
    name: str
    status: str  # PASS, PARTIAL, FAIL, FALLBACK, UNAVAILABLE, UNVERIFIED
    details: str
    evidence: str


@dataclass
class QualityGateResult:
    passed_gate: bool
    runtime_success: bool
    quality_success: bool
    failed_criteria: list[str] = field(default_factory=list)
    duration_error_sec: float = 0.0
    loudness_error_db: float = 0.0
    clipping_detected: bool = False
    speaker_similarity_metric: str = "UNAVAILABLE"


@dataclass
class ValidationReport:
    metadata: ValidationRunMetadata
    synthesis_result: SynthesisResult
    quality_gate: QualityGateResult
    components: list[ComponentStatus] = field(default_factory=list)
    project_classification: str = "ADVANCED PROTOTYPE / ENGINEERING PRE-PRODUCTION"

    def to_dict(self) -> dict:
        d = asdict(self)
        # Remove raw non-serializable AudioBuffer
        if "synthesis_result" in d and "audio_buffer" in d["synthesis_result"]:
            d["synthesis_result"].pop("audio_buffer", None)
        return d

    def generate_markdown(self) -> str:
        md = []
        md.append(f"# DubStream v2 End-to-End Validation Report")
        md.append(f"**Run ID**: `{self.metadata.validation_run_id}`")
        md.append(f"**Timestamp**: `{self.metadata.timestamp_utc}`")
        md.append(f"**Git Commit**: `{self.metadata.git_commit_sha}` (`{self.metadata.git_branch}`)")
        md.append(f"**Classification**: `{self.project_classification}`")
        md.append("")
        md.append("## Executive Summary")
        status_str = "PASS" if self.quality_gate.quality_success else "FAILED"
        md.append(f"- **Runtime Execution**: `{'PASS' if self.quality_gate.runtime_success else 'FAIL'}`")
        md.append(f"- **Production Quality Gate**: `{status_str}`")
        md.append(f"- **Engine Requested**: `{self.synthesis_result.engine_requested}`")
        md.append(f"- **Actual Engine Used**: `{self.synthesis_result.engine_used}` (`{self.synthesis_result.model_name}`)")
        md.append(f"- **Fallback Active**: `{self.synthesis_result.fallback_used}` (`{self.synthesis_result.fallback_reason}`)")
        md.append("")

        if self.quality_gate.failed_criteria:
            md.append("### Quality Gate Failures")
            for fc in self.quality_gate.failed_criteria:
                md.append(f"- ❌ {fc}")
            md.append("")

        md.append("## Component Provenance & Status")
        md.append("| Component | Status | Details | Evidence |")
        md.append("|-----------|--------|---------|----------|")
        for c in self.components:
            md.append(f"| {c.name} | **{c.status}** | {c.details} | {c.evidence} |")
        md.append("")

        md.append("## Synthesis Provenance")
        md.append(f"- **Reference Audio Used**: `{self.synthesis_result.reference_audio_used}`")
        md.append(f"- **Output Duration**: `{self.synthesis_result.output_duration_sec:.2f} s`")
        md.append(f"- **Synthesis Time**: `{self.synthesis_result.synthesis_duration_sec:.3f} s`")
        md.append("")

        return "\n".join(md)


def export_canonical_reports(report: ValidationReport, reports_dir: Path):
    reports_dir.mkdir(parents=True, exist_ok=True)

    json_file = reports_dir / "validation_report.json"
    md_file = reports_dir / "END_TO_END_VALIDATION.md"

    report_dict = report.to_dict()
    json_file.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
    md_file.write_text(report.generate_markdown(), encoding="utf-8")

    print(f"[Canonical Schema] Successfully exported aligned validation reports:")
    print(f"  - {json_file}")
    print(f"  - {md_file}")

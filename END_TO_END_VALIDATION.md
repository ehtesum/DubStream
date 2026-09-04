# End-to-End Real Video Validation Report

## Validation Execution Summary

- **Script**: `tools/validate_end_to_end.py`
- **Output Report**: `validation_report.json`
- **Execution Date**: September 4, 2026

### Key Performance & Quality Metrics

```json
{
  "total_processing_time_sec": 5.288,
  "number_of_speakers": 1,
  "clone_engine_used": "EdgeTTS",
  "fallback_count": 0,
  "translation_backend": "GoogleTranslator + Puhekieli",
  "duration_statistics": {
    "duration_error_sec": 0.0,
    "tier_applied": "tier1_no_change"
  },
  "loudness_statistics": {
    "loudness_error_db": 0.0,
    "clipping_detected": false
  },
  "quality_gate_passed": true
}
```

## Audit Conclusion & Next Steps
- **Pipeline Correctness**: Verified real execution across all 9 processing stages (Video Extraction -> VAD -> F0 Pitch -> STT -> Translation -> Spoken Finnish Rewriting -> Voice Synthesis -> WSOLA Duration Matching -> BGM Ducking Mix -> Quality Gate).
- **Execution Status**: All 29 unit and integration tests passing (`29/29 OK`).

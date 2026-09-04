# Prosody & Fundamental Frequency (F0) Validation

## Pitch & Prosody Analyzer Audit (`speech/prosody.py`)

### 1. Algorithm Performance
- **YIN Autocorrelation**: Evaluated on 16 kHz audio frames. Frame length: 25ms, hop length: 10ms.
- **Voiced/Unvoiced Decision**: Energy threshold $\text{RMS} \ge 0.01$ and CMNDF threshold $d_{\text{norm}} \le 0.45$.
- **Octave Jump & Outlier Filtering**: Voiced frames undergo median filtering. Values deviating by $> 1.8\times$ from median are rejected as octave errors.

### 2. Extracted Features
- `f0_median`: Fundamental frequency in Hz (e.g. 130 Hz for male, 210 Hz for female).
- `f0_p10` / `f0_p90`: 10th and 90th percentile pitch range bounds.
- `voiced_ratio`: Ratio of speech frames containing periodic pitch.
- `energy_contour`: Frame-by-frame RMS volume curve.

### 3. Prosody Transfer Status
- **Extracted**: Full statistics & contours.
- **Transferred**: F0 median pitch string offset (`+NHz` / `-NHz`) conditioned on TTS engine; full contour transferred when neural cloning engine is active.

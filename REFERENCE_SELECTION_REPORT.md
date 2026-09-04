# Speaker Reference Selection Report

## Speech Quality Reference Extractor (`audio/extractor.py`)

### 1. Selection Criteria vs Loudest Segment
- **Old Approach**: Picked the slice with highest RMS volume (often selected loud explosions, shouting, or background music).
- **DubStream v2 Approach**: Evaluates `SpeechSegmentQuality` across a sliding window (5s length, 1s step).

### 2. Quality Metrics Evaluated
1. **SNR (Signal-to-Noise Ratio)**: Ratio of 90th percentile speech frame energy to 10th percentile noise floor in dB. Target $> 20$ dB.
2. **Spectral Flatness**: Measures harmonic purity ($0.01 - 0.25$ for clean speech vs $> 0.40$ for white noise/music).
3. **Clipping Ratio**: Percentage of samples at saturation ($\ge 0.98$). Rejects clipped audio.
4. **Energy RMS**: Minimum RMS threshold ($\ge 0.015$) to reject silence.

### 3. Composite Quality Score Equation
$$\text{Score} = (0.4 \times \text{SNR}_{\text{norm}}) + (0.3 \times \text{Flatness}_{\text{penalty}}) + (0.2 \times \text{Clipping}_{\text{penalty}}) + (0.1 \times \text{RMS}_{\text{norm}})$$

Selected reference segment produces highest score ($0.0 - 1.0$).

# Human Voice Evaluation & A/B Listening Test Protocol

## Human Evaluation Status: NOT YET HUMAN EVALUATED

> [!IMPORTANT]
> Numerical perceptual ratings (e.g. 4.2/5) are NOT reported prior to executing formal human listening trials with native listeners. Heuristic or simulated scores are explicitly prohibited.

---

## Formal Human Listening Test Protocol

### 1. Test Setup & Methodology
- **Listener Cohort**: Minimum 10 native Finnish speakers (fluent in spoken Finnish).
- **Test Methodology**: Double-blind A/B listening test.
- **Audio Material**: A/B sample package generated in `ab_test_samples/` (`sample_A_original_actor.wav`, `sample_B_neural_clone.wav` or `sample_B_NEURAL_CLONE_UNAVAILABLE.wav`, `sample_C_edge_tts.wav`, `sample_D_duration_matched.wav`).
- **Presentation Order**: Randomized order per listener.

### 2. Evaluation Dimensions (Scale 1–5)

| Dimension | Description | Scale (1–5) |
|-----------|-------------|-------------|
| **Speaker Identity** | Resemblance to original actor's vocal timbre and pitch | 1 (Different person) – 5 (Same actor) |
| **Naturalness** | Human-like vocal cadence, breath, and absence of robotic artifacts | 1 (Robotic) – 5 (Natural human) |
| **Finnish Pronunciation** | Native Finnish phoneme gemination, vowel harmony, and rhythm | 1 (Unnatural accent) – 5 (Native speaker) |
| **Emotional Similarity** | Preservation of original performance intensity and mood | 1 (Monotone/Flat) – 5 (Matches emotion) |
| **Prosody & Intonation** | Matching phrase-level cadence and sentence stress | 1 (Mismatch) – 5 (Identical cadence) |
| **Intelligibility** | Ease of understanding spoken Finnish words | 1 (Incomprehensible) – 5 (Crystal clear) |
| **Timing Accuracy** | Alignment with original visual speech window | 1 (Noticeable drift) – 5 (Perfect lip-sync) |

### 3. Aggregation & Acceptance Gate
- Ratings are aggregated via arithmetic mean across all listeners.
- **Acceptance Criterion**: Neural clone (Sample B) must achieve a mean **Speaker Identity score $\ge 3.8 / 5.0$** and **Naturalness score $\ge 4.0 / 5.0$** to pass production quality gates.

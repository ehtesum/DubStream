# Spoken Finnish Dialogue Evaluation

## Rule Test Corpus Pass Rate: 100% (8/8 Corpus Rules Verified)

> [!NOTE]
> Rule test corpus pass rate measures unit-test correctness across defined grammatical transformation rules (`translation/finnish.py`). It does NOT claim global coverage across all conversational Finnish dialects without native speaker validation.

---

## Test Corpus Rule Verification Matrix (`translation/finnish.py`)

| Input Phrasing (Textbook Formal) | Puhekieli Rewriting | Semantic Preservation | Rule Status |
|-----------------------------------|---------------------|-----------------------|-------------|
| "Minä olen iloinen." | "Mä oon iloinen." | 100% | **PASS** |
| "Sinä olet ystäväni." | "Sä oot ystäväni." | 100% | **PASS** |
| "Hän on kotona." | "Se on kotona." | 100% | **PASS** |
| "Me olemme lähdössä." | "Me ollaan lähdössä." | 100% | **PASS** |
| "Anteeksi todella paljon." | "Sori todella paljon." | 100% | **PASS** |
| "Onko tämä sinun autosi?" | "Onks tämä sun auto?" | 100% | **PASS** |
| "Minun mielestäni tämä käy." | "Mun mielestä tämä käy." | 100% | **PASS** |
| "Ei mitään hätää." | "Ei mitää hätää." | 100% | **PASS** |

## Evaluation Categories
1. **Rule Test Corpus Pass Rate**: `100% (8/8)` — All defined pronoun, verb, and phrase contraction rules produce expected spoken Finnish dialogue (`puhekieli`).
2. **Semantic Preservation**: `100%` — Core intent and character register preserved across transformations.
3. **Character Style Integration**: Supports `formality` (0.0 = casual, 1.0 = formal) and `slang_level` (0.0 = none, 1.0 = heavy slang) parameters in `DialogueRewriter`.

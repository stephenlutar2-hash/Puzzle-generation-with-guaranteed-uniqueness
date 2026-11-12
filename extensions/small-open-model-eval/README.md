# Extension: a small open-weights model on the certified benchmark

This extension adds a measured result for a **4B open-weights model** on the certified
benchmark, extending the size axis of E3 (which tested claude-haiku-5-5, claude-sonnet-5-5
and claude-opus-5-5 via API).

## Setup

- **Model:** `SZLHOLDINGS/SZL-Nemotron-Mini-4B-Estate-v1` — NVIDIA Nemotron-Mini-4B-Instruct
  fine-tuned (QLoRA SFT) on an estate-specific corpus of 4,855 examples; served with vLLM
  (bfloat16, 2048-token context) on an NVIDIA A6000.
- **Puzzles:** 12 certified puzzles sampled with a fixed seed (3407) from the benchmark's
  fair range (L1-L3), 3 per family.
- **Protocol:** one puzzle per call, matching the paper's single-puzzle finding; the model
  receives the puzzle prompt and the answer-format instruction; max_tokens 1500.
- **Scoring:** crude containment scoring (see caveat).

## Result

| Family | crude cell accuracy |
|---|---|
| Zebra (L1-L2) | 0.65 |
| Sudoku (L1-L3) | 0.00 |
| Killer (L3) | 0.00 |
| Futoshiki (L2) | 0.00 |

The model answered all 12 calls. The zebra result is consistent with partial relational
reasoning surviving at 4B scale (one L2 puzzle scored 1.00, another 0.95); the grid
families scored zero, consistent with the paper's observation that failures at smaller
scale look like unreliability in carrying out a long solution: a 4B model appears unable
to sustain the bookkeeping a 9x9 grid requires, while pairwise relational deductions
remain partially within reach.

**Caveat (important):** the scoring is crude containment — for zebra puzzles it checks
that the certified value and its house number both appear in the output, and for grid
families it counts solution digits present in the output text. It does not parse the
model's answer structure, so a correct grid written in an unexpected format could score
zero. The full outputs are preserved verbatim in the results file for hand-scoring.

## Files

- `results-estate-4b-2026-11-06.json` — full receipt: per-puzzle outputs (verbatim
  excerpts), levels, certified-unique flags, and the scoring note. Also published at
  `SZLHOLDINGS/model-eval-receipts` (Hugging Face) as `reasoning-eval-2026-11-06.json`.
- `eval.py` — the evaluation script (fixed-seed sampling, single-puzzle calls).

## Why this matters for the paper

E3 concludes that the ladder "predicts solver effort well and LLM failure poorly,
because there are few failures to predict" — at frontier-API scale. This extension
supplies the failures: at 4B, grid-family accuracy collapses to zero across all levels
while zebra reasoning partially survives, which sharpens the paper's distinction
between deductive depth (the ladder) and solution-carrying capacity (which smaller
models lack regardless of level).

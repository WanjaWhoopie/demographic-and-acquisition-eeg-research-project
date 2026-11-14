# EXP-043 – Sensitivity: 8-s equal-length representation

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does the result depend on the very different amount of data per participant (ADFSU 8 s, ds004504 up to ~21 min)? The epoch count could itself reveal cohort (D-018).
- **Data:** Z8, each participant's first two clean epochs (8 s); APAVA HC-05 has fewer and is excluded (175 participants).
- **Method:** original vs centring (i) LOCO, refitted with the same nested selection.
- **Outcome:** mean ΔAUROC with CI (D-028 item 5, Holm family).
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`; design committed in 6507313 before the run
- **Command:** `python scripts/09_sensitivity.py` (20 parallel workers). The first attempt stopped before any sensitivity result because the participant ID column was not loaded. It was fixed and re-run in full; the primary numbers were identical.
- **Output:** `results/tables/T09_primary_and_sensitivity.csv`; predictions `results/runs/EXP-043/predictions.csv` (local)

## Results
175 participants (APAVA HC-05 has fewer than two clean epochs).

| Held-out cohort | Original AUROC [95% CI] | Centred AUROC [95% CI] | ΔAUROC [95% CI] |
|---|---|---|---|
| ADFSU | 0.861 [0.744, 0.953] | 0.849 [0.723, 0.946] | +0.013 [−0.003, 0.035] |
| APAVA | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 |
| ds004504 | 0.921 [0.847, 0.979] | 0.918 [0.843, 0.978] | +0.004 [−0.006, 0.016] |
| **Mean over folds** | **0.928 [0.882, 0.963]** | **0.922 [0.875, 0.960]** | **+0.005 [−0.001, 0.014]** |

## Interpretation
- **Pattern A: with equal data per participant, centring changes nothing.** The primary improvement does not survive this sensitivity analysis.
- **The equal-length representation transfers better than the all-data one** (0.928 against 0.853). This was not a pre-specified comparison and is descriptive only (see EXP-040). The likely reason is that unequal epoch counts make participant embeddings differ by cohort; equal length removes that difference at the source, leaving nothing for centring to fix.
- APAVA's AUROC of 1.000 rests on 12 AD and 10 HC and should not be over-read.

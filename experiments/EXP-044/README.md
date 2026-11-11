# EXP-044 – Sensitivity: amplitude-scaled input

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does the result depend on between-cohort amplitude differences (robust SD ~18 µV in ds004504, ~8 µV in ADFSU, ~5 µV in APAVA; D-019)?
- **Method (D-033):** embeddings re-extracted with every participant's clean epochs multiplied by 10 µV / SD, where SD is taken over all of that participant's epochs, channels and samples. All recordings then have the same overall amplitude, inside LaBraM's training range. Pretrained weights; GPU; `04_extract_embeddings.py --amplitude-scaled`, then `05_build_features.py --scaled-only`. Original vs centring (i) LOCO on the scaled representation.
- **Outcome:** mean ΔAUROC with CI (D-028 item 6, Holm family). The scaled representation's own LOCO AUROC is also reported against the unscaled 0.853.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`; design committed in 3e07a74 before the run
- **Command:** `python scripts/09_sensitivity.py` (20 parallel workers). The first attempt stopped before any sensitivity result because the participant ID column was not loaded. It was fixed and re-run in full; the primary numbers were identical.
- **Output:** `results/tables/T09_primary_and_sensitivity.csv`; predictions `results/runs/EXP-044/predictions.csv` (local); embeddings `data/embeddings/labram-base-scaled/` (local, GPU, ~2 min)

## Results
| Held-out cohort | Original AUROC [95% CI] | Centred AUROC [95% CI] | ΔAUROC [95% CI] |
|---|---|---|---|
| ADFSU | 0.742 [0.556, 0.905] | 0.787 [0.602, 0.939] | −0.046 [−0.157, 0.056] |
| APAVA | 0.939 [0.826, 1.000] | 0.902 [0.757, 1.000] | +0.038 [−0.030, 0.136] |
| ds004504 | 0.903 [0.824, 0.966] | 0.870 [0.773, 0.951] | +0.034 [−0.020, 0.092] |
| **Mean over folds** | **0.861 [0.787, 0.927]** | **0.853 [0.767, 0.925]** | **+0.009 [−0.037, 0.060]** |

## Interpretation
- **Pattern A: with amplitudes equalised, centring makes no detectable difference**, and the fold-level changes point in different directions.
- Equalising amplitude leaves the overall transfer about the same (0.861 against 0.853). It lowers ADFSU (0.742) and raises APAVA and ds004504, so absolute amplitude carries some AD-relevant information in some cohorts and cohort-specific information in others.
- Together with EXP-043, the primary improvement from centring looks like a correction for amplitude and data-amount differences between cohorts, rather than evidence that LaBraM uses cohort information for AD.

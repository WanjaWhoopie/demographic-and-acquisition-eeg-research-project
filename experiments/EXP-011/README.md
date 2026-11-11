# EXP-011 – Leave-one-cohort-out baseline

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1 / O4 reference
- **Question:** Does an AD classifier trained on two cohorts transfer to the third, never-seen cohort?
- **Expected:** lower than within-cohort; this original-representation AUROC is the "before" value of the primary ΔAUROC (D-026).
- **Data:** 3 folds: hold out ds004504, ADFSU or APAVA; train on the other two.
- **Method:** as EXP-010, with inner folds stratified on cohort × diagnosis; nothing (scaler, block, pooling, C) is fitted on the held-out cohort.
- **Metrics:** per-fold AUROC with stratified participant-bootstrap 95% CI; mean over folds with CI (fold-wise resampling); pooled AUROC (secondary); threshold metrics at 0.5.

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/06_baseline.py` (20 parallel workers, ~20 min)
- **Outputs:** `results/tables/T06_within_cohort.csv`, `T06_loco.csv`, `T06_loco_deltas.csv`, `T06_nuisance_baselines.csv`, `T06_selected_configs.csv`; participant predictions in `results/runs/EXP-011/predictions.csv` (local)

## Results
| Held-out cohort | n AD / HC | LaBraM AUROC | 95% CI | Selected | Bal. acc. | Sens. | Spec. |
|---|---|---|---|---|---|---|---|
| ADFSU | 76 / 12 | 0.810 | 0.661–0.938 | block 1, patch-mean, mean, C = 100 | 0.68 | 0.70 | 0.67 |
| APAVA | 12 / 11 | 0.879 | 0.697–1.000 | block 1, patch-mean, median, C = 0.1 | 0.87 | 0.83 | 0.91 |
| ds004504 | 36 / 29 | 0.870 | 0.774–0.952 | block 1, patch-mean, median, C = 0.1 | 0.82 | 0.67 | 0.97 |
| **Mean over folds** | | **0.853** | **0.773–0.922** | | | | |
| Pooled (secondary) | 124 / 52 | 0.788 | 0.719–0.853 | | | | |

## Interpretation
- AD classification **transfers** to unseen cohorts: mean LOCO AUROC 0.85, CI well above 0.5. This is the "before" value for the primary ΔAUROC (EXP-040).
- In all three folds the inner CV chose **block 1**, the first transformer block, i.e. the representation closest to the input spectrum. The cross-cohort AD signal appears to be low-level.
- Pooled AUROC (0.79) is lower than the per-fold mean (0.85): predicted probabilities sit at different levels in different held-out cohorts, so cohorts are mis-calibrated relative to each other even when ranking within a cohort is good. This is itself a cohort effect worth reporting.

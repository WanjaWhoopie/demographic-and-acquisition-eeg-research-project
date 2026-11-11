# EXP-022 – Nonlinear (MLP) probes

## Before running (committed before results were seen)
- **Objective:** O2 · **Question:** Does a nonlinear read-out find more nuisance information than the linear probes?
- **Method:** one hidden layer of 64 units, early stopping on a 20% inner validation split, on the LaBraM configuration most often selected by the corresponding linear probe (selection used the full ds004504 / pooled data, so this is descriptive). Same outer splits (5-fold × 5).
- **Use:** if MLP ≫ linear, linear removal in Phase 8 may leave nonlinearly recoverable information; Phase 8 re-probes the controlled representation with the same MLP (T8.4).

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/07_probes.py`, then `python scripts/07_probes.py --only-mlp` after the D-030 fix (re-runs this experiment alone with the configurations saved by the first run)
- **Outputs:** `results/tables/T07_mlp_probes.csv`
- **Deviation (D-030):** the first run's age MLP had an unscaled target and gave MAE 26.5 years, with predictions from 11 to 176 years. The regression MLP now standardises age within the training fold. The cohort and sex MLP results are identical in both runs. The cohort MLP's early-stopping patience was **not** changed (see below).

## Results
Pretrained LaBraM, on the configuration the linear probe selected most often; same outer splits; 5 repeats.

| Probe | Configuration | MLP (64) | Linear probe (EXP-020/021) | Reference |
|---|---|---|---|---|
| Cohort, balanced accuracy | block 11, patch-mean, mean | 0.640 | 0.879 | chance 0.333 |
| Sex, AUROC | block 12, patch-mean, mean | 0.562 | 0.521 | chance 0.5 |
| Age, MAE in years | block 1, CLS, median | 6.54 | 6.05 | guess the mean 5.71 |

## Interpretation
- **No evidence that a nonlinear read-out finds more nuisance information than the linear probes.** The MLP is lower for cohort, near chance for sex, and worse than guessing the mean for age.
- **Limitation:** this check is weak at these sample sizes. In a diagnostic split, the cohort MLP stopped after 15–40 epochs, before fitting its own training data (training balanced accuracy about 0.76). The pre-registered early-stopping rule therefore makes the MLP a *weaker* detector than the linear probe here. Longer patience raised test accuracy only to about 0.71, still below linear. It was not adopted, because it would be tuning after seeing results.
- **Consequence for Phase 8:** the linear probe is the more sensitive detector of residual cohort information. The MLP re-probe (T8.4) still runs as planned, but its result is read with this limitation.

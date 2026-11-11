# EXP-013 – Nuisance-only and negative-control baselines

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1 (references for interpreting O2–O4)
- **Baselines:**
  1. age + sex → AD within ds004504 (repeated stratified 5-fold × 10, C = 1);
  2. cohort identity (one-hot) → AD on all 176 participants pooled (stratified on cohort × diagnosis, 5-fold × 10, C = 1): how much "AD" a model gets from knowing the cohort's AD prevalence;
  3. untrained (random-weights) LaBraM, same pipeline as EXP-010 and EXP-011: how much comes from the architecture and preprocessing rather than pretraining.
- **Metric:** AUROC with stratified-bootstrap 95% CI.
- **Expected:** (1) modest (sex imbalance, age balanced); (2) well above 0.5 because ADFSU is 86% AD; (3) above chance if spectral power alone drives classification.

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/06_baseline.py` (20 parallel workers, ~20 min)
- **Outputs:** `results/tables/T06_within_cohort.csv`, `T06_loco.csv`, `T06_loco_deltas.csv`, `T06_nuisance_baselines.csv`, `T06_selected_configs.csv`; participant predictions in `results/runs/EXP-011/predictions.csv` (local)

## Results
| Baseline | AUROC | 95% CI |
|---|---|---|
| age + sex → AD (ds004504) | 0.607 | 0.463–0.740 |
| cohort identity → AD (all 176 pooled) | 0.646 | 0.552–0.737 |

| Untrained (random-weights) LaBraM | ds004504 | ADFSU | APAVA |
|---|---|---|---|
| Within-cohort AUROC (mean ± SD) | 0.786 ± 0.030 | 0.779 ± 0.030 | 0.673 ± 0.027 |
| LOCO AUROC [95% CI] | 0.805 [0.692, 0.906] | 0.870 [0.762, 0.954] | 0.841 [0.667, 0.970] |

LOCO mean over folds: random 0.838 [0.759, 0.907]; **pretrained − random = +0.015 [−0.055, 0.090]**.

## Interpretation
- Demographics alone barely predict AD in ds004504 (CI includes 0.5), consistent with age being balanced; the sex imbalance gives a weak signal.
- Knowing only the cohort gives AUROC 0.65 on pooled data, because the cohorts' AD prevalence differs (ADFSU 86%). This is the size of the "shortcut" available to any model that recognises the cohort in pooled analyses; LOCO removes it by construction.
- **An untrained LaBraM already reaches most of the pretrained model's performance**, and across cohorts the difference is not distinguishable from zero. Pretraining helps within cohorts (+0.04 to +0.15) but adds little to cross-cohort transfer. Random networks preserve spectral information of the input, so this agrees with EXP-011/012: the transferable signal is largely low-level spectral content.

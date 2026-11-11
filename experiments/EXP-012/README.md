# EXP-012 – Classical comparator

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1
- **Question:** Do LaBraM representations beat classical spectral features?
- **Features:** 16 channels × relative power in delta/theta/alpha/beta (64) + 16 aperiodic exponents (specparam fixed mode, 2–30 Hz; fits with R² < 0.9 set missing (476/2816, more often in HC) and imputed with the training-set median).
- **Method:** same splits, same classifier, C chosen by inner CV; within-cohort (EXP-010 splits) and LOCO (EXP-011 folds).
- **Metric:** AUROC; LaBraM − classical ΔAUROC per LOCO fold (paired bootstrap) and mean over folds. Reported with CIs, not hypothesis-tested (D-028).

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/06_baseline.py` (20 parallel workers, ~20 min)
- **Outputs:** `results/tables/T06_within_cohort.csv`, `T06_loco.csv`, `T06_loco_deltas.csv`, `T06_nuisance_baselines.csv`, `T06_selected_configs.csv`; participant predictions in `results/runs/EXP-011/predictions.csv` (local)

## Results
| | ds004504 | ADFSU | APAVA |
|---|---|---|---|
| Within-cohort AUROC, classical (mean ± SD) | 0.821 ± 0.020 | 0.877 ± 0.036 | 0.817 ± 0.019 |
| Within-cohort AUROC, LaBraM | 0.821 ± 0.030 | 0.925 ± 0.043 | 0.821 ± 0.040 |
| LOCO AUROC, classical [95% CI] | 0.867 [0.767, 0.947] | 0.939 [0.872, 0.986] | 0.894 [0.727, 1.000] |
| LOCO AUROC, LaBraM | 0.870 | 0.810 | 0.879 |
| **LOCO ΔAUROC LaBraM − classical** [paired 95% CI] | +0.003 [−0.057, 0.053] | **−0.128 [−0.253, −0.019]** | −0.015 [−0.068, 0.023] |

Mean over folds: classical 0.900 [0.832, 0.956]; **LaBraM − classical = −0.047 [−0.096, −0.004]**. Pooled (secondary): classical 0.929.

## Interpretation
- Within cohorts LaBraM matches the classical features (ds004504, APAVA) or does a little better (ADFSU).
- **Across cohorts, classical spectral features transfer at least as well as LaBraM, and better on average** (CI of the mean difference just excludes 0), driven by the ADFSU fold. ADFSU is the cohort recorded most differently (1990s, 128 Hz, band-limited and cleaned at source, 8 s per person).
- Reported with CIs, not hypothesis-tested (D-028). It sets the context for the primary question: if LaBraM's transferable AD signal is largely spectral, removing cohort information may change it little or a lot depending on how entangled spectral shape and cohort are (EXP-003: cohort is 0.69-decodable from spectral shape).

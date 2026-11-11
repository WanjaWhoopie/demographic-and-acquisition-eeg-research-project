# EXP-030 – Age and sex residualisation (ds004504)

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O3 · **Question:** Does removing the linear effect of age and sex from Z change within-cohort AD classification in ds004504?
- **Expected:** little change. EXP-020 found no decodable age or sex information, so there is little to remove; a ΔAUROC near 0 is the expected result. A clear drop would mean the classifier relied on age/sex-linked directions that the probes were too weak to detect.
- **Data:** ds004504, 36 AD / 29 HC (the only cohort with age and sex).
- **Method:** within each training fold, OLS per embedding dimension Z_d ~ age + sex (intercept, centred covariates, sex 0/1); the covariate-explained part is subtracted from training and test participants using their own age/sex (T8.1.1–T8.1.2). The residualiser is refitted inside every inner fold of the nested selection (D-031). Two versions: **resid_all**, fitted on all training participants (primary for this experiment), and **resid_hc**, fitted on training HC only (normative, T8.1.4). Same splits and seeds as EXP-010 (5-fold × 10 repeats); the uncontrolled classifier is re-run in the same script as the paired reference and must reproduce EXP-010.
- **Metrics:** ΔAUROC = AUROC(Z) − AUROC(Z\*), paired stratified bootstrap (2000) on repeat-averaged probabilities; mean ± SD over repeats of the per-repeat ΔAUROC. resid_all ΔAUROC is item 4 of the Holm family (D-028).
- **Verification (T8.1.5):** age (ridge, α = 10) and sex (logistic, C = 1) probes, linear and MLP, with and without residualisation, on the configuration the AD classifier chose most often (descriptive).
- **Script:** `scripts/08_control.py` → `results/tables/T08_demographic.csv`, `T08_verification_probes.csv`

## Run record
- **Date:** 2026-11-11 · same run as EXP-031 (`python scripts/08_control.py`)
- **Reproduction check:** the uncontrolled re-run reproduces EXP-010 for ds004504 exactly (0.821 ± 0.030).
- **Outputs:** `results/tables/T08_demographic.csv`, `T08_verification_probes.csv`

## Results
ds004504, 5-fold × 10 repeats. ΔAUROC = original − residualised, from a paired bootstrap on repeat-averaged probabilities.

| Representation | AUROC (mean ± SD over repeats) | ΔAUROC [95% CI] | Per-repeat ΔAUROC (mean ± SD) |
|---|---|---|---|
| Original | 0.821 ± 0.030 | – | – |
| Residualised on all training participants (primary) | 0.775 ± 0.019 | +0.042 [−0.026, 0.118] | +0.046 ± 0.034 |
| Residualised on training HC only (T8.1.4) | 0.811 ± 0.020 | −0.004 [−0.042, 0.035] | +0.010 ± 0.020 |

**Verification (T8.1.5).** Linear probes on the configuration the AD classifier chose most often, 5-fold × 5:

| Probe | Original | Residualised (all) | Residualised (HC only) | Reference |
|---|---|---|---|---|
| Age, MAE in years | 6.29 | 5.71 | **3.41** | guess the mean: 5.71 |
| Sex, AUROC | 0.463 | 0.500 | **0.902** | chance: 0.5 |

## Interpretation
- **Removing age and sex did not significantly change AD classification**: the CI includes 0. The point estimate is a drop of 0.04. A plausible reason, not tested, is that sex is imbalanced by diagnosis here (67% female in AD, 38% in HC), so a sex direction estimated in this sample also carries some AD signal.
- After residualising on all training participants, age and sex are at chance, as intended.
- **The HC-only version is not a valid control at this sample size: it *adds* age and sex information.** After it, sex is decodable at AUROC 0.90, and age is predicted to within 3.4 years against 5.7 by guessing. With only about 23 healthy controls per training fold, the 200 × 2 coefficients are noisy, so subtracting them writes each person's own age and sex into every dimension. Its ΔAUROC is reported as planned, but it does not measure removal of age or sex. This is a methodological caution for the final report.

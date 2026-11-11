# EXP-020 – Age and sex probes (ds004504)

## Before running (committed before results were seen)
- **Objective:** O2 · **Question:** Can age and sex be read out of the frozen LaBraM representation?
- **Data:** ds004504 only (the only cohort with demographics): all 65, HC only (29) for age, and AD-only / HC-only for sex (sex is imbalanced by diagnosis: 24/36 vs 11/29 female).
- **Method:** nested selection as the AD classifier (D-024): block × token × pooling × hyperparameter chosen on inner folds of the training participants. Age: ridge, MAE and R² against "predict the training mean". Sex: class-weighted logistic regression, AUROC and balanced accuracy. Outer stratified 5-fold × 10 repeats. Permutation tests for the pretrained model on all 65: 1000 (age) / 200 (sex) label shuffles through the full nested pipeline on one split each (D-029).
- **References:** same probes on random-weights LaBraM and on classical features.
- **Expected:** age decodable above baseline (EEG changes with age); sex partly decodable (Jochmann et al., 2023, ~81% with a CNN on 1140 patients; far fewer people here). Within AD-only / HC-only the sex probe tells whether sex information exists apart from the diagnosis–sex imbalance.
- **Script:** `scripts/07_probes.py` → `results/tables/T07_age_sex_probes.csv`, `T07_permutation_tests.csv`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/07_probes.py` (20 parallel workers, ~3 h 10 min in total for Phase 7; the permutation tests take most of it)
- **Outputs:** `results/tables/T07_age_sex_probes.csv`, `T07_permutation_tests.csv`, `T07_selected_configs.csv`

## Results
Age in ds004504: mean 67.1 years, SD 6.8, range 49–79. Mean over 10 repeats of 5-fold CV.

| Age probe (MAE in years, lower is better) | Pretrained LaBraM | Random LaBraM | Classical | Guess the training mean |
|---|---|---|---|---|
| All 65 | 6.05 (R² −0.15) | 6.16 (R² −0.20) | 5.77 (R² −0.02) | 5.71 |
| HC only (29) | 5.85 (R² −0.76) | 5.27 (R² −0.38) | 4.97 (R² −0.32) | 4.66 |

| Sex probe (AUROC [95% CI]) | Pretrained LaBraM | Random LaBraM | Classical |
|---|---|---|---|
| All 65 (35 F) | 0.521 [0.375, 0.661] | 0.536 [0.390, 0.674] | 0.530 [0.390, 0.667] |
| HC only (29, 11 F) | 0.500 [0.273, 0.737] | 0.571 [0.333, 0.788] | 0.434 [0.222, 0.677] |
| AD only (36, 24 F) | 0.340 [0.139, 0.563] | 0.524 [0.330, 0.715] | 0.344 [0.160, 0.549] |

Permutation tests, pretrained LaBraM, all 65 (full nested pipeline on one 5-fold split per permutation, D-029):

| Probe | Observed | Null mean | Null 95th percentile | Permutations | p |
|---|---|---|---|---|---|
| Age (−MAE) | −5.88 | −6.23 | −5.60 | 1000 | 0.21 |
| Sex (AUROC) | 0.571 | 0.500 | 0.623 | 200 | 0.21 |

## Interpretation
- **Neither age nor sex can be read out of the LaBraM representation in ds004504.** Every age probe is worse than predicting the training mean, every sex CI contains 0.5, and both permutation tests give p ≈ 0.21. The same holds for random-weights LaBraM and for classical features.
- The pre-registered expectation (age decodable) is **not met**. The test is weak: 65 people with an age SD of under 7 years, against EEG-age studies that use hundreds to thousands of people over decades of age. The result says "no detectable age or sex information at this sample size", not "none present".
- The below-chance sex AUROCs within AD only (0.34) have CIs reaching 0.56. Below-chance scores are a known small-sample cross-validation artefact when there is no signal, not evidence of reversed information.
- **Consequence for Phase 8:** age/sex residualisation (EXP-030, D-028 item 4) has little to remove, so a near-zero ΔAUROC there is expected. It still runs as planned.

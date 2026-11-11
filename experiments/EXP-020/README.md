# EXP-020 – Age and sex probes (ds004504)

## Before running (committed before results were seen)
- **Objective:** O2 · **Question:** Can age and sex be read out of the frozen LaBraM representation?
- **Data:** ds004504 only (the only cohort with demographics): all 65, HC only (29) for age, and AD-only / HC-only for sex (sex is imbalanced by diagnosis: 24/36 vs 11/29 female).
- **Method:** nested selection as the AD classifier (D-024): block × token × pooling × hyperparameter chosen on inner folds of the training participants. Age: ridge, MAE and R² against "predict the training mean". Sex: class-weighted logistic regression, AUROC and balanced accuracy. Outer stratified 5-fold × 10 repeats. Permutation tests for the pretrained model on all 65: 1000 (age) / 200 (sex) label shuffles through the full nested pipeline on one split each (D-029).
- **References:** same probes on random-weights LaBraM and on classical features.
- **Expected:** age decodable above baseline (EEG changes with age); sex partly decodable (Jochmann et al., 2023, ~81% with a CNN on 1140 patients; far fewer people here). Within AD-only / HC-only the sex probe tells whether sex information exists apart from the diagnosis–sex imbalance.
- **Script:** `scripts/07_probes.py` → `results/tables/T07_age_sex_probes.csv`, `T07_permutation_tests.csv`

# EXP-021 – Cohort probe

## Before running (committed before results were seen)
- **Objective:** O2 · **Question:** How well can the cohort (recording site/system) be read out of the representation?
- **Data:** all 176 participants, three cohorts; chance balanced accuracy 1/3.
- **Method:** class-weighted multinomial logistic regression with nested selection (D-024), outer stratified (cohort × diagnosis) 5-fold × 5; balanced accuracy, macro-F1, confusion matrix. Layer profile: the same probe per block (patch-mean token, mean pooling, C = 1), descriptive.
- **Reference values:** classical spectral features 0.687 (EXP-003, pre-registered as the floor); random-weights LaBraM.
- **Interpretation rule:** LaBraM ≫ 0.69 → the model encodes acquisition information beyond what spectral shape carries; ≈ 0.69 → the cohort signal is spectral and visible to any method.
- **Script:** `scripts/07_probes.py` → `results/tables/T07_cohort_probe.csv`, `T07_cohort_confusion.csv`, `T07_cohort_layer_profile.csv`, `results/figures/EXP-021_layer_profile.png`

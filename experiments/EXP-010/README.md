# EXP-010 – Within-cohort baseline

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1
- **Question:** How well do frozen LaBraM representations separate AD from HC *within* each cohort?
- **Expected:** above chance in every cohort (published within-dataset LaBraM dementia AUROC ≈ 0.89, Lin, Hou & Jung 2026, nonlinear read-out); ADFSU less certain (8 s per person, 12 HC).
- **Data:** each cohort separately; all clean epochs (D-018); ds004504 36/29, ADFSU 76/12, APAVA 12/11.
- **Representation:** frozen LaBraM-base; block × token × pooling chosen inside training folds (D-024).
- **Method:** participant-stratified 5-fold × 10 repeats (seed 20261001); inside each training fold an inner stratified 5-fold picks (block, token, pooling, C) by AUROC; class-weighted L2 logistic regression with standardisation (D-006).
- **Metrics:** AUROC (primary; mean ± SD over repeats and stratified-bootstrap 95% CI on repeat-averaged probabilities), PR-AUC, balanced accuracy / sensitivity / specificity / F1 at 0.5 (D-025).
- **Config:** `configs/analysis.yaml` · **Script:** `scripts/06_baseline.py`
- **What would change our plan?** A cohort at chance would make its LOCO fold uninformative about nuisance removal.

# EXP-011 – Leave-one-cohort-out baseline

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1 / O4 reference
- **Question:** Does an AD classifier trained on two cohorts transfer to the third, never-seen cohort?
- **Expected:** lower than within-cohort; this original-representation AUROC is the "before" value of the primary ΔAUROC (D-026).
- **Data:** 3 folds: hold out ds004504, ADFSU or APAVA; train on the other two.
- **Method:** as EXP-010, with inner folds stratified on cohort × diagnosis; nothing (scaler, block, pooling, C) is fitted on the held-out cohort.
- **Metrics:** per-fold AUROC with stratified participant-bootstrap 95% CI; mean over folds with CI (fold-wise resampling); pooled AUROC (secondary); threshold metrics at 0.5.

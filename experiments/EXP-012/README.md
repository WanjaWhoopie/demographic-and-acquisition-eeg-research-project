# EXP-012 – Classical comparator

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1
- **Question:** Do LaBraM representations beat classical spectral features?
- **Features:** 16 channels × relative power in delta/theta/alpha/beta (64) + 16 aperiodic exponents (specparam fixed mode, 2–30 Hz; fits with R² < 0.9 set missing (476/2816, more often in HC) and imputed with the training-set median).
- **Method:** same splits, same classifier, C chosen by inner CV; within-cohort (EXP-010 splits) and LOCO (EXP-011 folds).
- **Metric:** AUROC; LaBraM − classical ΔAUROC per LOCO fold (paired bootstrap) and mean over folds. Reported with CIs, not hypothesis-tested (D-028).

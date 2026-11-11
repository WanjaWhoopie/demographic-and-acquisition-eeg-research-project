# EXP-031 – Prevalence-balanced cohort centring (LOCO) – primary controlled representation

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O3 / O4 · **Question:** Does removing each cohort's mean (prevalence-balanced) change how well the AD classifier transfers to a held-out cohort?
- **Data:** all 176 participants; 3 LOCO folds (hold out ds004504, ADFSU or APAVA).
- **Method (T8.2, D-026, D-031):** inside each training fold, for every training cohort c, μ_c = ½(mean of AD + mean of HC) from training labels, subtracted from that cohort's participants. Held-out cohort: **variant (i)** subtracts the pooled training mean (mean of the μ_c), using no test data (**primary**, D-026); **variant (ii)** subtracts the unweighted mean of the held-out cohort's own embeddings without labels (transductive, secondary, D-028 item 1). Centring is refitted inside every inner fold of the nested selection, so block/token/pooling/C may differ from EXP-011. The uncontrolled classifier is re-run in the same script as the paired reference and must reproduce EXP-011.
- **Metrics:** per-fold AUROC with bootstrap CI; per-fold paired ΔAUROC = AUROC(Z) − AUROC(Z\*); **mean ΔAUROC over the 3 folds with CI (primary outcome, D-026)**. Pattern A/B/C (D-027) is assigned in Phase 9 (EXP-040) from these predictions.
- **Expected:** EXP-021 shows strong cohort information in LaBraM (0.88), concentrated in deeper blocks, while the LOCO classifier chose block 1. Centring removes mean offsets only, so cohort information in the covariance remains. Our prior is a small change (pattern A or B); we do not have a directional prediction strong enough to state.
- **Verification (T8.4):** cohort probes on the centred representation (see EXP-032).
- **Script:** `scripts/08_control.py` → `results/tables/T08_loco.csv`, `T08_loco_deltas.csv`; predictions `results/runs/EXP-031/predictions.csv` (local)

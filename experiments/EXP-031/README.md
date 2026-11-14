# EXP-031 – Prevalence-balanced cohort centring (LOCO) – primary controlled representation

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O3 / O4 · **Question:** Does removing each cohort's mean (prevalence-balanced) change how well the AD classifier transfers to a held-out cohort?
- **Data:** all 176 participants; 3 LOCO folds (hold out ds004504, ADFSU or APAVA).
- **Method (T8.2, D-026, D-031):** inside each training fold, for every training cohort c, μ_c = ½(mean of AD + mean of HC) from training labels, subtracted from that cohort's participants. Held-out cohort: **variant (i)** subtracts the pooled training mean (mean of the μ_c), using no test data (**primary**, D-026); **variant (ii)** subtracts the unweighted mean of the held-out cohort's own embeddings without labels (transductive, secondary, D-028 item 1). Centring is refitted inside every inner fold of the nested selection, so block/token/pooling/C may differ from EXP-011. The uncontrolled classifier is re-run in the same script as the paired reference and must reproduce EXP-011.
- **Metrics:** per-fold AUROC with bootstrap CI; per-fold paired ΔAUROC = AUROC(Z) − AUROC(Z\*); **mean ΔAUROC over the 3 folds with CI (primary outcome, D-026)**. Pattern A/B/C (D-027) is assigned in Phase 9 (EXP-040) from these predictions.
- **Expected:** EXP-021 shows strong cohort information in LaBraM (0.88), concentrated in deeper blocks, while the LOCO classifier chose block 1. Centring removes mean offsets only, so cohort information in the covariance remains. Our prior is a small change (pattern A or B); we do not have a directional prediction strong enough to state.
- **Verification (T8.4):** cohort probes on the centred representation (see EXP-032).
- **Script:** `scripts/08_control.py` → `results/tables/T08_loco.csv`, `T08_loco_deltas.csv`; predictions `results/runs/EXP-031/predictions.csv` (local)

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`; design committed in 4f996cf and D-032 in f8bba2e, both before this run
- **Command:** `python scripts/08_control.py` (20 parallel workers, about 45 min for all of Phase 8)
- **Reproduction check:** the uncontrolled re-run reproduces EXP-011 exactly (0.810 / 0.879 / 0.870; mean 0.853).
- **Outputs:** `results/tables/T08_loco.csv`, `T08_loco_deltas.csv`; predictions `results/runs/EXP-031/predictions.csv` (local)

## Results
ΔAUROC = AUROC(original) − AUROC(centred). A negative value means centring *improved* transfer.

| Held-out cohort | Original AUROC [95% CI] | Centred, variant (i) | ΔAUROC [95% CI] | Configuration chosen after centring |
|---|---|---|---|---|
| ADFSU | 0.810 [0.661, 0.938] | 0.855 [0.726, 0.959] | −0.045 [−0.136, 0.039] | block 11, CLS, mean, C = 100 |
| APAVA | 0.879 [0.697, 1.000] | 0.879 [0.697, 1.000] | 0.000 | block 1, patch-mean, median, C = 0.1 (unchanged) |
| ds004504 | 0.870 [0.774, 0.952] | 0.926 [0.853, 0.980] | −0.057 [−0.113, −0.012] | block 12, patch-mean, median, C = 100 |
| **Mean over folds** | **0.853 [0.773, 0.922]** | **0.887 [0.812, 0.951]** | **−0.034 [−0.069, −0.001]** | |

- Variant (ii) gives identical AUROCs, as D-032 predicted. Its threshold metrics differ: ADFSU balanced accuracy is 0.71 under (ii) and 0.83 under (i).
- Threshold metrics at 0.5 improve under variant (i). ADFSU balanced accuracy rises from 0.68 to 0.83, and ds004504 from 0.82 to 0.88.
- In the APAVA fold the centred classifier chose the same configuration as the original. Its predictions changed slightly (Spearman 0.995 with the original), but no AD–HC ordering changed.

## Interpretation
- **Primary outcome: centring did not hurt cross-cohort transfer. It improved it slightly**, from 0.853 to 0.887 mean AUROC. The 95% CI of ΔAUROC excludes 0, but its upper limit is close to 0 (−0.001). Under D-027 this is the pre-specified "significantly negative ΔAUROC" outcome, reported on its own rather than as pattern A, B or C. The formal classification and the sensitivity analyses follow in Phase 9 (EXP-040).
- **Cohort offsets were an obstacle, not a shortcut.** Without control the classifier used block 1, which carries the least cohort information (EXP-021). After centring it chose deep blocks (11–12) in two of the three folds. Those blocks are among the most cohort-laden (0.86–0.87, against 0.71 at block 1) and, it now appears, transferable AD information once the offsets are removed.
- Centring removes cohort *means*, not all cohort information; verification probes still decode cohort above chance (EXP-032). The result therefore shows that the AD signal LaBraM transfers does not depend on cohort mean offsets. It does not show that no cohort information is used.
- Descriptively, centred LaBraM (0.887) is now close to classical features (0.900 [0.832, 0.956], EXP-012). That difference was not tested.

## Revision after EXP-055 (14 November 2026)
Holding the block fixed (EXP-055) shows that deep blocks transfer better than block 1 with or without control (original block 11: 0.908 vs 0.853), and that removal at a fixed block never improves transfer with a CI below 0. The gain reported above came from the change of selected block, not from the removal. "Obstacle, not shortcut" is narrowed to: cohort offsets were an obstacle to the inner CV *selecting* deep blocks, not to those blocks transferring.

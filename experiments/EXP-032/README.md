# EXP-032 – Linear erasure of cohort: LEACE and INLP (LOCO)

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O3 / O4 · **Question:** Do linear concept erasers that remove cohort information change LOCO AD performance, and do they remove the cohort signal that the probes found?
- **Data:** as EXP-031.
- **Method (T8.3, D-031):**
  - **LEACE** (Belrose et al., 2023; `concept-erasure` 0.2.4, float64, default shrinkage): fitted on training participants with the training cohort as a one-hot concept, applied to training and held-out participants.
  - **INLP** (Ravfogel et al., 2020): 20 iterations of a class-weighted L2 logistic cohort classifier (C = 1) on standardised training features, each direction projected out; the final projection is applied to held-out participants. With two training cohorts this removes 20 of 200 dimensions.
  - Both are refitted inside every inner fold of the nested selection.
- **Metrics:** as EXP-031: per-fold and mean ΔAUROC with CIs. LEACE and INLP ΔAUROC are items 2 and 3 of the Holm family (D-028).
- **Verification (T8.4, descriptive):** cohort probes, linear (logistic C = 1) and MLP (64), stratified 5-fold × 5, with the control fitted on the probe's training rows only: (a) inside each LOCO training set (two cohorts, chance 0.5) on the configuration the AD classifier chose; (b) on all 176 participants (three cohorts, chance 1/3) on block 11 / patch-mean / mean pooling, the EXP-021 configuration, against its uncontrolled value. A linear probe should fall towards chance after LEACE; the MLP is the informative check, read with the underfitting limitation found in EXP-022.
- **Expected:** LEACE and INLP remove linearly decodable cohort information on training data by construction. Whether that information carries over to the held-out cohort, and whether AD transfer changes, is the open question.
- **Script:** `scripts/08_control.py` → `results/tables/T08_loco.csv`, `T08_loco_deltas.csv`, `T08_verification_probes.csv`

## Run record
- **Date:** 2026-11-11 · same run as EXP-031 (`python scripts/08_control.py`)
- **Outputs:** `results/tables/T08_loco.csv`, `T08_loco_deltas.csv`, `T08_verification_probes.csv`

## Results
ΔAUROC = AUROC(original) − AUROC(erased). A negative value means erasure improved transfer. Holm correction is applied in Phase 10.

| Held-out cohort | Original | LEACE | ΔAUROC LEACE [95% CI] | INLP | ΔAUROC INLP [95% CI] |
|---|---|---|---|---|---|
| ADFSU | 0.810 | 0.841 | −0.031 [−0.131, 0.061] | 0.871 | −0.060 [−0.166, 0.037] |
| APAVA | 0.879 | 0.939 | −0.061 [−0.167, 0.008] | 0.902 | −0.023 [−0.091, 0.008] |
| ds004504 | 0.870 | 0.869 | +0.001 [−0.076, 0.073] | 0.856 | +0.013 [−0.058, 0.085] |
| **Mean over folds** | **0.853** | **0.883 [0.820, 0.936]** | **−0.030 [−0.081, 0.016]** | **0.876 [0.809, 0.935]** | **−0.023 [−0.071, 0.020]** |

**Verification of removal (T8.4).** Cohort balanced accuracy, mean over 5 repeats of 5-fold CV:

| Check | Probe | None | Centring (i) | LEACE | INLP | Chance |
|---|---|---|---|---|---|---|
| LOCO training set, ADFSU held out | linear | 0.839 | 0.566 | 0.500 | 0.582 | 0.5 |
| LOCO training set, APAVA held out | linear | 0.893 | 0.876 | 0.500 | 0.573 | 0.5 |
| LOCO training set, ds004504 held out | linear | 0.777 | 0.829 | 0.500 | 0.608 | 0.5 |
| Same three folds | MLP (64) | 0.55–0.73 | 0.54–0.65 | 0.53–0.57 | 0.54–0.56 | 0.5 |
| All 176, block 11 configuration (EXP-021) | linear | 0.875 | 0.652 | 0.333 | 0.433 | 0.333 |
| All 176, block 11 configuration | MLP (64) | 0.640 | 0.511 | 0.408 | 0.391 | 0.333 |

In the LOCO training-set rows, each control is probed on the configuration its own AD classifier chose, so the columns are not all on the same block.

## Interpretation
- **Neither linear eraser reduced cross-cohort AD performance.** Both point estimates are improvements of about the same size as centring, and both CIs include 0.
- **LEACE removed linear cohort information completely**, including on held-out rows of the verification CV (exactly 0.500 and 0.333). The AD classifier still transferred at 0.883. The linear cohort information in LaBraM is therefore not what carries its cross-cohort AD performance.
- INLP with a fixed 20 iterations removed most, but not all, linear cohort information (0.57–0.61 left in the LOCO training sets).
- Centring removes mean offsets but leaves cohort decodable from the remaining structure; linear probes still read 0.83–0.88 in two of the three LOCO training sets. It is a weaker control than LEACE, yet all three controls move AUROC in the same direction.
- After LEACE the MLP finds little (0.53–0.57). The EXP-022 limitation applies: the MLP is a weak detector at this sample size, so nonlinear cohort information cannot be ruled out.

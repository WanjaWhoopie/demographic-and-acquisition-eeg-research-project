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

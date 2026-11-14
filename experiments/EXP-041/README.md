# EXP-041 – Sensitivity: without ADFSU

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Is the primary result driven by ADFSU, the cohort recorded most differently with 86% AD?
- **Data:** ds004504 and APAVA only; 2 LOCO folds (train on one, test on the other).
- **Method:** as EXP-040, refitted.
- **Known before running (D-033):** each fold has a single training cohort. Centring then subtracts one constant vector from all training and all test participants, and the classifier's standardisation removes it exactly. ΔAUROC is therefore 0 by construction, and LEACE/INLP have no concept to erase. The run confirms the identity. **This analysis cannot test cohort control.** It reports how well the original representation transfers between the two remaining cohorts. Holm-family item 7 (D-028) is recorded as not estimable.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`; design committed in 6507313 before the run
- **Command:** `python scripts/09_sensitivity.py` (20 parallel workers). The first attempt stopped before any sensitivity result because the participant ID column was not loaded. It was fixed and re-run in full; the primary numbers were identical.
- **Output:** `results/tables/T09_primary_and_sensitivity.csv`; predictions `results/runs/EXP-041/predictions.csv` (local)

## Results
| Held-out cohort (trained on the other) | Original AUROC [95% CI] | Centred AUROC | ΔAUROC |
|---|---|---|---|
| APAVA (trained on ds004504) | 0.864 [0.682, 1.000] | 0.864 | 0.000 |
| ds004504 (trained on APAVA) | 0.884 [0.794, 0.953] | 0.884 | 0.000 |
| **Mean** | **0.874 [0.769, 0.950]** | 0.874 | **0.000** |

The largest difference in any predicted probability was 0.0019. That is solver tolerance, not a change: every AUROC is identical, as D-033 predicted.

## Interpretation
- As recorded before the run, this analysis cannot test cohort control: with one training cohort, centring is cancelled by standardisation. Holm-family item 7 is **not estimable**.
- What it does show: **without ADFSU, LaBraM transfers between ds004504 and APAVA at 0.874**, close to the three-cohort value (0.853). The cross-cohort AD signal is not an ADFSU artefact.

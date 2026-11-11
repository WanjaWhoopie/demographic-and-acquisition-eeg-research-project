# EXP-041 – Sensitivity: without ADFSU

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Is the primary result driven by ADFSU, the cohort recorded most differently with 86% AD?
- **Data:** ds004504 and APAVA only; 2 LOCO folds (train on one, test on the other).
- **Method:** as EXP-040, refitted.
- **Known before running (D-033):** each fold has a single training cohort. Centring then subtracts one constant vector from all training and all test participants, and the classifier's standardisation removes it exactly. ΔAUROC is therefore 0 by construction, and LEACE/INLP have no concept to erase. The run confirms the identity. **This analysis cannot test cohort control.** It reports how well the original representation transfers between the two remaining cohorts. Holm-family item 7 (D-028) is recorded as not estimable.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

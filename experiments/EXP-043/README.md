# EXP-043 – Sensitivity: 8-s equal-length representation

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does the result depend on the very different amount of data per participant (ADFSU 8 s, ds004504 up to ~21 min)? The epoch count could itself reveal cohort (D-018).
- **Data:** Z8, each participant's first two clean epochs (8 s); APAVA HC-05 has fewer and is excluded (175 participants).
- **Method:** original vs centring (i) LOCO, refitted with the same nested selection.
- **Outcome:** mean ΔAUROC with CI (D-028 item 5, Holm family).
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

# EXP-044 – Sensitivity: amplitude-scaled input

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does the result depend on between-cohort amplitude differences (robust SD ~18 µV in ds004504, ~8 µV in ADFSU, ~5 µV in APAVA; D-019)?
- **Method (D-033):** embeddings re-extracted with every participant's clean epochs multiplied by 10 µV / SD, where SD is taken over all of that participant's epochs, channels and samples. All recordings then have the same overall amplitude, inside LaBraM's training range. Pretrained weights; GPU; `04_extract_embeddings.py --amplitude-scaled`, then `05_build_features.py --scaled-only`. Original vs centring (i) LOCO on the scaled representation.
- **Outcome:** mean ΔAUROC with CI (D-028 item 6, Holm family). The scaled representation's own LOCO AUROC is also reported against the unscaled 0.853.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

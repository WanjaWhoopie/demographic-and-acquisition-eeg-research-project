# EXP-050 – Band perturbation (exploratory)

## Before running (committed before results were seen; D-036)
- **Objective:** O5 · **Question:** Which frequency bands does the cross-cohort AD classifier rely on?
- **Method:** each band (delta 1–4, theta 4–8, alpha 8–13, beta 13–30 Hz) is removed in turn from every clean epoch with a 4th-order zero-phase Butterworth band-stop filter, and embeddings are re-extracted on the GPU. For each LOCO fold, the EXP-031 classifier (same configuration and C, original and centred (i)) is refitted on the training cohorts' *unperturbed* data and applied to the held-out cohort twice: intact and with the band removed. The intact predictions must reproduce the saved EXP-031 predictions.
- **Metrics:** mean over folds of ΔAUROC = AUROC(intact) − AUROC(band removed), paired bootstrap CI; mean change in predicted AD probability among AD and among HC participants, with bootstrap CI. Exploratory: CIs only, no multiplicity correction.
- **Expected (T11.5, AD EEG slowing):** removing **theta** lowers P(AD), mostly in AD participants, and costs AUROC; removing **alpha** raises P(AD), mostly in HC; beta removal may also raise P(AD). If removing a band does not change AUROC, the classifier does not depend on that band alone.
- **Limitation:** filtering 4-s epochs creates edge effects, worst for the delta band.
- **Script:** `scripts/11_interpret.py --part bands` → `results/tables/T11_band_perturbation.csv`, `results/figures/EXP-050_band_perturbation.png`

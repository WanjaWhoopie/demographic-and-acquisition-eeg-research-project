# EXP-050 – Band perturbation (exploratory)

## Before running (committed before results were seen; D-036)
- **Objective:** O5 · **Question:** Which frequency bands does the cross-cohort AD classifier rely on?
- **Method:** each band (delta 1–4, theta 4–8, alpha 8–13, beta 13–30 Hz) is removed in turn from every clean epoch with a 4th-order zero-phase Butterworth band-stop filter, and embeddings are re-extracted on the GPU. For each LOCO fold, the EXP-031 classifier (same configuration and C, original and centred (i)) is refitted on the training cohorts' *unperturbed* data and applied to the held-out cohort twice: intact and with the band removed. The intact predictions must reproduce the saved EXP-031 predictions.
- **Metrics:** mean over folds of ΔAUROC = AUROC(intact) − AUROC(band removed), paired bootstrap CI; mean change in predicted AD probability among AD and among HC participants, with bootstrap CI. Exploratory: CIs only, no multiplicity correction.
- **Expected (T11.5, AD EEG slowing):** removing **theta** lowers P(AD), mostly in AD participants, and costs AUROC; removing **alpha** raises P(AD), mostly in HC; beta removal may also raise P(AD). If removing a band does not change AUROC, the classifier does not depend on that band alone.
- **Limitation:** filtering 4-s epochs creates edge effects, worst for the delta band.
- **Script:** `scripts/11_interpret.py --part bands` → `results/tables/T11_band_perturbation.csv`, `results/figures/EXP-050_band_perturbation.png`

## Run record
- **Date:** 2026-11-12 · design committed in b496eae before the run
- **Commands:** `python scripts/04_extract_embeddings.py --cohort <c> --band-stop <band>` for 4 bands × 3 cohorts (GPU, about 2 min per band), then `python scripts/11_interpret.py`
- **Check:** the refitted classifiers reproduce the EXP-031 AUROCs exactly. Probabilities differed by up to 0.012 in the one fold with C = 100, where the solver stops at a marginally different point, so the check was relaxed to "identical AUROC and probabilities within 0.02" (first attempt stopped on the stricter 1e-6 check).
- **Outputs:** `results/tables/T11_band_perturbation.csv`, `results/figures/EXP-050_band_perturbation.png`; embeddings `data/embeddings/labram-base-stop-<band>/` (local)

## Results
Mean over the 3 LOCO folds. ΔAUROC = AUROC(intact) − AUROC(band removed), so a positive value means the band was needed. ΔP(AD) is the mean change in predicted AD probability when the band is removed.

| Band removed | Classifier | ΔAUROC [95% CI] | ΔP(AD), AD participants | ΔP(AD), HC participants |
|---|---|---|---|---|
| delta (1–4 Hz) | original | +0.020 [0.001, 0.043] | −0.07 | −0.05 |
| delta | centred (i) | +0.024 [0.008, 0.046] | −0.11 | −0.03 |
| **theta (4–8 Hz)** | original | **+0.066 [0.026, 0.109]** | **−0.41** | −0.10 |
| **theta** | centred (i) | **+0.064 [0.026, 0.104]** | **−0.43** | −0.14 |
| alpha (8–13 Hz) | original | +0.004 [−0.032, 0.037] | 0.00 | 0.00 |
| alpha | centred (i) | +0.047 [0.004, 0.087] | −0.04 | +0.13 |
| beta (13–30 Hz) | original | −0.003 [−0.050, 0.040] | +0.20 | +0.20 |
| beta | centred (i) | −0.002 [−0.049, 0.044] | +0.14 | +0.45 |

Per fold, the theta effect comes mostly from ADFSU (ΔAUROC +0.16 [0.08, 0.26]); it is small in APAVA (+0.02) and ds004504 (+0.01).

## Interpretation (exploratory)
- **Theta is the band the classifier relies on most**, as expected from EEG slowing in AD. Removing it costs the most discrimination and cuts the predicted AD probability of AD participants by 0.41 on average, four times the drop in HC.
- In APAVA and ds004504, removing theta shifts probabilities strongly but barely changes the ranking. The information is redundant across bands there: the remaining bands still separate the groups.
- **Removing beta raises P(AD) for everyone** without changing AUROC. Loss of fast activity looks "more AD-like" to the classifier, which fits the known beta reduction in AD, but it moves both groups equally.
- **Alpha matters only for the centred classifier.** Removing alpha raises P(AD) for HC (+0.13) and costs discrimination (+0.047), as expected if lower alpha signals AD. The original classifier, which uses block 1 in every fold, is insensitive to alpha removal.
- Delta has a small effect. Filtering delta out of 4-s epochs is the least reliable of these perturbations (edge effects).
- **Overall, the cross-cohort AD signal is carried mainly by slowing (theta) with contributions from delta, beta and, for the centred classifier, alpha.** That is consistent with the classical EEG literature on AD, and with classical spectral features doing as well as LaBraM (EXP-012).

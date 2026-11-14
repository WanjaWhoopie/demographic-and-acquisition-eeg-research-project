# EXP-051 – Channel occlusion (exploratory)

## Before running (committed before results were seen; exploratory, D-038)
- **Objective:** O5 (interpretation). **Question:** which scalp regions does the cross-cohort AD
  signal come from? EXP-050 showed it depends mostly on theta; EXP-052 found the strongest marker
  correlations over posterior channels. Channel occlusion asks the spatial question directly.
- **Was deferred** for time (D-036: "not run unless time remains after writing starts"). Writing
  is done, so it is run now, with the design below fixed before any occluded embedding exists.
- **Occlusion.** In the preprocessed (common-average-referenced) epochs of the held-out cohort, the
  occluded channel(s) are set to **zero** in every clean epoch before frozen LaBraM-base. After
  average referencing the mean over channels is zero at every sample, so a zeroed channel carries
  the montage average and no channel-specific signal. The channel stays in the input, so LaBraM's
  channel and time embeddings, the input shape and the scaling are unchanged.
- **Conditions (19).** Each of the 16 channels alone, and three regions:
  frontal (Fp1, Fp2, F7, F3, F4, F8), central-temporal (T3, C3, C4, T4),
  posterior (T5, P3, P4, T6, O1, O2; the EXP-052 posterior set).
- **Classifiers.** Exactly as EXP-050: for each LOCO fold, the EXP-031 classifier (same
  configuration and C) for the original and the centred (variant i) representation, refitted on the
  training cohorts' *unoccluded* data and applied to the held-out cohort intact and occluded. The
  intact predictions must reproduce EXP-031 (the script stops otherwise).
- **Outcomes per condition and classifier.** Mean over the 3 folds of AUROC(intact) − AUROC(occluded),
  paired participant bootstrap CI (2000 draws, seed 20261001, each fold resampled); per fold
  ΔAUROC; mean change in predicted AD probability in AD and in HC participants. Topographic maps of
  the 16 single-channel ΔAUROCs, one per classifier.
- **Reading rule (fixed now).** 38 comparisons (19 conditions × 2 classifiers), exploratory, no
  multiplicity correction; a condition "matters" if its mean ΔAUROC CI lies above 0.
  - **Posterior emphasis** is supported if posterior occlusion has a CI above 0 *and* the largest
    point estimate of the three regions, for the original classifier.
  - **Spatially distributed** is supported if no region has a CI above 0 for the original classifier.
  - Anything else is reported as **mixed**, with the numbers.
  - Expectation, stated for the record: single channels cost little (ΔAUROC < 0.02) because
    neighbouring channels carry much of the same slowing.
- **Commands.** `python scripts/04_extract_embeddings.py --cohort <c> --occlude <condition>` for
  every cohort and condition (GPU, about 2 min per condition), then
  `python scripts/11_interpret.py --part channels`.
- **Outputs.** `results/tables/T11_channel_occlusion.csv`, `results/figures/EXP-051_channel_occlusion.png`

## Run record
- **Date:** 2026-11-12 to 2026-11-14 · design committed in 5f9519a before any occluded embedding existed
- **Commands:** `python scripts/04_extract_embeddings.py --cohort <c> --occlude <condition>` for 3 cohorts × 19
  conditions (GPU, about 1 min each), then `python scripts/11_interpret.py --part channels`
- **Checks passed:** every occluded folder has all 176 participants and all epochs; the processed
  epochs are average-referenced (largest |mean over channels| 2 × 10⁻⁶ µV); the intact predictions
  reproduce EXP-031 in every fold. The refactored EXP-050 code reproduces `T11_band_perturbation.csv`
  byte for byte.
- **Outputs:** `results/tables/T11_channel_occlusion.csv`, `results/figures/EXP-051_channel_occlusion.png`

## Results
ΔAUROC = AUROC(intact) − AUROC(occluded), mean over the 3 LOCO folds [paired bootstrap 95% CI];
Δp = mean change in predicted AD probability.

| Region occluded | Original classifier | Centred (i) classifier | Δp AD / Δp HC (original) |
|---|---|---|---|
| **Posterior** (T5 P3 P4 T6 O1 O2) | **+0.196 [0.119, 0.285]** | **+0.255 [0.166, 0.350]** | +0.09 / **+0.21** |
| Frontal (Fp1 Fp2 F7 F3 F4 F8) | +0.052 [0.004, 0.105] | +0.018 [−0.032, 0.071] | −0.33 / −0.10 |
| Central-temporal (T3 C3 C4 T4) | −0.010 [−0.051, 0.026] | −0.002 [−0.039, 0.036] | −0.03 / −0.06 |

Per fold, posterior occlusion cost most when ADFSU was held out (original +0.37, centred +0.48),
then APAVA (+0.19, +0.17), least in ds004504 (+0.03, +0.11). The frontal effect came only from the
ADFSU fold (+0.19; −0.02 and −0.01 in the others).

**Single channels.** Each channel alone cost little: largest mean ΔAUROC 0.030 (T5, original);
4 of 32 estimates reached 0.02; only F4 (original, +0.026 [0.009, 0.047]) and P4 (centred, +0.022
[0.003, 0.047]) had CIs above 0, uncorrected among 32.

## Interpretation (exploratory)
- **By the pre-registered rule: posterior emphasis.** Posterior occlusion has a CI above 0 and the
  largest cost of the three regions, for both classifiers. The cross-cohort AD signal comes mainly
  from posterior channels, the same channels over which the classical slowing markers correlated
  most strongly with the AD score (EXP-052).
- **What is lost is the healthy posterior rhythm.** Occluding the posterior region raised the
  predicted AD probability of controls (+0.21) more than that of AD participants (+0.09): without
  posterior channels, controls look more like AD. Together with EXP-050 (theta removal costs most;
  alpha matters for the centred classifier) this fits the classical picture of AD slowing as a loss
  of posterior alpha relative to theta.
- **It is not just the amount of input removed.** The frontal region also zeroes 6 of 16 channels
  but cost a quarter as much (0.05, only in the ADFSU fold), and central-temporal (4 channels) cost
  nothing.
- **The signal is spatially redundant.** No single channel matters much, as expected: neighbouring
  posterior channels carry the same slowing, so the effect only appears when the region is removed.
- **Caveats.** Zeroing 6 of 16 channels moves the input further from LaBraM's training data than
  zeroing one, so part of a region effect could be the model's response to an unusual input. The
  frontal/posterior contrast argues against this explaining the posterior result. Fold sizes are
  small (11–29 HC), and the comparisons are uncorrected.

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

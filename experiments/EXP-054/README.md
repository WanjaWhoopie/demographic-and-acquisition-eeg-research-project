# EXP-054 – Time in recording versus amount of data (exploratory follow-up to EXP-053)

## Before running (committed before results were seen; exploratory and post hoc, D-037)
- **Objective:** O5 (interpretation). **Question:** EXP-053 found that pooling only the *first* few epochs of each recording gave higher AD discrimination than pooling all of them, both across cohorts and within ds004504. Is that because the early part of a recording is more informative (time in recording), or because fewer epochs help whatever their position (amount of data)?
- **Design, two arms, both with the EXP-053 pipeline** (frozen LaBraM-base, nested selection D-024, original representation only, no control):
  1. **Position at fixed amount.** Each participant is represented by 8 consecutive clean epochs (32 s) taken from the **first**, **middle** or **last** part of their clean epochs in time order. Middle = epochs ⌊(n − 8)/2⌋ to ⌊(n − 8)/2⌋ + 7. Participants with fewer than 8 clean epochs use all of them in every position (all of ADFSU; some APAVA), so the position effect comes from ds004504 and most of APAVA.
  2. **Amount at random position.** Each participant is represented by k ∈ {2, 8, 32} clean epochs drawn **at random** without replacement (capped at n), 5 independent draws per k (draw seeds 1–5).
  - Reference: all clean epochs (reproduces EXP-011 LOCO 0.853 and EXP-010 ds004504 0.821; the script stops otherwise).
- **Per representation:** (a) LOCO AUROC, mean over the 3 folds; (b) within-ds004504 AUROC, 5-fold × 10 with the EXP-010 splits, from repeat-averaged probabilities.
- **Contrasts:** first-8 − last-8 and first-8 − middle-8, paired, with bootstrap CIs (LOCO: mean over folds, each fold resampled; within ds004504: paired stratified bootstrap). For random draws: mean AUROC over the 5 draws with min–max, compared descriptively with first-k (EXP-053) and with all epochs. No multiplicity correction: exploratory.
- **Reading rule (fixed now):**
  - **Time in recording** is supported if, within ds004504, first-8 − last-8 has a CI above 0 *and* the first-8 AUROC is above the highest of the 5 random-8 draws.
  - **Amount of data** is supported if random-2 and random-8 both beat all epochs by at least 0.03 on average, in LOCO and within ds004504, *and* first-8 − last-8 within ds004504 has a CI that includes 0.
  - Anything else is reported as **mixed**, with the numbers.
- **Script:** `scripts/11_random_epochs.py` → `results/tables/T11_random_epochs.csv`, `T11_random_epochs_contrasts.csv`, `results/figures/EXP-054_random_epochs.png`

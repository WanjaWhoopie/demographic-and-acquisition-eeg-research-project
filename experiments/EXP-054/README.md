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

## Run record
- **Date:** 2026-11-12 · design committed in 3a7b546 before the run
- **Command:** `python scripts/11_random_epochs.py` (20 parallel workers, about 2 hours)
- **Checks passed:** the all-epoch representation equals the stored Z and reproduces EXP-011 (LOCO 0.853) and EXP-010 (within ds004504 0.821).
- **Outputs:** `results/tables/T11_random_epochs.csv`, `T11_random_epochs_contrasts.csv`, `results/figures/EXP-054_random_epochs.png`

## Results
AUROC, original representation. Random rows: mean over 5 draws, with the lowest and highest draw.

| Epochs per participant | LOCO, mean over folds | Within ds004504 (mean over 10 repeats) |
|---|---|---|
| First 8 | 0.908 [0.845, 0.958] | 0.840 |
| Middle 8 | 0.852 [0.775, 0.919] | 0.818 |
| Last 8 | 0.861 [0.782, 0.926] | **0.895** |
| Random 2 (5 draws) | 0.868 (0.821–0.898) | 0.777 (0.728–0.823) |
| Random 8 (5 draws) | 0.880 (0.849–0.905) | 0.816 (0.788–0.859) |
| Random 32 (5 draws) | 0.873 (0.859–0.890) | 0.827 (0.814–0.836) |
| All | 0.853 [0.773, 0.922] | 0.821 |

| Paired contrast | LOCO ΔAUROC [95% CI] | Within ds004504 ΔAUROC [95% CI] |
|---|---|---|
| First 8 − last 8 | +0.048 [−0.014, 0.118] | **−0.053 [−0.128, 0.014]** |
| First 8 − middle 8 | +0.057 [0.007, 0.112] | +0.038 [−0.043, 0.123] |
| First 8 − all | +0.055 [0.012, 0.105] | +0.016 [−0.047, 0.077] |

Per fold, the spread between random 8-epoch draws is largest when ADFSU is held out (0.75–0.90): with only 2 ADFSU epochs per person, that fold depends entirely on which ds004504 and APAVA epochs the classifier was trained on. 13 of the 15 random draws transfer better than all epochs (0.853).

## Interpretation (exploratory)
- **By the pre-registered rule the result is mixed: neither explanation is supported.**
  - *Time in recording* fails: within ds004504 the **last** 8 epochs classify best (0.895) and first − last is negative (−0.053, CI includes 0).
  - *Amount of data* fails: within ds004504 fewer random epochs make AD detection **worse** (0.777 with 2, 0.816 with 8, 0.827 with 32, 0.821 with all), and across cohorts random subsets beat all epochs by only 0.015–0.027 on average, below the 0.03 threshold.
- **The main lesson is variability.** Which 8 epochs are pooled moves AUROC by about ±0.03 within ds004504 and by up to 0.15 in a single LOCO fold. The within-cohort differences in EXP-053 (0.82–0.88 across k) are of the same size, so EXP-053's within-cohort "early epochs are best" pattern is not a reliable property of these recordings. **This revises EXP-053's practical note.**
- **Across cohorts there is a modest, consistent tilt towards using fewer epochs:** 13 of 15 random subsets and the first 8 epochs transfer better than all data. That fits EXP-053's finding that cohort becomes more decodable the more epochs are averaged, but it is small and not robust by the pre-set rule.
- **For the report:** pooling all available epochs is a defensible default within a cohort. Across cohorts, differences in recording length are a cohort property worth equalising (as in EXP-043), but no strong claim about early versus late EEG is supported.

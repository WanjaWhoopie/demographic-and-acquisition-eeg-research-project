# EXP-053 – Amount of EEG per participant as a hidden cohort effect (exploratory)

## Before running (committed before results were seen; exploratory and post hoc, D-035)
- **Objective:** O5 (interpretation), added after EXP-043. **Question:** Does the very different amount of clean EEG per participant act as a cohort effect that hurts cross-cohort transfer?
- **Why:** with 8 s per participant (EXP-043), LaBraM transferred at 0.928, against 0.853 with all data (EXP-011). Clean 4-s epochs per participant: ADFSU always 2; APAVA median about 30 (1–59); ds004504 median about 180 (68–322). A participant vector averaged over 180 epochs is less noisy than one averaged over 2, so the noise level alone could reveal the cohort.
- **Design:** for k in {1, 2, 4, 8, 16, 32, 64, all}, each participant is represented by the pooled embeddings of their first min(k, n_i) clean epochs in time order. All 176 participants are used at every k. ADFSU stays at 2, so the imbalance between cohorts grows with k. The k = all and k = 2 representations must reproduce the stored Z and Z8 exactly.
- **Per k:** (a) LOCO AD classification with the nested classifier (D-024), original and centring (i); (b) within-ds004504 AD classification, 5-fold × 10 with the EXP-010 splits (k is exact there, since everyone has ≥ 68 epochs); (c) cohort probe, multinomial logistic C = 1, stratified 5-fold × 5, on block 1 and block 11 (patch-mean, mean pooling); (d) mean distance of participants to their cohort centroid.
- **Contrasts:** LOCO AUROC at each k minus at all epochs, paired, mean over folds with bootstrap CI. No multiplicity correction: this is exploratory and reported as such.
- **Expected if data amount is a cohort effect:** (H1) LOCO AUROC is higher at small k than with all data; (H2) within-ds004504 AUROC does *not* fall as k grows, so more data is not harmful in itself; (H3) cohort decodability rises with k; (H4) the centring benefit appears only at large k.
- **Reading rule:** the data-amount explanation is **supported** if the k = 2 versus all contrast has a CI above 0 *and* within-ds004504 AUROC at all epochs is not lower than at k = 2. It is **not supported** if LOCO AUROC does not change with k, or if within-ds004504 AUROC falls as much as LOCO, which would mean later epochs are simply less informative.
- **Known limitation:** "first k epochs" mixes data amount with time in the recording; drowsiness may grow later in long ds004504 sessions. The within-ds004504 curve (H2) is the partial check.
- **Script:** `scripts/11_data_amount.py` → `results/tables/T11_data_amount.csv`, `T11_data_amount_paired.csv`, `T11_dispersion.csv`, `results/figures/EXP-053_data_amount.png`

## Run record
- **Date:** 2026-11-12 · design committed in 3e9b0fe before the run
- **Command:** `python scripts/11_data_amount.py` (20 parallel workers)
- **Checks passed:** the k = all and k = 2 representations equal the stored Z and Z8. At k = all the run reproduces EXP-011 (LOCO 0.853) and EXP-010 (ds004504 0.821).
- **Outputs:** `results/tables/T11_data_amount.csv`, `T11_data_amount_paired.csv`, `T11_dispersion.csv`, `results/figures/EXP-053_data_amount.png`

## Results
Median epochs used per participant: ADFSU 2 at every k; APAVA min(k, n), up to 32.5; ds004504 = k, up to 180.

| Epochs per participant (k) | LOCO AUROC [95% CI] | LOCO(k) − LOCO(all) [95% CI] | Centring ΔAUROC | Within ds004504 AUROC (mean ± SD) | Cohort probe, block 11 |
|---|---|---|---|---|---|
| 1 | 0.888 [0.816, 0.949] | +0.035 [−0.019, 0.097] | +0.004 | 0.867 | 0.684 |
| 2 | 0.922 [0.876, 0.961] | +0.069 [−0.003, 0.149] | +0.062 | 0.882 | 0.751 |
| 4 | 0.909 [0.843, 0.962] | +0.056 [0.016, 0.102] | −0.027 | 0.865 | 0.779 |
| 8 | 0.908 [0.845, 0.958] | +0.055 [0.012, 0.105] | −0.008 | 0.840 | 0.835 |
| 16 | 0.893 [0.830, 0.948] | +0.040 [−0.011, 0.096] | −0.005 | 0.862 | 0.849 |
| 32 | 0.827 [0.746, 0.903] | −0.026 [−0.076, 0.022] | −0.003 | 0.817 | 0.872 |
| 64 | 0.829 [0.744, 0.905] | −0.024 [−0.064, 0.013] | −0.072 | 0.832 | 0.874 |
| all | 0.853 [0.773, 0.922] | – | −0.034 | 0.821 ± 0.030 | 0.875 |

Centring ΔAUROC = original − centred; negative means centring helped. The block 1 cohort probe rises less, from 0.62 to 0.71. Mean distance to the cohort centroid in ds004504 shrinks from 14.0 (k = 1) to 11.9 (k = all) as more epochs are averaged.

## Interpretation (exploratory)
- **By the pre-registered rule, the data-amount explanation is not supported.** Cross-cohort AUROC is higher with a few epochs than with all of them, by 0.04–0.07, with CIs above 0 at k = 4 and k = 8. But **within ds004504 alone, AUROC falls by about as much** (0.88 at k = 2 against 0.82 with all data). The loss with more data is therefore not specific to transfer between cohorts. The first epochs of a recording are simply more informative about AD than the later ones, within a cohort too.
- **More data does make the cohort easier to recognise** (H3 supported). Cohort decodability at block 11 rises from 0.68 to 0.88 as k grows, as within-cohort spread shrinks with averaging. Data amount is thus part of what makes cohort readable. It just is not what limits AD transfer.
- **The centring benefit is not stable across k** (H4 unclear). It appears at 64 epochs and with all data, but at k = 2 centring hurts (+0.062). EXP-043 found +0.005 at 8 s; the difference is one APAVA participant with a single epoch, who is excluded there and included here, in a fold of only 23 people. This instability fits the Phase 9 conclusion that the centring improvement is not robust.
- **Practical note for the report (revised by EXP-054, see below):** in these data, the first 8–16 s of eyes-closed EEG gave the highest AD discrimination, both within and across cohorts. Possible reasons are rising drowsiness or changing state later in long recordings, or more artefact later on. They are not tested here.
- **Limitation:** "first k epochs" mixes the amount of data with the time in the recording. Taking k epochs at random instead of the first k would separate the two. That would be a further exploratory step.

## Follow-up (EXP-054)
EXP-054 separated time in the recording from amount of data and supported neither. Within ds004504 the last 8 epochs classified best (0.895) and fewer random epochs did worse, and AUROC varied by about ±0.03 between random 8-epoch subsets, as much as the within-cohort differences above. The "first 8–16 s are best" note is therefore not a reliable property of these recordings. Only the small cross-cohort advantage of pooling fewer epochs remains, and it is below EXP-054's pre-set threshold.

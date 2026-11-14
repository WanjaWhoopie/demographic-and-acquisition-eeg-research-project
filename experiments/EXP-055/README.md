# EXP-055 – Fixed-block comparison of original and controlled representations (review-prompted)

## Before running (committed before results were seen; post hoc, D-039)
- **Why.** The mentor's review of the draft (14 November 2026) pointed out that the primary
  comparison is not like for like: without control the inner CV chose block 1 in every LOCO fold,
  with centring it chose blocks 11–12 in two folds (`T08_loco.csv`), and in the one fold where the
  block stayed the same (APAVA) ΔAUROC was exactly 0. The primary estimate (0.853 → 0.887) therefore
  mixes the effect of cohort removal with the effect of switching layer. This experiment separates
  them by holding the block fixed.
- **Objective:** O3/O4. **Question:** at a fixed transformer block, does removing cohort
  information change cross-cohort AD performance, and does the answer depend on the block?
- **Design.** For each block b = 1 … 12 and each control in {none, centring (i), LEACE, INLP}:
  leave-one-cohort-out as in EXP-031, with the EXP-031 pipeline (class-weighted logistic regression,
  D-024 nested selection, control refitted inside every inner and outer training fold, D-031), but
  the candidate set is restricted to the four token × pooling configurations of block b. C and
  token/pooling are still chosen by inner CV, so the only change from EXP-031 is that the block
  cannot switch. 12 × 4 × 3 = 144 fits.
- **Outcomes.** Per block and control: per-fold AUROC; mean-over-folds AUROC; ΔAUROC = AUROC(none) −
  AUROC(control), mean over folds, paired stratified participant bootstrap 95% CI (2000 draws, seed
  20261001). Two summary quantities, stated in advance:
  - **Layer-switch share.** How much of the EXP-031 primary gain (+0.034) is reproduced by the
    original (uncontrolled) classifier simply moving from block 1 to the block the centred
    classifier chose: AUROC(none, block 11 or 12) − AUROC(none, block 1), per fold.
  - **Removal effect at the block actually used.** ΔAUROC at block 1 for each control.
- **Reading rule (fixed now; original vs centring (i) is the primary contrast, the others descriptive).**
  - **Obstacle, not shortcut:** no block has a centring ΔAUROC CI above 0 (no harm anywhere), and
    at least one of blocks 9–12 has a CI below 0 (removal helps where cohort information is
    largest). Then the EXP-031 reading stands: cohort offsets stopped the classifier from using
    deep-layer AD information.
  - **Harm hidden by selection:** any block has a centring ΔAUROC CI above 0. Then "removal never
    reduced transfer" is withdrawn from the report and replaced by the per-block result.
  - **No measurable effect at fixed block:** every block's CI includes 0. Then the primary gain is
    reported as a selection effect, not a removal effect.
  - 12 comparisons per control, uncorrected, exploratory: the CIs are read as above without
    multiplicity adjustment, and that is stated.
- **Script:** `scripts/13_review_analyses.py --part fixed_block` → `results/tables/T13_fixed_block.csv`,
  `T13_fixed_block_deltas.csv`, `results/figures/EXP-055_fixed_block.png`. Checks: at block 1 with no
  control, the per-fold AUROC must reproduce EXP-011/EXP-031 where the EXP-031 selection was a
  block-1 configuration (all three folds for "none", APAVA for centring).

## Run record
- **Date:** 2026-11-14 · design committed in 60b0a71 (now 1b35945's parent after the history rewrite; the
  pre-registration is the commit "Pre-register three analyses prompted by the review") before the run
- **Command:** `python scripts/13_review_analyses.py --part fixed_block` (20 workers, about 50 min)
- **Check passed:** block 1 without control reproduces EXP-031 in every fold.
- **Outputs:** `results/tables/T13_fixed_block.csv`, `T13_fixed_block_deltas.csv`, `results/figures/EXP-055_fixed_block.png`

## Results
Mean LOCO AUROC over the three folds, at a fixed block (token, pooling and C by inner CV):

| Block | Original | Centring (i) | LEACE | INLP |
|---|---|---|---|---|
| 1 | 0.853 | 0.862 | 0.852 | 0.862 |
| 4 | 0.841 | 0.839 | 0.840 | 0.843 |
| 8 | 0.830 | 0.858 | 0.816 | 0.844 |
| 10 | 0.891 | 0.875 | 0.860 | 0.877 |
| 11 | **0.908** | 0.887 | 0.858 | 0.879 |
| 12 | 0.888 | **0.908** | 0.860 | 0.860 |

ΔAUROC = original − controlled, mean over folds [95% CI], 36 comparisons, uncorrected:
- **Block 1** (the block the uncontrolled classifier used in every fold): centring −0.009 [−0.027, 0.008];
  LEACE +0.001 [−0.032, 0.034]; INLP −0.009 [−0.051, 0.031]. Removal does nothing there.
- **CIs above 0 (removal costs AUROC):** centring at block 11, +0.021 [0.002, 0.043]; LEACE at block 11,
  +0.050 [0.008, 0.099], and block 12, +0.028 [0.011, 0.051]. Three of 36, against about two expected
  by chance at 5%.
- **CIs below 0 (removal helps):** none. The closest is centring at block 12, −0.020 [−0.044, 0.001].
- **Layer-switch share.** Without any control, deep blocks transfer better than block 1: 0.891 (block 10),
  0.908 (block 11), 0.888 (block 12) against 0.853. The step from block 1 to block 11 alone (+0.055) is
  larger than the whole EXP-031 primary gain (+0.034). Per fold, original block 11 vs block 1: ADFSU
  0.896 vs 0.810, APAVA 0.954 vs 0.879, ds004504 0.873 vs 0.870.

## Interpretation
- **By the pre-registered rule: harm hidden by selection.** One centring CI (block 11) lies above 0.
  The size is small (0.02), it is one of 36 uncorrected comparisons, and LEACE shows the same at blocks
  11–12 (0.03–0.05). The report's sentence "removing cohort information never reduced transfer" is
  withdrawn and replaced by the per-block result.
- **The EXP-031 primary gain was a selection effect, not a removal effect.** At no block does removal
  improve transfer with a CI below 0, and at block 1 it does nothing. What changed in EXP-031 was which
  block the inner CV chose: without control, block 1; with centring, blocks 11–12, which transfer
  better *with or without* control. Cohort offsets did not stop deep blocks from transferring; they
  stopped the inner CV, a pooled cross-validation over two training cohorts with different AD
  prevalence, from *selecting* them. Removing the offsets fixed the selection, and the selection, not
  the removal, raised the AUROC.
- **What stands.** Frozen LaBraM's cross-cohort AD signal does not depend on cohort information:
  removing it at the block in use changes nothing, and at any block it changes AUROC by at most 0.05
  in either direction. The strongest statement the data support is a bound, not a gain.
- **Revises EXP-031.** Its reading "cohort offsets were an obstacle, not a shortcut" is narrowed to
  "an obstacle to model selection, not to transfer".

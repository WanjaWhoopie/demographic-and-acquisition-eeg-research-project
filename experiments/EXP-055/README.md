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

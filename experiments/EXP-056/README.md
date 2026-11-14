# EXP-056 – Positive control: do the cohort controls remove a shortcut where one exists? (review-prompted)

## Before running (committed before results were seen; post hoc, D-039)
- **Why.** The mentor's review (14 November 2026): leave-one-cohort-out already defeats the cohort
  shortcut, because the held-out cohort is never in training. Removal only acts on the training
  cohorts, and with ADFSU held out those two have nearly the same AD prevalence (55% vs 52%). A
  "no harm" result was therefore likely whether or not the controls do anything. The design has no
  setting in which a shortcut exists and removal is shown to take it away. This experiment adds one.
- **Objective:** O3. **Question:** in a pooled analysis where cohort identity predicts diagnosis
  (cohort alone gives AUROC 0.65, `T06_nuisance_baselines.csv`, because ADFSU is 86% AD), do the
  controls reduce the classifier's use of that shortcut?
- **Design.** All 176 participants pooled; participant-level stratified (cohort × diagnosis) 5-fold
  CV × 10 repeats (the splits of the EXP-013 cohort-only baseline, seed 20261001). The full EXP-031
  pipeline: 48 candidates (12 blocks × token × pooling), D-024 nested selection, control refitted
  inside every inner and outer training fold. Controls: none, centring (i), LEACE, INLP. Every
  cohort is present in training, so centring subtracts each cohort's own prevalence-balanced mean
  and no cohort is "unseen".
- **Outcomes**, from repeat-averaged out-of-fold probabilities (as EXP-030):
  - **Pooled AUROC** over all 176 (this is where a cohort shortcut inflates performance).
  - **Within-cohort AUROC** of the same predictions, computed inside each cohort and averaged over
    the three (a shortcut that only orders cohorts cannot raise this).
  - **Shortcut gap** = pooled AUROC − mean within-cohort AUROC, per control.
  - ΔAUROC(pooled) = AUROC(none) − AUROC(control), paired stratified participant bootstrap 95% CI;
    the same for the shortcut gap (bootstrap of the difference of gaps).
  - Also mean ± SD over the 10 repeats of the per-repeat values.
- **Reading rule (fixed now; centring (i) is the primary contrast).**
  - **Controls remove the shortcut:** the original classifier's shortcut gap is at least 0.03, and
    centring reduces the pooled AUROC with a CI above 0 *or* reduces the shortcut gap with a CI
    above 0, while its within-cohort AUROC does not fall by more than 0.03. Then the controls are
    shown to act on cohort information without damaging the within-cohort AD signal, and the LOCO
    "no harm" result is informative.
  - **Controls ineffective:** the original shortcut gap is at least 0.03 and neither CI is above 0.
    Then the controls do not measurably remove what they are meant to remove, and the report must
    say that the LOCO null result cannot be read as evidence about the controls.
  - **Shortcut not exploited:** the original classifier's shortcut gap is below 0.03. Then the
    pooled setting gives no test of the controls either, and this is reported as such; an induced
    cohort–diagnosis correlation would be the next step, outside this experiment.
- **Script:** `scripts/13_review_analyses.py --part pooled` → `results/tables/T13_pooled_control.csv`,
  `results/figures/EXP-056_pooled_control.png`.

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

## Run record
- **Date:** 2026-11-14 · design committed in abf5c4d ("Pre-register three analyses prompted by the review") before the run
- **Command:** `python scripts/13_review_analyses.py --part pooled` (20 workers, about 1 h 50 min)
- **Outputs:** `results/tables/T13_pooled_control.csv`, `results/figures/EXP-056_pooled_control.png`

## Results
Pooled participant-level CV over all 176 (cohort × diagnosis stratified, 5-fold × 10), repeat-averaged
probabilities. Shortcut gap = pooled AUROC − mean within-cohort AUROC of the same predictions.

| Control | Pooled AUROC [95% CI] | Within-cohort AUROC | Shortcut gap | ΔAUROC pooled [CI] | Δgap [CI] | Most selected |
|---|---|---|---|---|---|---|
| Original | 0.935 [0.883, 0.972] | 0.910 | **+0.025** | – | – | block 12, patch-mean, median |
| Centring (i) | 0.934 [0.886, 0.970] | 0.915 | +0.019 | 0.000 [−0.008, 0.008] | +0.005 [−0.009, 0.024] | block 12, patch-mean, mean |
| LEACE | 0.896 [0.838, 0.941] | 0.901 | −0.006 | **+0.039 [0.006, 0.072]** | **+0.030 [0.006, 0.056]** | block 12, patch-mean, median |
| INLP | 0.882 [0.820, 0.932] | 0.878 | +0.004 | **+0.052 [0.016, 0.091]** | +0.020 [−0.015, 0.056] | block 2, CLS, median |

Within-cohort AUROC per cohort (original): ADFSU 0.909, APAVA 0.939, ds004504 0.882. INLP lowered the
within-cohort AUROC by 0.032 (ADFSU 0.817); centring and LEACE left it within 0.01.

## Interpretation
- **By the pre-registered rule: shortcut not exploited.** The original classifier's shortcut gap is
  0.025, below the 0.03 threshold. Although cohort identity alone predicts AD at 0.65 in this pooled
  setting (EXP-013), the LaBraM classifier took almost none of that shortcut: its pooled AUROC is
  only 0.025 above what it achieves inside each cohort. The pooled setting therefore cannot show
  whether centring removes a shortcut, because there was little to remove. This is reported as such.
- **What the controls did anyway.** Centring changed nothing (ΔAUROC 0.000). LEACE lowered pooled AUROC
  by 0.039 and closed the gap (−0.006 after), while leaving within-cohort AUROC within 0.01: it removed
  the small between-cohort ordering the classifier had used, and no more. INLP lowered pooled AUROC by
  0.052 but also within-cohort AUROC by 0.032, so part of its effect was damage to the AD signal, as
  Aimoldin et al. (2026) report for erasure elsewhere.
- **Why the shortcut was not taken.** In pooled CV the inner CV chose block 12 and reached 0.91 within
  cohorts; a classifier that separates AD from HC that well inside every cohort gains little from
  ordering cohorts by prevalence. The cohort shortcut is available in these data but not attractive
  to this classifier. That weakens the premise that "no harm" in LOCO was a near-certain null, but it
  also means the positive control is only partly informative: it shows LEACE acting on cohort
  information without damaging the within-cohort AD signal, and shows nothing about centring.
- **Next step, not taken for time:** an induced cohort–diagnosis correlation (for example, dropping
  ADFSU controls so that cohort predicts diagnosis more strongly) would give centring a shortcut large
  enough to test.

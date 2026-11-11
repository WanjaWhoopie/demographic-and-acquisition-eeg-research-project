# EXP-040 – Primary outcome: cohort-controlled vs original LOCO AUROC

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does removing cohort information change cross-cohort AD performance, by the pre-specified primary measure?
- **Data and method:** the EXP-031 predictions, with no refitting. Original Z vs prevalence-balanced centring variant (i) (D-026), 3 LOCO folds.
- **Outcome:** mean over folds of ΔAUROC = AUROC(Z) − AUROC(Z\*), with a 95% CI from the paired stratified bootstrap (2000 draws, each fold resampled independently). Per-fold ΔAUROC with CIs, and the controlled representation's mean AUROC with CI.
- **Decision rule (D-027):** **A**: the CI of mean ΔAUROC includes 0. **Significantly negative**: the CI lies below 0, meaning control improved transfer; reported as its own outcome. **C**: the CI lies above 0 and the controlled mean AUROC CI includes 0.5. **B**: the CI lies above 0 and the controlled AUROC stays above 0.5.
- **Note:** EXP-031 already shows the estimate (−0.034 [−0.069, −0.001]). This experiment applies the rule and builds the T9.4 summary table; nothing is re-estimated.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`; design committed in 3e07a74 before the run
- **Command:** `python scripts/09_sensitivity.py` (20 parallel workers). The first attempt stopped before any sensitivity result because the participant ID column was not loaded. It was fixed and re-run in full; the primary numbers were identical.
- **Output:** `results/tables/T09_primary_and_sensitivity.csv`

## Results
| Held-out cohort | n AD / HC | Original AUROC [95% CI] | Centred (i) AUROC [95% CI] | ΔAUROC [95% CI] |
|---|---|---|---|---|
| ADFSU | 76 / 12 | 0.810 [0.661, 0.938] | 0.855 [0.726, 0.959] | −0.045 [−0.136, 0.039] |
| APAVA | 12 / 11 | 0.879 [0.697, 1.000] | 0.879 [0.697, 1.000] | 0.000 |
| ds004504 | 36 / 29 | 0.870 [0.774, 0.952] | 0.926 [0.853, 0.980] | −0.057 [−0.113, −0.012] |
| **Mean over folds** | | **0.853 [0.773, 0.922]** | **0.887 [0.812, 0.951]** | **−0.034 [−0.069, −0.001]** |

**Pattern (D-027): significantly negative ΔAUROC.** Cohort control improved cross-cohort transfer. The rule's criteria for A, B and C are not met.

## Interpretation, read together with the sensitivity analyses (EXP-041 to EXP-044)
| Analysis | Mean original AUROC | Mean centred AUROC | Mean ΔAUROC | Reading |
|---|---|---|---|---|
| Primary | 0.853 | 0.887 | −0.034 [−0.069, −0.001] | control improved transfer |
| Without ADFSU (EXP-041) | 0.874 | 0.874 | 0 by construction | not a test of control (D-033) |
| ADFSU AD subsampled, 100 draws (EXP-042) | 0.878 (median) | 0.895 (median) | −0.017, draws 2.5–97.5%: [−0.063, 0.031] | same direction in 80% of draws |
| 8 s per participant (EXP-043) | 0.928 | 0.922 | +0.005 [−0.001, 0.014] | A: no change |
| Amplitude-scaled (EXP-044) | 0.861 | 0.853 | +0.009 [−0.037, 0.060] | A: no change |

- **Robust conclusion: removing cohort information never reduced LaBraM's cross-cohort AD performance.** No analysis shows a ΔAUROC whose CI lies above 0. The AD signal LaBraM transfers between cohorts does not depend on cohort mean offsets, or on linearly decodable cohort information (LEACE, EXP-032).
- **The small improvement in the primary analysis is not robust.** It shrinks when ADFSU is balanced, and it disappears when every participant contributes the same 8 s or when amplitudes are equalised. It is best read as centring partly compensating for two cohort differences that those sensitivity analyses remove directly: the amount of data per participant and the signal amplitude.
- **Data amount itself looks like a cohort effect.** With 8 s per participant the original representation transfers at 0.928, against 0.853 with all available data. This was not a pre-specified comparison, and the participant sets differ by one, so it is descriptive. It fits the risk recorded in D-018: averaging hundreds of epochs (ds004504) against two (ADFSU) makes participant embeddings differ by cohort for reasons unrelated to disease. It is a candidate for a Phase 11 follow-up and a point for the final report.
- Formal multiplicity correction across the secondary comparisons (D-028) follows in Phase 10.

## Statistics (Phase 10, D-034)
`python scripts/10_stats.py` works from the saved predictions only. All 10 headline ΔAUROCs and CIs in T08/T09 were reproduced, with a largest difference of 0.00005 (`results/tables/T10_reproduction.csv`).

| Comparison | ΔAUROC [95% CI] | Bootstrap p | Holm-adjusted p (m = 6) |
|---|---|---|---|
| **Primary: centring (i)** | **−0.034 [−0.069, −0.001]** | **0.046** | tested alone |
| 1 Centring (ii) | −0.034 [−0.069, −0.001] | 0.046 | 0.28 |
| 2 LEACE | −0.030 [−0.081, 0.016] | 0.24 | 0.92 |
| 3 INLP | −0.023 [−0.071, 0.020] | 0.31 | 0.92 |
| 4 Age/sex residualisation, ds004504 | +0.042 [−0.026, 0.118] | 0.23 | 0.92 |
| 5 8 s per participant | +0.005 [−0.001, 0.014] | 0.11 | 0.55 |
| 6 Amplitude-scaled | +0.009 [−0.037, 0.060] | 0.76 | 0.92 |
| 7 Without ADFSU | not estimable (D-033) | – | – |
| 8 ADFSU subsampled | distribution, not tested (EXP-042) | – | – |

- **The primary outcome is just significant (p = 0.046).** No secondary comparison survives Holm correction. The same contrast as the primary, under centring (ii), gives an adjusted p of 0.28, because it is the most significant of six.
- **DeLong cross-check (T10.4):** across 22 per-fold AUROC CIs, the largest difference between a DeLong and a bootstrap limit is 0.029, below the 0.05 materiality threshold. Bootstrap and analytic intervals agree (`T10_delong.csv`).
- **Overall statistical reading:** one borderline improvement in the primary analysis, and no evidence in any analysis that removing cohort information reduces cross-cohort AD performance.

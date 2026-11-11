# EXP-021 – Cohort probe

## Before running (committed before results were seen)
- **Objective:** O2 · **Question:** How well can the cohort (recording site/system) be read out of the representation?
- **Data:** all 176 participants, three cohorts; chance balanced accuracy 1/3.
- **Method:** class-weighted multinomial logistic regression with nested selection (D-024), outer stratified (cohort × diagnosis) 5-fold × 5; balanced accuracy, macro-F1, confusion matrix. Layer profile: the same probe per block (patch-mean token, mean pooling, C = 1), descriptive.
- **Reference values:** classical spectral features 0.687 (EXP-003, pre-registered as the floor); random-weights LaBraM.
- **Interpretation rule:** LaBraM ≫ 0.69 → the model encodes acquisition information beyond what spectral shape carries; ≈ 0.69 → the cohort signal is spectral and visible to any method.
- **Script:** `scripts/07_probes.py` → `results/tables/T07_cohort_probe.csv`, `T07_cohort_confusion.csv`, `T07_cohort_layer_profile.csv`, `results/figures/EXP-021_layer_profile.png`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/07_probes.py` (same run as EXP-020)
- **Outputs:** `results/tables/T07_cohort_probe.csv`, `T07_cohort_confusion.csv`, `T07_cohort_layer_profile.csv`, `results/figures/EXP-021_layer_profile.png`

## Results
Mean ± SD over 5 repeats of stratified 5-fold CV, all 176 participants; chance = 0.333.

| Representation | Balanced accuracy | Macro-F1 | Most-selected configuration |
|---|---|---|---|
| **Pretrained LaBraM** | **0.879 ± 0.006** | 0.861 | block 11, patch-mean, mean pooling |
| Random-weights LaBraM | 0.773 ± 0.027 | 0.742 | block 9, CLS, mean pooling |
| Classical features, 80 (same nested pipeline) | 0.769 ± 0.031 | 0.759 | – |
| Classical relative band power, 64 (EXP-003, pre-registered reference) | 0.687 ± 0.093 | – | – |

The like-for-like reference is the 80-feature classical row, which uses the same nested pipeline. EXP-003 used shape-only band power without the aperiodic exponents.

Per-cohort recall, pretrained LaBraM, summed over 5 repeats: ds004504 96% (311/325), ADFSU 86% (379/440), APAVA 82% (94/115). Most errors are ADFSU recordings predicted as APAVA (35) or ds004504 (26).

**Layer profile** (patch-mean token, mean pooling, C = 1, descriptive; figure `EXP-021_layer_profile.png`):

| Block | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pretrained | 0.71 | 0.77 | 0.76 | 0.84 | 0.85 | 0.82 | 0.84 | **0.89** | 0.87 | 0.88 | 0.87 | 0.86 |
| Random | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 | 0.79 |

## Interpretation
- **Cohort identity is strongly decodable from LaBraM (0.88, chance 0.33), and more so than from classical features (0.77) or an untrained LaBraM (0.77).** Under the pre-registered rule this is the "LaBraM ≫ reference" case: pretraining adds acquisition information beyond what spectral shape carries. The gap is about 0.11 balanced accuracy against a repeat-to-repeat SD of 0.006–0.031. These are descriptive comparisons. No CI on the difference was pre-registered.
- **Cohort information grows with depth.** Block 1 holds less than the untrained network (0.71 vs 0.79), and blocks 8–12 hold the most (0.86–0.89). The untrained network is flat across blocks, as expected for a random residual stack that mostly passes its input through.
- **Link to Phase 6:** the LOCO AD classifier chose block 1 in all three folds, the block with the *least* cohort information. That fits the reading that deeper, more cohort-laden blocks transfer worse. It is a correlation across two analyses, not a test.
- **Consequence for Phase 8:** cohort is the nuisance variable worth removing. Centring, LEACE and INLP are all justified, and the controlled representation should be re-probed against the 0.879 here.

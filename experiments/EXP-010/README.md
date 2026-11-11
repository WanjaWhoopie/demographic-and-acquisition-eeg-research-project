# EXP-010 – Within-cohort baseline

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1
- **Question:** How well do frozen LaBraM representations separate AD from HC *within* each cohort?
- **Expected:** above chance in every cohort (published within-dataset LaBraM dementia AUROC ≈ 0.89, Lin, Hou & Jung 2026, nonlinear read-out); ADFSU less certain (8 s per person, 12 HC).
- **Data:** each cohort separately; all clean epochs (D-018); ds004504 36/29, ADFSU 76/12, APAVA 12/11.
- **Representation:** frozen LaBraM-base; block × token × pooling chosen inside training folds (D-024).
- **Method:** participant-stratified 5-fold × 10 repeats (seed 20261001); inside each training fold an inner stratified 5-fold picks (block, token, pooling, C) by AUROC; class-weighted L2 logistic regression with standardisation (D-006).
- **Metrics:** AUROC (primary; mean ± SD over repeats and stratified-bootstrap 95% CI on repeat-averaged probabilities), PR-AUC, balanced accuracy / sensitivity / specificity / F1 at 0.5 (D-025).
- **Config:** `configs/analysis.yaml` · **Script:** `scripts/06_baseline.py`
- **What would change our plan?** A cohort at chance would make its LOCO fold uninformative about nuisance removal.

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`
- **Command:** `python scripts/06_baseline.py` (20 parallel workers, ~20 min)
- **Outputs:** `results/tables/T06_within_cohort.csv`, `T06_loco.csv`, `T06_loco_deltas.csv`, `T06_nuisance_baselines.csv`, `T06_selected_configs.csv`; participant predictions in `results/runs/EXP-011/predictions.csv` (local)

## Results
| Cohort | n AD / HC | LaBraM AUROC (mean ± SD over 10 repeats) | 95% CI* | Bal. acc. | Sens. | Spec. |
|---|---|---|---|---|---|---|
| ds004504 | 36 / 29 | **0.821 ± 0.030** | 0.770–0.942 | 0.77 | 0.75 | 0.79 |
| ADFSU | 76 / 12 | **0.925 ± 0.043** | 0.875–1.000 | 0.88 | 1.00 | 0.75 |
| APAVA | 12 / 11 | **0.821 ± 0.040** | 0.636–0.992 | 0.83 | 0.75 | 0.91 |

\*CI from the stratified participant bootstrap on probabilities averaged over the 10 repeats; averaging acts as a small ensemble, so the point estimate behind the CI (0.866 / 0.961 / 0.833) sits above the per-repeat mean. The per-repeat mean is the headline number.

Selected representations varied across folds: late blocks (11–12) and early blocks (1–2) were both chosen; no single block dominated.

## Interpretation
Frozen LaBraM separates AD from HC within every cohort, comparable to the published within-dataset LaBraM result (Lin, Hou & Jung 2026, AUROC 0.89 with a random forest). See EXP-012/013 for how much of this a simpler or untrained representation also achieves.

# EXP-040 – Primary outcome: cohort-controlled vs original LOCO AUROC

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does removing cohort information change cross-cohort AD performance, by the pre-specified primary measure?
- **Data and method:** the EXP-031 predictions, with no refitting. Original Z vs prevalence-balanced centring variant (i) (D-026), 3 LOCO folds.
- **Outcome:** mean over folds of ΔAUROC = AUROC(Z) − AUROC(Z\*), with a 95% CI from the paired stratified bootstrap (2000 draws, each fold resampled independently). Per-fold ΔAUROC with CIs, and the controlled representation's mean AUROC with CI.
- **Decision rule (D-027):** **A**: the CI of mean ΔAUROC includes 0. **Significantly negative**: the CI lies below 0, meaning control improved transfer; reported as its own outcome. **C**: the CI lies above 0 and the controlled mean AUROC CI includes 0.5. **B**: the CI lies above 0 and the controlled AUROC stays above 0.5.
- **Note:** EXP-031 already shows the estimate (−0.034 [−0.069, −0.001]). This experiment applies the rule and builds the T9.4 summary table; nothing is re-estimated.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

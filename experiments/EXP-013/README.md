# EXP-013 – Nuisance-only and negative-control baselines

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O1 (references for interpreting O2–O4)
- **Baselines:**
  1. age + sex → AD within ds004504 (repeated stratified 5-fold × 10, C = 1);
  2. cohort identity (one-hot) → AD on all 176 participants pooled (stratified on cohort × diagnosis, 5-fold × 10, C = 1): how much "AD" a model gets from knowing the cohort's AD prevalence;
  3. untrained (random-weights) LaBraM, same pipeline as EXP-010 and EXP-011: how much comes from the architecture and preprocessing rather than pretraining.
- **Metric:** AUROC with stratified-bootstrap 95% CI.
- **Expected:** (1) modest (sex imbalance, age balanced); (2) well above 0.5 because ADFSU is 86% AD; (3) above chance if spectral power alone drives classification.

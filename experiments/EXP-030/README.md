# EXP-030 – Age and sex residualisation (ds004504)

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O3 · **Question:** Does removing the linear effect of age and sex from Z change within-cohort AD classification in ds004504?
- **Expected:** little change. EXP-020 found no decodable age or sex information, so there is little to remove; a ΔAUROC near 0 is the expected result. A clear drop would mean the classifier relied on age/sex-linked directions that the probes were too weak to detect.
- **Data:** ds004504, 36 AD / 29 HC (the only cohort with age and sex).
- **Method:** within each training fold, OLS per embedding dimension Z_d ~ age + sex (intercept, centred covariates, sex 0/1); the covariate-explained part is subtracted from training and test participants using their own age/sex (T8.1.1–T8.1.2). The residualiser is refitted inside every inner fold of the nested selection (D-031). Two versions: **resid_all**, fitted on all training participants (primary for this experiment), and **resid_hc**, fitted on training HC only (normative, T8.1.4). Same splits and seeds as EXP-010 (5-fold × 10 repeats); the uncontrolled classifier is re-run in the same script as the paired reference and must reproduce EXP-010.
- **Metrics:** ΔAUROC = AUROC(Z) − AUROC(Z\*), paired stratified bootstrap (2000) on repeat-averaged probabilities; mean ± SD over repeats of the per-repeat ΔAUROC. resid_all ΔAUROC is item 4 of the Holm family (D-028).
- **Verification (T8.1.5):** age (ridge, α = 10) and sex (logistic, C = 1) probes, linear and MLP, with and without residualisation, on the configuration the AD classifier chose most often (descriptive).
- **Script:** `scripts/08_control.py` → `results/tables/T08_demographic.csv`, `T08_verification_probes.csv`

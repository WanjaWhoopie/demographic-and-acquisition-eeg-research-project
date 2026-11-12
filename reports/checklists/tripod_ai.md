# TRIPOD+AI checklist (T12.1)

Collins et al. (2024), *BMJ* 385:e078378. Item wording is shortened here; **check the numbering and
wording against the published checklist (Table 1) before the report goes to the mentor.**

**How TRIPOD+AI applies here.** This is a *measurement study* of a frozen EEG foundation model, not
the development of a clinical prediction model for deployment. The "model" is a frozen LaBraM
encoder with a logistic-regression read-out, evaluated by leave-one-cohort-out (LOCO). Items about
intended clinical use, model updating and implementation are answered by saying so.

"Report §" refers to `reports/writeup/final_report.md`. State: ✅ addressed · ⚠️ partly or still to
write · n/a not applicable, with the reason.

| Item | Topic | Where / how addressed | State |
|---|---|---|---|
| 1 | Title: development/evaluation of a prediction model, AI, target population, outcome | Report title names frozen EEG foundation model, AD vs healthy controls, cross-cohort evaluation | ✅ |
| 2 | Abstract (TRIPOD+AI for Abstracts) | Report abstract; check against the abstract checklist once results are final | ⚠️ |
| 3a | Healthcare context and rationale | Report §1, §2 | ✅ |
| 3b | Target population and intended use; intended users | Report §1: research measurement, not a diagnostic tool; no intended clinical user | ✅ |
| 3c | Known health inequalities between groups | Report §2.3 (sex imbalance in ds004504; age); §5.4 limitations; demographics only in one cohort | ✅ |
| 4 | Objectives, including development and/or validation | Report §1 (O1–O5); `docs/protocol.md` | ✅ |
| 5a | Data sources, separately for development and evaluation | Report §3.1, Table 1; `docs/datasets.md` | ✅ |
| 5b | Dates of data collection | Report §3.1 (ds004504 recorded 2010s; ADFSU 1990s FSU database; APAVA early 2000s) – **check exact years against the source papers** | ⚠️ |
| 6a | Setting and centres | Report §3.1 (three centres, three countries, one per cohort) | ✅ |
| 6b | Eligibility criteria | Report §3.1: AD and HC only, eyes-closed resting EEG; FTD and ADSZ excluded (D-017) | ✅ |
| 6c | Treatments received, if relevant | Not reported in the source datasets; stated as unknown in §5.4 | ✅ |
| 7 | Data pre-processing and quality checking, comparable across groups | Report §3.2, Table 2; EXP-001, EXP-003; `reports/data_audit_report.md` | ✅ |
| 8a | Outcome definition, time horizon, how assessed | Report §3.1: clinical AD diagnosis as given by each source (criteria differ, see §5.4); cross-sectional | ✅ |
| 8b | Qualifications and demographics of outcome assessors | Not available from public sources; stated | ✅ |
| 8c | Blinding of outcome assessment to predictors | Diagnosis made before and independent of our analysis; source-level blinding unknown | ✅ |
| 9a | Choice of initial predictors and pre-selection | Report §3.3: all LaBraM blocks × token × pooling; selection inside training folds only (D-024) | ✅ |
| 9b | Definition and measurement of predictors | Report §3.3; D-022 (LaBraM input conventions) | ✅ |
| 9c | Qualifications and blinding of predictor assessors | Predictors computed automatically by the pipeline, the same for every participant | ✅ |
| 10 | Sample size justification | Report §3.6: fixed by the available public cohorts (176 participants); no formal calculation; consequences discussed (§5.4) | ✅ |
| 11 | Missing data and how handled | Report §3.2: no participant lost; one APAVA HC with a single epoch (excluded only from the 8-s analysis); demographics missing in two cohorts by design (D-007, D-008); median imputation in the pipeline for the aperiodic features | ✅ |
| 12a | How data were used (development, tuning, evaluation) | Report §3.4: nested CV within training cohorts; LOCO outer loop | ✅ |
| 12b | Handling of predictors in the analyses | Report §3.3–3.5 | ✅ |
| 12c | Model type, rationale, building steps, hyperparameter tuning | Report §3.4: class-weighted logistic regression, inner-CV selection over representation and C | ✅ |
| 12d | Heterogeneity in performance across clusters (centres) | Per-fold (per-cohort) results throughout; F5 | ✅ |
| 12e | Performance measures and their rationale | Report §3.6: AUROC primary; PR-AUC, balanced accuracy, sensitivity, specificity at 0.5 (D-025) | ✅ |
| 12f | Model updating / recalibration | n/a: no model is updated; the controlled representation is a comparison, not an update | n/a |
| 12g | Fairness / comparison with existing models | Classical spectral comparator and untrained LaBraM (EXP-012, EXP-013) | ✅ |
| 13 | Class imbalance and methods to handle it | Class-weighted logistic regression; prevalence-balanced cohort means (D-009); ADFSU subsampling sensitivity (EXP-042) | ✅ |
| 14 | Fairness: approaches to address it | Age and sex probes and residualisation within ds004504 (EXP-020, EXP-030); limited by missing demographics in two cohorts | ✅ |
| 15 | Model output and rationale for thresholds | Probability of AD; threshold 0.5 (D-025); calibration across cohorts discussed (pooled vs per-fold AUROC, EXP-011) | ✅ |
| 16 | Differences between development and evaluation data | Report §3.1, Table 1 (cohort differences in amplifier, rate, length, prevalence); this is the object of study | ✅ |
| 17 | Ethical approval | Report §3.7: secondary analysis of public, de-identified datasets used under their published data-use terms (`docs/licences/`) | ✅ |
| 18 | Funding | Report back matter: fellowship (fill in funder wording) | ⚠️ |
| 19 | Conflicts of interest | Report back matter | ⚠️ |
| 20a | Protocol availability | `docs/protocol.md`; analysis plan frozen as git tag `analysis-plan-v1` | ✅ |
| 20b | Registration | Not registered in an external registry; pre-registration is internal (frozen tag, per-experiment "Before running" commits, decision log with before/after column) | ✅ |
| 20c | Data availability | Public sources listed in `docs/datasets.md`; no data redistributed | ✅ |
| 20d | Code availability | Public GitHub repository; `README` run order (T12.7) | ✅ |
| 21 | Patient and public involvement | None; stated | ✅ |
| 22 | Participant flow and characteristics (development vs evaluation) | Report §4.1, F2, Table 1 | ✅ |
| 23a | Model development: number of participants and outcome events per analysis | Report §4 tables give n AD / n HC for every fold | ✅ |
| 23b | Full model specification / how to obtain it | Selected configurations per fold (`T06_selected_configs.csv`, `T08_loco.csv`); code to refit | ✅ |
| 24 | Model specification for use | n/a for clinical use; reproducible from the code and public data | n/a |
| 25 | Performance with CIs, for each cohort and overall | F5, Tables 3 and 5; bootstrap CIs, DeLong cross-check (T10_delong) | ✅ |
| 26 | Results of any model updating | n/a | n/a |
| 27a | Interpretation, including fairness | Report §5.1–5.3 | ✅ |
| 27b | Limitations (non-representative sample, sample size, overfitting, missing data) | Report §5.4 | ✅ |
| 27c | Usability, implications for practice and research | Report §5.5: research implications; no claim of clinical readiness | ✅ |

## Open items before submission
- Item 2: check the abstract against TRIPOD+AI for Abstracts.
- Item 5b: exact recording years for each cohort.
- Items 18–19: funding and conflict-of-interest statements.
- Check item numbering against the published checklist.

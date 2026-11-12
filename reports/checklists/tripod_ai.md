# TRIPOD+AI checklist (T12.1)

Collins et al. (2024), *BMJ* 385:e078378. Structure as given in the statement: title (item 1), abstract
(2), introduction (3–4), methods (5–17), open science (18a–f), patient and public involvement (19),
results (20–24), discussion (25–27); 52 sub-items. Item wording is shortened here; **check each
sub-item's wording was checked against the published checklist (Table 2 of the paper; checklist PDF of 11 January 2024) on 12 November 2026.** The correction (BMJ 2024;385:q902) changed author affiliations only.

**How TRIPOD+AI applies here.** This is a *measurement study* of a frozen EEG foundation model, not
the development of a clinical prediction model for deployment. The "model" is a frozen LaBraM
encoder with a logistic-regression read-out, developed on two cohorts and evaluated on the third
(leave-one-cohort-out, LOCO), so both development (D) and evaluation (E) items apply. Items about
intended clinical use and model updating are answered by saying so.

"Report §" refers to `reports/writeup/final_report.md`. State: ✅ addressed · ⚠️ partly or still to
write · n/a not applicable, with the reason.

| Item | Topic | Where / how addressed | State |
|---|---|---|---|
| 1 | Title | Report title names the population (AD vs healthy controls), the model (frozen EEG foundation model) and the cross-cohort question; it is a measurement study, so it does not say "develops a prediction model" | ✅ |
| 2 | Abstract (TRIPOD+AI for Abstracts, 13 items) | Checked: data sources, eligibility, outcome, model type and tuning, measures, participants, selected representation, CIs, interpretation, registration status | ✅ |
| 3a | Healthcare context and rationale | Report §1, §2 | ✅ |
| 3b | Target population, intended use, intended users | Report §1: research measurement, not a diagnostic tool; no intended clinical user | ✅ |
| 3c | Known health inequalities between groups | Report §2.3 (sex imbalance in ds004504; age); §5.4; demographics only in one cohort | ✅ |
| 4 | Objectives (development and/or evaluation) | Report §1 (O1–O5); `docs/protocol.md` | ✅ |
| 5a | Data sources, separately for development and evaluation; representativeness | Report §3.1, Table 1; `docs/datasets.md` | ✅ |
| 5b | Dates of data collection | Report §3.1: not reported by any source; inferred eras stated (ADFSU before 1991, APAVA before 2006, ds004504 not stated) | ✅ |
| 6a | Setting and centres | Report §3.1: one centre per cohort, three countries (Greece, USA, Spain) | ✅ |
| 6b | Eligibility criteria | Report §3.1: AD and HC only, eyes-closed resting EEG; FTD and ADSZ excluded (D-017) | ✅ |
| 6c | Treatments received | Not reported by the sources; stated as unknown (§5.4) | ✅ |
| 7 | Data pre-processing and quality checking, comparable across groups | Report §3.2, Table 2; EXP-001, EXP-003; `reports/data_audit_report.md` | ✅ |
| 8a | Outcome definition, time horizon, how assessed | Report §3.1: clinical AD diagnosis per source; cross-sectional. Criteria: ds004504 DSM-IIIR/DSM-IV/ICD-10 and NINCDS-ADRDA (Miltiadous et al., 2023); ADFSU NINCDS-ADRDA and DSM-III-R | ✅ |
| 8b | Outcome assessors' qualifications and demographics | Not available from public sources; stated | ✅ |
| 8c | Blinding of outcome assessment | Diagnoses predate and are independent of this analysis | ✅ |
| 9a | Choice of initial predictors and pre-selection | Report §3.3: all LaBraM blocks × token × pooling; selection inside training folds only (D-024) | ✅ |
| 9b | Definition and measurement of predictors | Report §3.3; D-022 (LaBraM input conventions) | ✅ |
| 9c | Predictor assessors' qualifications and blinding | Predictors computed automatically, identically for every participant | ✅ |
| 10 | Sample size | Report §3.6: fixed by the public cohorts (176); no formal calculation; consequences in §5.4 | ✅ |
| 11 | Missing data | Report §3.2: no participant lost; one APAVA HC with one epoch (excluded only from the 8-s analysis); demographics missing in two cohorts by design (D-007, D-008); median imputation for undefined aperiodic exponents | ✅ |
| 12a | How data were used (development, tuning, evaluation) | Report §3.4: nested CV within training cohorts; LOCO outer loop | ✅ |
| 12b | How predictors were handled | Report §3.3–3.5 | ✅ |
| 12c | Model type, building steps, hyperparameter tuning | Report §3.4: class-weighted logistic regression; inner-CV selection of representation and C | ✅ |
| 12d | Heterogeneity across clusters (centres) | Per-fold (per-cohort) results throughout; F5 | ✅ |
| 12e | Performance measures and rationale | Report §3.6: AUROC primary; PR-AUC, balanced accuracy, sensitivity, specificity at 0.5 (D-025) | ✅ |
| 12f | Model updating, overall or for subgroups/settings | n/a: no model is updated; the controlled representations are comparisons | n/a |
| 12g | How predictions were calculated in evaluation | Report §3.4: the fold's training-cohort model applied to the held-out cohort; controls refitted on training rows only (D-031) | ✅ |
| 13 | Class imbalance | Class-weighted logistic regression; prevalence-balanced cohort means (D-009); ADFSU subsampling (EXP-042) | ✅ |
| 14 | Fairness: methods used | Age and sex probes and residualisation in ds004504 (EXP-020, EXP-030); limited by missing demographics elsewhere | ✅ |
| 15 | Model output and thresholds | Probability of AD; threshold 0.5 (D-025); between-cohort calibration discussed (pooled vs per-fold AUROC, EXP-011) | ✅ |
| 16 | Differences between development and evaluation data | Report §3.1, Table 1: amplifier, rate, length, prevalence; the object of study | ✅ |
| 17 | Ethical approval | Report §3.7: secondary analysis of public, de-identified data under published data-use terms (`docs/licences/`) | ✅ |
| 18a | Funding | Report back matter: ABDN fellowship | ✅ |
| 18b | Conflicts of interest | Report back matter: none declared | ✅ |
| 18c | Protocol | `docs/protocol.md`; analysis plan frozen as git tag `analysis-plan-v1` | ✅ |
| 18d | Registration | Not in an external registry; internal pre-registration (frozen tag, per-experiment "Before running" commits, decision log with before/after column) | ✅ |
| 18e | Data sharing | Public sources in `docs/datasets.md`; no data redistributed | ✅ |
| 18f | Code sharing | Public GitHub repository; `README.md` run order | ✅ |
| 19 | Patient and public involvement | None; stated | ✅ |
| 20a | Participant flow | Report §3.1, F2 | ✅ |
| 20b | Participant characteristics, including by group | Table 1 (age and sex where available) | ✅ |
| 20c | Comparison of development and evaluation data | Table 1; each LOCO fold's training and test cohorts | ✅ |
| 21 | Number of participants and outcome events in each analysis | n AD / n HC per fold in Tables 3 and 5, F5 | ✅ |
| 22 | Full model specification | Selected configuration and C per fold (`T06_selected_configs.csv`, `T08_loco.csv`); code to refit | ✅ |
| 23a | Performance with CIs, including subgroups | F5, Tables 3 and 5; bootstrap CIs; DeLong cross-check (`T10_delong.csv`); sex and age subgroups only in ds004504 probes | ✅ |
| 23b | Heterogeneity in performance across clusters | Per-cohort results; Report §4.2, §4.4 | ✅ |
| 24 | Model updating results | n/a | n/a |
| 25 | Interpretation, including fairness | Report §5.1–5.3 | ✅ |
| 26 | Limitations | Report §5.4 | ✅ |
| 27a–c | Usability, implications, future research | Report §5.5: research implications only; no claim of clinical readiness | ✅ |

## Open items before submission
None. Numbering and sub-items match the published checklist; recheck the report section references
after the mentor's edits.

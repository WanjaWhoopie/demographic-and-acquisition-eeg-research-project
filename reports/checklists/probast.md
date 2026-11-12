# PROBAST self-assessment (T12.2)

Wolff et al. (2019), *Annals of Internal Medicine* 170(1):51–58. Four domains, each rated for risk of
bias (RoB) and, for the first three, applicability concerns. Ratings: low · high · unclear.

**Note.** PROBAST was written for prediction-model studies. This project measures what a frozen
model encodes and whether its AD signal transfers between cohorts; it does not propose a clinical
model. The assessment is still useful because it names the weaknesses a reader should weigh.
An AI-specific update (PROBAST+AI) has since been published **[verify reference: Moons et al., 2025,
*BMJ*]**; consider re-rating with it if time allows.

## Summary

| Domain | Risk of bias | Applicability concern |
|---|---|---|
| 1 Participants | **high** | **high** |
| 2 Predictors | low | low |
| 3 Outcome | unclear | unclear |
| 4 Analysis | **high** (small samples) | – |
| **Overall** | **high** | **high** |

The overall rating follows PROBAST's rule: one high domain makes the study high risk of bias. This is
expected for any analysis built on small public case–control EEG datasets, and is stated in the
report's limitations (§5.4).

## Domain 1 – Participants
| Signalling question | Answer | Notes |
|---|---|---|
| 1.1 Appropriate data sources (e.g. cohort, RCT, nested case–control)? | **No** | All three are convenience case–control collections: people with a known AD diagnosis and recruited controls. AD prevalence (ADFSU 86%, APAVA 52%, ds004504 55%) reflects recruitment, not a target population. |
| 1.2 All inclusions and exclusions appropriate? | Probably yes | AD and HC only; FTD (ds004504) and ADSZ (duplicate of ADFSU, EXP-002) excluded by pre-set rules. Source-level inclusion criteria are only partly documented. |

**RoB: high.** **Applicability: high** – a case–control spectrum with clear-cut diagnoses overstates
discrimination compared with a memory-clinic population (mild cognitive impairment, other dementias, comorbidity).

## Domain 2 – Predictors
| Signalling question | Answer | Notes |
|---|---|---|
| 2.1 Predictors defined and assessed the same way for all participants? | Yes, after harmonisation | One pipeline for every cohort (D-012 to D-022). Recording hardware and settings still differ by cohort; that difference is the object of study. |
| 2.2 Predictors assessed without knowledge of outcome? | Yes | Fully automatic feature extraction; epoch rejection is amplitude-based and blind to diagnosis (it does reject more AD epochs in ds004504, EXP-003). |
| 2.3 All predictors available at the time the model is intended to be used? | Yes | Resting EEG only. |

**RoB: low.** **Applicability: low.**

## Domain 3 – Outcome
| Signalling question | Answer | Notes |
|---|---|---|
| 3.1 Outcome determined appropriately? | Probably yes | Clinical AD diagnosis from each source. |
| 3.2 Pre-specified or standard outcome definition? | Unclear | Diagnostic criteria differ by cohort and era (ds004504: DSM-IV/NINCDS-ADRDA per its descriptor **[verify]**; ADFSU: NINCDS-ADRDA and DSM-III-R (`docs/datasets.md`); APAVA: as reported by Escudero et al. (2006) **[verify]**). |
| 3.3 Predictors excluded from the outcome definition? | Yes | EEG was not part of the diagnoses as far as reported **[verify]**. |
| 3.4 Outcome defined the same way for all participants? | No | Three sources, three diagnostic processes. |
| 3.5 Outcome determined without knowledge of predictors? | Probably yes | Diagnoses predate this analysis. |
| 3.6 Appropriate interval between predictor and outcome? | Yes | Cross-sectional. |

**RoB: unclear.** **Applicability: unclear.** Different diagnostic definitions across cohorts are
part of the cohort effect this study measures; they cannot be separated from acquisition.

## Domain 4 – Analysis
| Signalling question | Answer | Notes |
|---|---|---|
| 4.1 Reasonable number of participants with the outcome? | **No** | 124 AD / 52 HC overall; the smallest held-out fold has 11 HC (APAVA) and the largest training class imbalance is ADFSU (76 / 12). Hundreds of candidate predictors per participant. |
| 4.2 Continuous and categorical predictors handled appropriately? | Yes | Continuous embeddings, standardised within training folds. |
| 4.3 All enrolled participants included? | Yes | 176 of 176 in the primary analysis; 175 in the 8-s analysis (one APAVA HC with one epoch). |
| 4.4 Missing data handled appropriately? | Yes | No missing EEG; demographics missing by design in two cohorts and not imputed. |
| 4.5 Selection of predictors avoided univariable analysis? | Yes | Representation chosen by inner-CV AUROC of the full model (D-024). |
| 4.6 Complexities in the data accounted for? | Yes | Participant-level splits (D-001); LOCO for centre effects. |
| 4.7 Relevant performance measures evaluated? | Partly | Discrimination with CIs throughout. Calibration was not a pre-specified outcome; the pooled vs per-fold AUROC gap (EXP-011) shows miscalibration between cohorts. |
| 4.8 Overfitting and optimism accounted for? | Yes | Nested CV; every transform fitted on training participants only (leakage tests in `tests/`). |
| 4.9 Predictors and weights correspond to the reported model? | Yes | Selected configurations and C per fold are reported (`T06_selected_configs.csv`, `T08_loco.csv`). |

**RoB: high**, driven by 4.1 (small samples, wide CIs) and 4.7 (no calibration analysis).

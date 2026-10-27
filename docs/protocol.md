# Study protocol (summary of the revised proposal)

This is the working, prespecified version of the design. The proposal document is the
authoritative text; if the two disagree, fix one of them and log it in `decision_log.md`.

## Question
When a frozen, self-supervised EEG foundation model (LaBraM) is used to classify Alzheimer's
disease (AD) versus healthy controls (HC), how much of the performance depends on
demographic (age, sex) and acquisition/cohort information, and how does removing that
information change cross-cohort generalisation?

- **H0:** removing nuisance information does not change within- or cross-cohort AD performance.
- **H1:** removing it significantly changes AD performance and/or generalisation.

## Cohorts
| Cohort | AD | HC | Channels | Rate | Eyes-closed EEG per person | Demographics |
|---|---|---|---|---|---|---|
| ds004504 | 36 | 29 | 19 | 500 Hz | 5–21 min | age, sex, MMSE |
| ADFSU (deduplicated) | 76 | 12 | 19 | 128 Hz | 8 s | none |
| APAVA | 12 | 11 | 16 | 256 Hz | 5–295 s | none |

176 participants in three cohorts. ADSZ was dropped because it is a subset of ADFSU (D-017, EXP-002);
FTD (ds004504) excluded from the primary analysis.

## Pipeline
1. Duplicate check (ADSZ vs ADFSU).
2. Eyes-closed only → 16 common channels → µV → 0.5–30 Hz (4th-order Butterworth, zero-phase, per
   segment) → common average → 200 Hz → 4-s epochs within segments → amplitude-based rejection →
   all clean epochs kept (D-018; equal 8-s crop as a sensitivity analysis).
3. Frozen LaBraM → epoch embeddings (every layer) → participant pooling → **Z**.
4. Branches on Z:
   - **A** linear AD classifier (vs classical band power + 1/f comparator);
   - **B** probes: age, sex (ds004504 only), cohort (all cohorts);
   - **C** nuisance control → **Z\*** → AD classifier.
5. Leave-one-cohort-out (LOCO, 3 folds) evaluation; participant bootstrap.

## Objectives → analyses
| Obj | Analysis | Where evaluated |
|---|---|---|
| O1 Baseline | Z → AD, logistic regression; classical comparator | within-cohort CV + LOCO |
| O2 Probe | Z → age (MAE, R²), sex (AUROC), cohort (bal. acc., macro-F1) | age/sex: ds004504; cohort: all |
| O3 Control | age/sex residualisation; prevalence-balanced cohort centring; LEACE/INLP | age/sex: ds004504; cohort: LOCO |
| O4 Generalise | ΔAUROC original vs controlled | LOCO + sensitivity analyses |
| O5 Interpret (exploratory) | band/channel perturbation, correlation of Z\* with theta/alpha, PAF, aperiodic exponent | all |

## Primary outcome
Mean ΔAUROC = AUROC(Z) − AUROC(Z\*acq) across the four LOCO folds, each fold reported with a
95% participant-bootstrap CI (paired). Z\*acq = cohort-controlled representation.

## Key rules
- The participant, never the epoch, is the unit of analysis and splitting.
- Every transform (scaler, residualiser, centring, eraser, layer choice, pooling choice,
  hyperparameters) is fitted on training participants only.
- Cohort centring of a held-out cohort is reported two ways: (i) pooled training mean
  (no test information); (ii) label-free test mean (transductive, declared as such).
- A representation controlled for both demographics and cohort is not built for LOCO
  (held-out cohorts have no age/sex).
- Sensitivity: LOCO without ADFSU; LOCO with ADFSU AD subsampled to 12 (100 draws); equal 8-s crop per participant (D-018); per-recording amplitude scaling (D-019).
- Report whichever pattern appears (A little change / B moderate drop / C large drop).

## Reporting
TRIPOD+AI (Collins et al., 2024) checklist and PROBAST (Wolff et al., 2019) self-assessment.

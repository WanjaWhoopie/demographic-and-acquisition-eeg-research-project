# EXP-003 – Preprocessing QC

## Before running (committed before results were seen)
- **Objective:** data (WORKPLAN T4.9)
- **Question:** After the common pipeline (16 channels → 0.5–30 Hz → average reference → 200 Hz → 4-s epochs → rejection), how comparable are the cohorts, and how much cohort information survives in *classical* spectral features?
- **Hypothesis:** amplitude differences shrink but do not vanish; cohort identity will still be decodable well above chance (1/3) from relative band power, because the cohorts differ in recording system, era and source processing. This number is the reference against which the LaBraM cohort probe (O2) is read.
- **Data:** all three cohorts, every included participant, all clean epochs.
- **Method:** `scripts/03_preprocess.py` per cohort, then `scripts/03_qc.py`:
  - per cohort × diagnosis: participants, epochs before/after rejection, rejection reasons, robust amplitude;
  - mean PSD per cohort × diagnosis on processed epochs;
  - visual check: 4-s traces of two random participants per cohort;
  - cohort probe: relative band power per channel (64 features, shape only) and the same plus log total power (amplitude), multinomial logistic regression, participant-grouped stratified 5-fold × 5 repeats, balanced accuracy.
- **Config:** `configs/preprocessing.yaml` (D-012, D-013, D-014, D-015, D-018, D-020, D-021)
- **Seed:** 20261001
- **What result would change our plan?** Rejection rates that differ strongly by diagnosis within a cohort (would be a confound to report); a cohort with many participants left with < 2 epochs; a PSD showing residual mains noise or filter artefacts inside 0.5–30 Hz.

## Run record
- **Date:** 2026-10-27
- **Commands:** `python scripts/03_preprocess.py --cohort {ds004504,ADFSU,APAVA}`; `python scripts/03_qc.py`
- **Outputs:** `results/tables/T03_preprocessing_qc.csv`, `T03_cohort_probe_classical.csv`, `results/figures/EXP-003_psd_processed.png`, `EXP-003_snippets.png`

## Results
(filled after the run)

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
| Cohort | Dx | n | Epochs kept / before | Rejected | Epochs per person (min / median / max) | Robust SD after (µV) |
|---|---|---|---|---|---|---|
| ds004504 | AD | 36 | 6407 / 7332 | 12.6 % (all amplitude) | 68 / 178 / 322 | 5.99 |
| ds004504 | HC | 29 | 5597 / 6096 | 8.2 % | 164 / 192 / 241 | 6.26 |
| ADFSU | AD | 76 | 152 / 152 | 0 % | 2 / 2 / 2 | 6.01 |
| ADFSU | HC | 12 | 24 / 24 | 0 % | 2 / 2 / 2 | 6.83 |
| APAVA | AD | 12 | 398 / 400 | 0.5 % | 10 / 33 / 59 | 6.21 |
| APAVA | HC | 11 | 263 / 263 | 0 % | 1 / 28 / 40 | 4.78 |

- No participant lost all epochs; one (APAVA HC-05) has a single epoch (excluded only in the 8-s sensitivity analysis, D-018).
- No flat-channel rejections anywhere; all rejections are > 150 µV peak-to-peak and nearly all are in ds004504, the only cohort that was not artefact-cleaned at source.
- **Amplitude converged.** Before preprocessing the cohorts' robust SDs were 18.3 / 7.7 / 4.9 µV; after the common pipeline they are 6.0–6.8 (ADFSU, ds004504) and 4.8–6.2 (APAVA). Most of the raw gap came from the reference (linked ears vs common average) and the 0.5–30 Hz band, not from the recordings' scale. D-019's amplitude-scaled sensitivity analysis remains in place.
- **Spectra** (`EXP-003_psd_processed.png`): every cohort shows the expected pattern: a 10-Hz alpha peak in HC and a flatter, slower spectrum in AD. No mains residue or filter ripple inside 0.5–30 Hz. ADFSU rolls off more steeply above 30 Hz (band-limited at source), which lies outside the analysis band.
- **Traces** (`EXP-003_snippets.png`): recognisable resting EEG in all cohorts (posterior alpha in HC, slow waves in AD); no clipped or dead channels among the sampled participants.

| Cohort probe on classical features (participant-grouped 5-fold × 5) | Balanced accuracy | Chance |
|---|---|---|
| relative band power, 16 channels × 4 bands (shape only) | **0.687 ± 0.093** | 0.333 |
| + log total power per channel (amplitude) | 0.704 ± 0.087 | 0.333 |

## Interpretation
- The pipeline makes the cohorts comparable in form (16 channels, 200 Hz, 4-s epochs, similar amplitude) but **cohort identity is still decodable at about 0.69 balanced accuracy from spectral shape alone**, twice chance. That is the floor for the LaBraM cohort probe (O2): if LaBraM embeddings decode cohort much better than 0.69, the model has picked up more acquisition information than classical features carry; if about the same, the cohort signal is spectral and visible to any method.
- Amplitude adds little on top of shape (+0.02), consistent with the amplitude convergence above.
- A confound to report: in ds004504, AD recordings lose more epochs to artefacts than HC (12.6 % vs 8.2 %). Rejection is per epoch, so this changes how many epochs each person contributes, not who is included; the 8-s sensitivity analysis (first two clean epochs each) is unaffected.
- Epoch counts per person differ by two orders of magnitude between cohorts (2 vs ~30 vs ~180), the risk recorded in D-018.

## Follow-ups
- Freeze the analysis plan (T4.0, tag `analysis-plan-v1`) once the mentor has signed off.
- In O2, compare the LaBraM cohort probe with the 0.687 reference here.

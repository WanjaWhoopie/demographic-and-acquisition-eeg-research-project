# EXP-002 – ADSZ–ADFSU overlap check

## Before running
- **Objective:** data (WORKPLAN Phase 3)
- **Question:** Do ADSZ and ADFSU share participants? Both trace to the FSU / Dennis Duke database.
- **Method:** `scripts/02_overlap_check.py` → `src/eegconf/overlap.py`. Per-channel exact matching
  (SHA-1 of values rounded to 0.001) scanning every sample offset, plus channel-level correlation
  (|r| > 0.999) to catch rescaled copies. Works without knowing ADSZ's channel order.
  A file matches a recording when ≥ 80% of its channels have a copy in that one recording.
- **What would change our plan?** Any overlap means the two cannot be separate LOCO cohorts.

## Run record
- **Date:** 2026-09-29 · ADFSU `EEG_data.zip` (osf.io/2v5md) · ADSZ `dataset.zip` (figshare 19091771)
- **Outputs:** `data/metadata/overlap_adsz_adfsu.csv`, `overlap_within_adfsu.csv` (local);
  `results/tables/T02_overlap_summary.csv`

## Results
| Check | Result |
|---|---|
| ADSZ files matched in ADFSU | **47 / 48, all exact** |
| Which ADFSU recordings | AD Paciente1–12 (eyes closed + open), Healthy Paciente1–12 (eyes closed + open) |
| Unmatched ADSZ file | `eeg24o1` (HC eyes open) – its ADFSU folder (Healthy/Eyes_open/Paciente5) is empty |
| Label / condition disagreements | 0 / 0 |
| ADSZ column order | F1(=Fp1) F2(=Fp2) F7 F3 Fz F4 F8 T3 C3 Cz C4 T4 T5 P3 Pz P4 T6 O1 O2 |
| Longer ADSZ files | 7 AD eyes-open files are 10–14 s; ADFSU holds their first 8 s |
| Duplicates inside ADFSU | AD Paciente40–44 identical (one recording, five IDs), eyes open and closed |
| Duplicate channels in ADFSU | F1 ≡ Fp1 and F2 ≡ Fp2 in all 182 recordings |

## Interpretation
ADSZ is not an independent cohort. Keeping both would place the same people in training and test
folds of leave-one-cohort-out. Proposed (D-017): drop ADSZ, deduplicate ADFSU (76 unique AD + 12 HC),
and run LOCO over ds004504, ADFSU and APAVA. An earlier inference from ADSZ alone ("3 AD people ×
4 segments") was wrong: the 12 AD codes are 12 different people.

# EXP-001 – Raw data audit

## Before running
- **Objective:** data (WORKPLAN Phase 2, checks A1–A12)
- **Question:** What exactly is in each download (channels, rate, units, duration, condition, reference, bad data, duplicates)?
- **Data:** ds004504 v1.0.9, AD + HC (36 + 29). Other cohorts once downloaded.
- **Method:** `scripts/01_audit.py` → `src/eegconf/audit.py`. Amplitude checks on a 1–30 Hz band-passed copy
  (raw recordings carry slow drift); duplicates by correlating cohort-centred log-PSD fingerprints (1–30 Hz).
- **What would change our plan?** Missing channels, wrong units, non-eyes-closed data, or duplicated participants.

## Run record – ds004504
- **Date:** 2026-09-29
- **Command:** `python scripts/01_audit.py --cohort ds004504`
- **Outputs:** `data/metadata/audit_ds004504.csv` (local), `results/tables/T00_audit_ds004504_summary.csv`,
  `results/figures/EXP-001_ds004504_psd.png`

## Results – ds004504
| Check | Result |
|---|---|
| Recordings | 65 (36 AD, 29 HC), all `task-eyesclosed` |
| Channels / rate | 19 channels in identical order; all 16 target channels present; 500 Hz |
| Reference / online filter | A1 A2; 0.4–50 Hz; 50 Hz line |
| Duration | 307–1291 s (median 827 s) |
| Units | robust SD 18.3 µV median after 1–30 Hz band-pass (raw 86.7 µV because of drift) – plausible in all 65 |
| Bad data | no NaN/Inf, flat or clipped channels |
| Extreme amplitude | 13 recordings with > 1% samples above 150 µV in some channel → handled by epoch rejection |
| Line noise | strong at 50 Hz (median +19.6 dB) – outside the analysis band |
| Duplicates | 1 spectral pair (sub-024/sub-028, r = 0.94) ruled out: different sex/age, max time-domain r = 0.24 |

## Interpretation
ds004504 matches its documentation. Group-mean spectra show the expected AD slowing (more 4–8 Hz power,
weaker 10 Hz alpha peak). AD recordings also carry more power above 30 Hz (likely muscle), which the
30-Hz low-pass removes.

## Follow-ups
- Run the same audit on ADFSU, ADSZ and APAVA once their loaders exist.

# EXP-001 – Raw data audit

## Before running
- **Objective:** data (WORKPLAN Phase 2, checks A1–A12)
- **Question:** What exactly is in each download (channels, rate, units, duration, condition, reference, bad data, duplicates)?
- **Data:** ds004504 v1.0.9 (36 AD + 29 HC); ADFSU osf.io/2v5md after EXP-002 cleaning (76 AD + 12 HC, eyes closed, F1/F2 dropped); APAVA.zip (12 AD + 11 HC, 5-s trials rebuilt from 1-s windows).
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

## Run record – ADFSU and APAVA
- **Date:** 2026-10-27 · `python scripts/01_audit.py --cohort ADFSU` / `--cohort APAVA`
- Audit now works per *segment* (APAVA has many 5-s trials per person); per-participant values are
  the median over segments (amplitude) or the worst segment (flat, clipping, extreme). Clipping is
  defined as a run of ≥ 4 samples at the channel's extreme (quantised data such as ADFSU repeat
  their maximum at scattered positions, which is not saturation).

## Results – ADFSU
| Check | Result |
|---|---|
| Recordings | 88 (76 AD, 12 HC), all eyes closed, 8.0 s each |
| Channels / rate | 19 channels in identical order; all 16 target channels present; 128 Hz |
| Units | robust SD 7.7 after 1–30 Hz (stored unit undocumented; treated as µV, D-019) |
| Bad data | no NaN, flat or extreme segments |
| Clipping | AD-03 (O1) and AD-31 (F3) sit at their extreme for exactly 4 samples – borderline, left to epoch rejection |
| Prior processing | 40–48 Hz is 7.2 dB below 20–30 Hz: source band-limiting (0.5–30 Hz) confirmed |
| Duplicates (within cohort) | none after removing AD-41..44 |

## Results – APAVA
| Check | Result |
|---|---|
| Participants | 23 (12 AD, 11 HC); 1–59 five-second trials each (5–295 s, median 160 s) |
| Channels / rate | 16 channels (10–20 minus Fz, Cz, Pz); 256 Hz; common-average referenced at source |
| Units | robust SD 4.9 after 1–30 Hz (AD 5.9, HC 4.2); HC-22 at 2.9, just under the 3 µV floor |
| Bad data | no NaN, flat or clipped channels |
| Extreme amplitude | AD-08: one 5-s trial with a channel 21% beyond ±150 µV; the person's other trials are normal → epoch rejection removes that trial |
| Line noise | weak 50-Hz peak (+6.5 dB), outside the analysis band |
| Duplicates | none |

## Interpretation (all cohorts)
All three cohorts match their documentation after the EXP-002 cleaning. Amplitudes differ
systematically between cohorts (ds004504 18.3 µV, ADFSU 7.7, APAVA 4.9 after 1–30 Hz), which is
handled by D-019. No participant needs to be excluded on audit grounds; the few extreme segments
are removed by the prespecified epoch-rejection rule.

## Follow-ups
- Preprocessing QC (EXP-003) should confirm that per-cohort amplitude and PSD differences shrink after
  the common pipeline, and report rejected-epoch counts by cohort and diagnosis.

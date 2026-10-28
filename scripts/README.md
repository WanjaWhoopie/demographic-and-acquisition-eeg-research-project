# scripts/

Command-line entry points, one per pipeline stage, each reading a config from `configs/`:

| Script | Stage | WORKPLAN | Exists |
|---|---|---|---|
| `download_ds004504.py` | selective download of ds004504 (AD + HC raw, 2.16 GB) | T2.1.2 | yes |
| `00_participants.py` | combined participant table + cohort summary | T2.5 | yes |
| `01_audit.py --cohort X` | inventory + QC of raw data (A1–A12) | Phase 2 | yes |
| `02_overlap_check.py` | ADSZ–ADFSU duplicate detection | Phase 3 | yes |
| `03_preprocess.py` | harmonised preprocessing | Phase 4 | not yet |
| `04_extract_embeddings.py --cohort X [--random]` | frozen LaBraM features (GPU) | Phase 5 | yes |
| `04_sanity.py` | embedding sanity checks | T5.4 | yes |
| `05_classical_features.py` | band power + aperiodic exponent | Phase 6 | not yet |
| `06_run_experiment.py --exp EXP-xxx` | probes / classifiers / control / LOCO | Phases 6–9 | not yet |
| `07_stats.py --exp EXP-xxx` | bootstrap CIs, ΔAUROC | Phase 10 | not yet |

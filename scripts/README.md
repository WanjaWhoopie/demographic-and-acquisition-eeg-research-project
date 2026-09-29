# scripts/

Command-line entry points, one per pipeline stage, each reading a config from `configs/`:

| Script | Stage | WORKPLAN |
|---|---|---|
| `01_audit.py` | inventory + QC of raw data | Phase 2 |
| `02_overlap_check.py` | ADSZ–ADFSU duplicate detection | Phase 3 |
| `03_preprocess.py` | harmonised preprocessing | Phase 4 |
| `04_extract_embeddings.py` | frozen LaBraM features | Phase 5 |
| `05_classical_features.py` | band power + aperiodic exponent | Phase 6 |
| `06_run_experiment.py --exp EXP-xxx` | probes / classifiers / control / LOCO | Phases 6–9 |
| `07_stats.py --exp EXP-xxx` | bootstrap CIs, ΔAUROC | Phase 10 |

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
| `05_build_features.py` | participant-level LaBraM representations + classical features | T5.3, T6.4 | yes |
| `06_baseline.py` | within-cohort, LOCO, classical, nuisance-only, random-weights (EXP-010–013) | Phase 6 | yes |
| `07_probes.py` | age, sex, cohort probes, layer profile, MLP (EXP-020–022); `--only-mlp` re-runs EXP-022 alone | Phase 7 | yes |
| `07_stats.py --exp EXP-xxx` | bootstrap CIs, ΔAUROC | Phase 10 | not yet |

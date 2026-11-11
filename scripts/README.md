# scripts/

Command-line entry points, one per pipeline stage, each reading a config from `configs/`:

| Script | Stage | WORKPLAN | Exists |
|---|---|---|---|
| `download_ds004504.py` | selective download of ds004504 (AD + HC raw, 2.16 GB) | T2.1.2 | yes |
| `00_participants.py` | combined participant table + cohort summary | T2.5 | yes |
| `01_audit.py --cohort X` | inventory + QC of raw data (A1–A12) | Phase 2 | yes |
| `02_overlap_check.py` | ADSZ–ADFSU duplicate detection | Phase 3 | yes |
| `03_preprocess.py` | harmonised preprocessing | Phase 4 | not yet |
| `04_extract_embeddings.py --cohort X [--random \| --amplitude-scaled]` | frozen LaBraM features (GPU); `--amplitude-scaled` for EXP-044 | Phase 5 | yes |
| `04_sanity.py` | embedding sanity checks | T5.4 | yes |
| `05_build_features.py [--scaled-only]` | participant-level LaBraM representations + classical features; `--scaled-only` for EXP-044 | T5.3, T6.4 | yes |
| `06_baseline.py` | within-cohort, LOCO, classical, nuisance-only, random-weights (EXP-010–013) | Phase 6 | yes |
| `07_probes.py` | age, sex, cohort probes, layer profile, MLP (EXP-020–022); `--only-mlp` re-runs EXP-022 alone | Phase 7 | yes |
| `08_control.py` | age/sex residualisation, cohort centring (i, ii), LEACE, INLP; ΔAUROC and verification probes (EXP-030–032); `--quick` smoke test; `--only-demographic` re-runs EXP-030 and saves its predictions | Phase 8 | yes |
| `09_sensitivity.py` | primary outcome and pattern (EXP-040); sensitivity without ADFSU, ADFSU subsampled, 8 s, amplitude-scaled (EXP-041–044); `--part` runs one | Phase 9 | yes |
| `10_stats.py` | reproduces headline numbers from saved predictions; bootstrap p-values, Holm, DeLong cross-check | Phase 10 | yes |
| `11_data_amount.py` | EXP-053: AD transfer, within-cohort AUROC and cohort probe against epochs per participant (exploratory) | Phase 11 | yes |
| `07_stats.py --exp EXP-xxx` | bootstrap CIs, ΔAUROC | Phase 10 | not yet |

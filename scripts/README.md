# scripts/

Command-line entry points, one per pipeline stage, each reading a config from `configs/`:

| Script | Stage | WORKPLAN | Exists |
|---|---|---|---|
| `download_ds004504.py` | selective download of ds004504 (AD + HC raw, 2.16 GB) | T2.1.2 | yes |
| `00_participants.py` | combined participant table + cohort summary | T2.5 | yes |
| `01_audit.py --cohort X` | inventory + QC of raw data (A1–A12) | Phase 2 | yes |
| `02_overlap_check.py` | ADSZ–ADFSU duplicate detection | Phase 3 | yes |
| `02_overlap_recheck.py` | independent re-check of the ADSZ–ADFSU duplication: direct float equality, no shared code with `02_overlap_check.py` | Phase 3 | yes |
| `03_preprocess.py --cohort X` | harmonised preprocessing | Phase 4 | yes |
| `03_qc.py` | preprocessing QC: epochs kept, amplitude, PSD, classical cohort probe (EXP-003) | T4.9 | yes |
| `04_extract_embeddings.py --cohort X [--random \| --amplitude-scaled \| --band-stop B \| --occlude C]` | frozen LaBraM features (GPU); `--amplitude-scaled` for EXP-044, `--band-stop` for EXP-050, `--occlude` (channel or region) for EXP-051 | Phase 5 | yes |
| `04_sanity.py` | embedding sanity checks | T5.4 | yes |
| `05_build_features.py [--scaled-only]` | participant-level LaBraM representations + classical features; `--scaled-only` for EXP-044 | T5.3, T6.4 | yes |
| `06_baseline.py` | within-cohort, LOCO, classical, nuisance-only, random-weights (EXP-010–013) | Phase 6 | yes |
| `07_probes.py` | age, sex, cohort probes, layer profile, MLP (EXP-020–022); `--only-mlp` re-runs EXP-022 alone | Phase 7 | yes |
| `08_control.py` | age/sex residualisation, cohort centring (i, ii), LEACE, INLP; ΔAUROC and verification probes (EXP-030–032); `--quick` smoke test; `--only-demographic` re-runs EXP-030 and saves its predictions | Phase 8 | yes |
| `09_sensitivity.py` | primary outcome and pattern (EXP-040); sensitivity without ADFSU, ADFSU subsampled, 8 s, amplitude-scaled (EXP-041–044); `--part` runs one | Phase 9 | yes |
| `10_stats.py` | reproduces headline numbers from saved predictions; bootstrap p-values, Holm, DeLong cross-check | Phase 10 | yes |
| `11_data_amount.py` | EXP-053: AD transfer, within-cohort AUROC and cohort probe against epochs per participant (exploratory) | Phase 11 | yes |
| `11_random_epochs.py` | EXP-054: first, middle or last 8 epochs vs randomly drawn epochs; separates time in recording from amount of data (exploratory) | Phase 11 | yes |
| `11_interpret.py` | EXP-050 band perturbation (needs `--band-stop` embeddings), EXP-051 channel occlusion (needs `--occlude` embeddings), EXP-052 score vs EEG markers (exploratory) | Phase 11 | yes |
| `13_review_analyses.py --part fixed_block` / `--part pooled` | EXP-055 fixed-block comparison and EXP-056 pooled positive control (review-prompted, D-039) | Phase 11 | yes |
| `12_figures.py` | Report figures F5 (LOCO AUROC by control) and F6 (ΔAUROC across analyses) from committed tables | Phase 12 | yes |
| `12_workbook.py` | Excel workbook with one sheet per experiment, copied from the committed tables (`results/experiments_summary.xlsx`, local only); needs `pandas` and `openpyxl` | Phase 12 | yes |

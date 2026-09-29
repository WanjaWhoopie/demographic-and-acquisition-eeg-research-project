# data/

Nothing in this folder is committed except this file. Each dataset keeps its own licence;
redistribute nothing.

```
data/
  raw/<cohort>/          untouched downloads, exactly as released (read-only)
  interim/<cohort>/      after condition selection + channel mapping + units (MNE .fif)
  processed/<cohort>/    filtered, re-referenced, resampled, epoched, cropped (MNE -epo.fif)
  embeddings/<model>/    frozen LaBraM outputs per epoch and layer (.npz)
  metadata/              participants_all.csv, overlap_report.csv, qc_report.csv (committed copies live in results/tables/)
```

Cohort folder names: `ds004504`, `ADFSU`, `ADSZ`, `APAVA` (match `configs/datasets.yaml`).

Record for every download in `docs/datasets.md`: source URL, version or date, licence, checksum
of the archive (`sha256sum`).

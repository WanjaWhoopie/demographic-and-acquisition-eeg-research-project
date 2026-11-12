# data/

Nothing in this folder is committed except this file. Each dataset keeps its own licence;
redistribute nothing.

```
data/
  raw/<cohort>/          untouched downloads, exactly as released (read-only)
  processed/<cohort>/    filtered, re-referenced, resampled, epoched clean EEG per participant (.npz, 03_preprocess.py)
  embeddings/<model>/    frozen LaBraM outputs per epoch and block (.npz, 04_extract_embeddings.py)
  features/              participant-level representations and classical features (.npz, 05_build_features.py)
  metadata/              participant and preprocessing tables (committed aggregates live in results/tables/)
```

Cohort folder names: `ds004504`, `ADFSU`, `ADSZ`, `APAVA` (match `configs/datasets.yaml`).

Record for every download in `docs/datasets.md`: source URL, version or date, licence, checksum
of the archive (`sha256sum`).

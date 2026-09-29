# Experiments

Every run that produces a number we might report is an experiment with an ID.

- `registry.csv` – one row per experiment (planned ones included). Update `status` and
  `git_commit` when it runs.
- `EXP-xxx/README.md` – copy `_template/README.md`, fill *before* running (question,
  hypothesis, config), then fill results and interpretation after.
- Raw outputs go to `results/runs/EXP-xxx/` (not committed); curated tables/figures to
  `results/tables|figures/` with the experiment ID in the filename.

## Numbering
| Range | Area |
|---|---|
| 000–009 | data audit, overlap, preprocessing QC |
| 010–019 | O1 baseline classification |
| 020–029 | O2 probes |
| 030–039 | O3 nuisance control |
| 040–049 | O4 cross-cohort + sensitivity |
| 050–059 | O5 interpretation (exploratory) |
| 090–099 | robustness / reviewer requests |

## Rules
1. Fill the pre-run half of the README and commit it **before** running on held-out cohorts.
2. Record the git commit, config file, data version and seed of the run.
3. Never overwrite a run; a re-run gets a suffix (`EXP-011b`) and a line saying why.
4. Negative and null results are recorded exactly like positive ones.

# Demographic and Acquisition-Related Information Disentanglement in Self-Supervised EEG Foundation Models for Cross-Cohort Alzheimer's Disease Classification

EEG is low-cost and non-invasive. Pretrained models can learn transferable structure from
thousands of hours of unlabelled recordings. But when a frozen EEG foundation model separates
Alzheimer's disease (AD) from healthy controls, is it using disease neurophysiology, or
age, sex and the signature of the cohort/recording system?

This project measures how much demographic and acquisition information is encoded in frozen
LaBraM representations, removes it, and tests whether AD classification still transfers to an
unseen cohort (leave-one-cohort-out across ds004504, ADFSU and APAVA; ADSZ turned out to be a subset of ADFSU and was dropped).

**Start here:** [`docs/protocol.md`](docs/protocol.md) (design) · [`WORKPLAN.md`](WORKPLAN.md) (tasks) ·
[`docs/decision_log.md`](docs/decision_log.md) (prespecified choices) ·
[`reports/data_audit_report.md`](reports/data_audit_report.md) (what the data turned out to contain)

## Status (12 November 2026)
Analysis plan frozen on 11 November 2026 (git tag `analysis-plan-v1`).

| Phase | State |
|---|---|
| 0 Setup, data-use terms, leakage tests | done |
| 1 Literature review | ongoing: 29 papers in the matrix, draft review written, verification list open |
| 2 Data acquisition and audit | done for all three cohorts (EXP-001) |
| 3 Overlap check | done (EXP-002): ADSZ is a subset of ADFSU and was dropped |
| 4 Preprocessing | done (EXP-003): cohorts harmonised; cohort still decodable from spectral shape at 0.69 |
| 5 LaBraM embeddings | done: all 176 participants, pretrained + random-weights control, on the local GPU |
| 6 Baseline classification | done (EXP-010–013): LaBraM LOCO AUROC 0.85; classical features 0.90; untrained LaBraM 0.84 |
| 7 Nuisance probes | done (EXP-020–022): age and sex not decodable in ds004504; cohort decodable from LaBraM at 0.88 balanced accuracy vs 0.77 for classical features and untrained LaBraM |
| 8 Nuisance control | done (EXP-030–032): removing cohort information did not hurt cross-cohort AD transfer; centring raised mean LOCO AUROC 0.853 → 0.887 (Δ −0.034 [−0.069, −0.001]); LEACE 0.883, INLP 0.876 |
| 9 Primary outcome and sensitivity | done (EXP-040–044): removing cohort information never reduced cross-cohort AD performance; the small improvement in the primary analysis did not hold with 8 s per participant or equalised amplitude (pattern A in both) |
| 10 Statistics | done: primary ΔAUROC −0.034, p = 0.046; no secondary comparison significant after Holm; DeLong agrees with the bootstrap CIs; every headline number reproduced from saved predictions |
| 11 Neurophysiological interpretation (exploratory) | done (EXP-050, 052–054): the cross-cohort AD score is mainly a theta-slowing signal and tracks classical markers closely; no reliable effect of where in the recording the EEG comes from, and which epochs are pooled matters about as much as how many; channel occlusion deferred |
| 12 Writing and reporting | in progress: first full report draft (`reports/writeup/final_report.md`), TRIPOD+AI and PROBAST drafts (`reports/checklists/`), figures F5–F6 |

Cohorts in use: ds004504 (36 AD / 29 HC), ADFSU deduplicated (76 / 12), APAVA (12 / 11) = 176 participants.

## Repository layout
```
docs/              protocol, dataset cards, decision log, data-use terms (licences/)
literature/        review matrix (CSV), per-paper notes, gap synthesis, claims to verify
experiments/       experiment registry + one README per experiment
configs/           datasets, preprocessing and analysis parameters (YAML)
src/eegconf/       analysis package (io, preprocessing, features, representation,
                   probing, control, evaluation, stats, viz)
scripts/           pipeline entry points, one per stage
notebooks/         exploration only
tests/             leakage, audit and overlap unit tests (run on every push: .github/workflows)
data/              local only, never committed (see data/README.md)
results/           tables/ and figures/ committed; runs/ local only
reports/           data audit report, meeting notes, write-up drafts
WORKPLAN.md        phase-by-phase task list
```

## Setup
```bash
conda env create -f environment.yml
conda activate eegconf
pytest
```
Data download instructions are in `WORKPLAN.md` Phase 2 and `docs/datasets.md`. Run scripts from the
repository root with the `eegconf` environment active (on Windows, `conda run -n eegconf python scripts/...`).

## Reproduce the results
Data are not in the repository. Download the three cohorts as described in `docs/datasets.md` into
`data/raw/`, and clone LaBraM into `external/LaBraM` at commit `c431221` (its `checkpoints/labram-base.pth`
has sha256 `7c505838…57c37c`; WORKPLAN T5.1). The exact package versions are in `docs/env_lock.yml`.
Then run, from the repository root (each step writes the tables and figures named in its docstring):

| Step | Command | Produces |
|---|---|---|
| Participants | `python scripts/00_participants.py` | `T01_cohort_summary.csv` |
| Audit, overlap | `python scripts/01_audit.py --cohort <c>`; `python scripts/02_overlap_check.py` | `T00_*`, `T02_*` (EXP-001, 002) |
| Preprocess | `python scripts/03_preprocess.py --cohort <c>`; `python scripts/03_qc.py` | `T03_*`, F3 (EXP-003) |
| Embeddings (GPU) | `python scripts/04_extract_embeddings.py --cohort <c>` and again with `--random`, `--amplitude-scaled`, `--band-stop <band>`; `python scripts/04_sanity.py` | `T04_*` |
| Features | `python scripts/05_build_features.py`; `python scripts/05_build_features.py --scaled-only` | participant features (local) |
| Baseline | `python scripts/06_baseline.py` | `T06_*` (EXP-010–013) |
| Probes | `python scripts/07_probes.py` | `T07_*`, F4 (EXP-020–022) |
| Control | `python scripts/08_control.py` | `T08_*` (EXP-030–032) |
| Primary + sensitivity | `python scripts/09_sensitivity.py` | `T09_*` (EXP-040–044) |
| Statistics | `python scripts/10_stats.py` | `T10_*` |
| Interpretation | `python scripts/11_data_amount.py`; `python scripts/11_random_epochs.py`; `python scripts/11_interpret.py` | `T11_*`, F7 (EXP-050–054) |
| Report figures | `python scripts/12_figures.py` | F5, F6 |
| Results workbook | `python scripts/12_workbook.py` (needs `openpyxl`) | `results/experiments_summary.xlsx`, one sheet per experiment (not committed) |

`<c>` is each of `ds004504`, `ADFSU`, `APAVA`. The analysis seed is in `configs/analysis.yaml`. Steps 06–11
use 20 CPU workers by default (`--n-jobs`); the longest runs take one to two hours.

## Pipeline at a glance
1. Download and audit each cohort; resolve the ADSZ–ADFSU overlap (done).
2. Eyes-closed → 16 common channels → 0.5–30 Hz (zero-phase Butterworth) → average reference →
   200 Hz → 4-s epochs → amplitude-based rejection; all clean epochs kept (8-s crop as a sensitivity analysis).
3. Frozen LaBraM embeddings → participant-level representation **Z**.
4. **A** AD classifier · **B** probes for age, sex (ds004504) and cohort · **C** nuisance-controlled **Z\*** → AD classifier.
5. Leave-one-cohort-out over three cohorts; primary outcome = mean per-fold ΔAUROC(Z, Z\*).

## Working together
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branches, commit messages, and how to log papers and experiments.

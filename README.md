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

## Status (27 October 2026)
| Phase | State |
|---|---|
| 0 Setup, data-use terms, leakage tests | done (branch model still to agree; PyTorch duplicate to tidy before Phase 5) |
| 1 Literature review | ongoing: 29 papers in the matrix, draft review written, verification list open |
| 2 Data acquisition and audit | done for all three cohorts (EXP-001) |
| 3 Overlap check | done (EXP-002): ADSZ is a subset of ADFSU and was dropped |
| 4 Preprocessing | next |

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

## Pipeline at a glance
1. Download and audit each cohort; resolve the ADSZ–ADFSU overlap (done).
2. Eyes-closed → 16 common channels → 0.5–30 Hz (zero-phase Butterworth) → average reference →
   200 Hz → 4-s epochs → amplitude-based rejection; all clean epochs kept (8-s crop as a sensitivity analysis).
3. Frozen LaBraM embeddings → participant-level representation **Z**.
4. **A** AD classifier · **B** probes for age, sex (ds004504) and cohort · **C** nuisance-controlled **Z\*** → AD classifier.
5. Leave-one-cohort-out over three cohorts; primary outcome = mean per-fold ΔAUROC(Z, Z\*).

## Working together
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branches, commit messages, and how to log papers and experiments.

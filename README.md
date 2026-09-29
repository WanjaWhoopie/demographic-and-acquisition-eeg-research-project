# Demographic and Acquisition-Related Information Disentanglement in Self-Supervised EEG Foundation Models for Cross-Cohort Alzheimer's Disease Classification

EEG is low-cost and non-invasive. Pretrained models can learn transferable structure from
thousands of hours of unlabelled recordings. But when a frozen EEG foundation model separates
Alzheimer's disease (AD) from healthy controls, is it using disease neurophysiology, or
age, sex and the signature of the cohort/recording system?

This project measures how much demographic and acquisition information is encoded in frozen
LaBraM representations, removes it, and tests whether AD classification still transfers to an
unseen cohort (leave-one-cohort-out across ds004504, ADFSU, ADSZ and APAVA).

**Start here:** [`docs/protocol.md`](docs/protocol.md) (design) · [`WORKPLAN.md`](WORKPLAN.md) (tasks) ·
[`docs/decision_log.md`](docs/decision_log.md) (prespecified choices)

## Repository layout
```
docs/              protocol, dataset cards, decision log, data licences
literature/        review matrix (CSV), per-paper notes, gap synthesis, claims to verify
experiments/       experiment registry + one README per experiment
configs/           datasets, preprocessing and analysis parameters (YAML)
src/eegconf/       analysis package (io, preprocessing, features, representation,
                   probing, control, evaluation, stats, viz)
scripts/           pipeline entry points, one per stage
notebooks/         exploration only
tests/             leakage and harmonisation unit tests
data/              local only, never committed (see data/README.md)
results/           tables/ and figures/ committed; runs/ local only
reports/           meeting notes, progress updates, write-up drafts
WORKPLAN.md        phase-by-phase task list
```

## Setup
```bash
conda env create -f environment.yml
conda activate eegconf
pytest
```
Data download instructions are in `WORKPLAN.md` Phase 2 and `docs/datasets.md`.

## Pipeline at a glance
1. Audit and download each cohort; resolve ADSZ–ADFSU overlap.
2. Eyes-closed → 16 common channels → 0.5–30 Hz → average reference → 200 Hz → 4-s epochs →
   equal number of epochs per participant.
3. Frozen LaBraM embeddings → participant-level representation **Z**.
4. **A** AD classifier · **B** probes for age, sex (ds004504) and cohort · **C** nuisance-controlled **Z\*** → AD classifier.
5. Leave-one-cohort-out; primary outcome = mean per-fold ΔAUROC(Z, Z\*).

## Working together
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branches, commit messages, and how to log papers and experiments.

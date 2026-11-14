# Demographic and Acquisition-Related Information Disentanglement in Self-Supervised EEG Foundation Models for Cross-Cohort Alzheimer's Disease Classification

EEG is low-cost and non-invasive. Pretrained models can learn transferable structure from
thousands of hours of unlabelled recordings. But when a frozen EEG foundation model separates
Alzheimer's disease (AD) from healthy controls, is it using disease neurophysiology, or
age, sex and the signature of the cohort/recording system?

This project measures how much demographic and acquisition information is encoded in frozen
LaBraM representations, removes it, and tests whether AD classification still transfers to an
unseen cohort: leave-one-cohort-out across three public cohorts, ds004504 (Greece), ADFSU (USA)
and APAVA (Spain), 176 participants. A fourth public cohort, ADSZ, turned out to be a copy of part
of ADFSU and was dropped.

**Start here:** [`docs/protocol.md`](docs/protocol.md) (design) · [`WORKPLAN.md`](WORKPLAN.md) (tasks) ·
[`docs/decision_log.md`](docs/decision_log.md) (every choice, and whether it was made before or after seeing results) ·
[`reports/writeup/final_report.md`](reports/writeup/final_report.md) (the full write-up) ·
[`experiments/registry.csv`](experiments/registry.csv) (one line per experiment)

## What we found

Each experiment has its own folder under `experiments/` with the design committed before the run, the
run record and the result. In short:

1. **Two "independent" public AD datasets are the same people** ([EXP-002](experiments/EXP-002/README.md)).
   Before using ADSZ and ADFSU as separate cohorts we compared every file. 47 of ADSZ's 48 files are
   byte-for-byte copies of ADFSU recordings (12 AD and 12 HC people), confirmed twice by independent
   methods. ADSZ was dropped. A published AD foundation model (LEAD) and a 2026 review count the two
   as separate datasets, so a benchmark can test the same 24 people twice.

2. **Frozen LaBraM transfers across cohorts, but no better than band power** ([EXP-010–013](experiments/EXP-011/README.md)).
   Trained on two cohorts and tested on the third, the frozen model reached mean AUROC 0.853
   [0.773, 0.922]. Classical spectral features (band power and the aperiodic slope) reached 0.900, and
   the same network with random weights 0.838. The classifier chose the first transformer block in every fold.

3. **Cohort is strongly encoded; age and sex were not detectable** ([EXP-020–022](experiments/EXP-021/README.md)).
   A linear probe reads which cohort a recording came from at balanced accuracy 0.88 (chance 0.33),
   against 0.77 from classical features or the untrained network, and the information grows with depth.
   Age and sex could only be probed in ds004504 (65 people) and were at chance there, which at that
   sample size means "not detectable", not "absent".

4. **Removing cohort information did not reduce cross-cohort AD performance, and the apparent gain was a layer switch**
   ([EXP-030–032](experiments/EXP-031/README.md), [EXP-040](experiments/EXP-040/README.md), [EXP-055](experiments/EXP-055/README.md)).
   Prevalence-balanced cohort centring, LEACE and INLP were each refitted inside every training fold.
   The pre-registered primary outcome was a small improvement after centring (0.853 → 0.887, ΔAUROC
   −0.034 [−0.069, −0.001], p = 0.046). The mentor's review pointed out that the controlled classifier
   had switched to deeper blocks. Holding the block fixed showed why: deep blocks transfer better with
   or without control (0.908 at block 11, uncontrolled), removal at the block in use changes nothing
   (−0.009 [−0.027, 0.008]), and removal never helps at any block. The supportable statement is a
   bound: **removing cohort information changes cross-cohort AD performance by less than 0.03.**

5. **The classifier barely takes the cohort shortcut even when offered one** ([EXP-056](experiments/EXP-056/README.md)).
   As a positive control, pooled cross-validation over all 176, where cohort identity alone predicts AD
   at 0.65, gave the classifier a shortcut. It used almost none of it (pooled AUROC 0.935 against 0.910
   within cohorts). Centring therefore had nothing to remove; LEACE lowered pooled AUROC by 0.04 without
   touching within-cohort performance; INLP also cost within-cohort accuracy.

6. **The small gain was fragile in every direction** ([EXP-041–044](experiments/EXP-043/README.md)).
   With 8 s of EEG per participant, or with every recording scaled to the same amplitude, the gain
   disappeared; with ADFSU's AD group subsampled it halved. No secondary comparison survived Holm correction.

7. **What transfers is posterior theta slowing** ([EXP-050](experiments/EXP-050/README.md), [EXP-051](experiments/EXP-051/README.md), [EXP-052](experiments/EXP-052/README.md)).
   Removing the theta band from the held-out EEG cost the most (ΔAUROC +0.066); zeroing the six posterior
   channels cost 0.196, against 0.052 for the six frontal ones. The classifier's score correlated with the
   theta/alpha ratio at up to ρ = 0.91, within diagnostic groups as well as between them.

8. **Recording length is a cohort variable, and which epochs you pool matters as much as how many**
   ([EXP-053](experiments/EXP-053/README.md), [EXP-054](experiments/EXP-054/README.md)). Pooling fewer
   epochs transferred slightly better across cohorts (below the pre-set threshold), different random
   subsets of 8 epochs moved AUROC by ±0.03 within a cohort and by up to 0.15 in one fold, and there was
   no reliable effect of where in the recording the EEG came from. Within one dataset LEAD found the
   opposite (longer helps); between cohorts, where length differs 100-fold, this is the first test we know of.

**Bottom line.** Frozen LaBraM knows which cohort a recording came from, but its cross-cohort AD signal
does not depend on that: removing cohort information at the representation in use changes performance
by less than 0.03. What transfers is largely the classical posterior slowing of the AD EEG, which simple
spectral features capture as well. Demographic effects could not be assessed with the data available.

## Status (14 November 2026)
Analysis plan frozen on 11 November 2026 (git tag `analysis-plan-v1`, an internal time-stamped plan, not an
external registration). Everything after that is in the decision log with a before/after column.

| Phase | State |
|---|---|
| 0 Setup, data-use terms, leakage tests | done |
| 1 Literature review | 50 papers in the matrix, each cited claim checked against its primary source; a few items still open in `literature/to_verify.md` |
| 2 Data acquisition and audit | done for all three cohorts (EXP-001) |
| 3 Overlap check | done (EXP-002): ADSZ is a copy of part of ADFSU and was dropped; re-checked independently |
| 4 Preprocessing | done (EXP-003): cohorts harmonised; cohort still decodable from spectral shape at 0.69 |
| 5 LaBraM embeddings | done: all 176 participants, pretrained + random-weights control, on the local GPU |
| 6 Baseline classification | done (EXP-010–013): LaBraM LOCO AUROC 0.853; classical features 0.900; untrained LaBraM 0.838 |
| 7 Nuisance probes | done (EXP-020–022): age and sex not detectable in ds004504; cohort decodable from LaBraM at 0.88 vs 0.77 for classical features and untrained LaBraM |
| 8 Nuisance control | done (EXP-030–032): centring 0.853 → 0.887 (Δ −0.034 [−0.069, −0.001]); LEACE 0.883, INLP 0.876; LEACE put the cohort probe at chance |
| 9 Primary outcome and sensitivity | done (EXP-040–044): the primary gain did not hold with 8 s per participant or equalised amplitude |
| 10 Statistics | done: p = 0.046 for the primary; nothing secondary survives Holm; DeLong agrees with the bootstrap; every headline number reproduced from saved predictions |
| 11 Interpretation and review-prompted checks | done (EXP-050–056): posterior theta slowing; recording length as a cohort variable; fixed-block comparison shows the primary gain was a layer switch; positive control shows the shortcut was barely used |
| 12 Writing and reporting | report draft revised after the mentor's review (`reports/writeup/final_report.md`); TRIPOD+AI and PROBAST done (`reports/checklists/`); results deck and workbook kept outside git; final read-through and `final-v1` tag still to do |

Cohorts in use: ds004504 (36 AD / 29 HC), ADFSU deduplicated (76 / 12), APAVA (12 / 11) = 176 participants.

## Repository layout
```
docs/              protocol, dataset cards, decision log, data-use terms (licences/)
literature/        review matrix (CSV), per-paper notes, gap synthesis, claims to verify
experiments/       experiment registry + one README per experiment (design before the run, then results)
configs/           datasets, preprocessing and analysis parameters (YAML)
src/eegconf/       analysis package (io, preprocessing, features, representation,
                   probing, control, evaluation, stats, viz)
scripts/           pipeline entry points, one per stage (scripts/README.md lists them)
notebooks/         exploration only
tests/             leakage, audit and overlap unit tests (run on every push: .github/workflows)
data/              local only, never committed (see data/README.md)
results/           tables/ and figures/ committed; runs/ and the Excel workbook local only
reports/           final report, reporting checklists, data audit report, meeting notes
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
| Audit, overlap | `python scripts/01_audit.py --cohort <c>`; `python scripts/02_overlap_check.py`; `python scripts/02_overlap_recheck.py` | `T00_*`, `T02_*` (EXP-001, 002) |
| Preprocess | `python scripts/03_preprocess.py --cohort <c>`; `python scripts/03_qc.py` | `T03_*`, F3 (EXP-003) |
| Embeddings (GPU) | `python scripts/04_extract_embeddings.py --cohort <c>` and again with `--random`, `--amplitude-scaled`, `--band-stop <band>`, `--occlude <channel or region>`; `python scripts/04_sanity.py` | `T04_*` |
| Features | `python scripts/05_build_features.py`; `python scripts/05_build_features.py --scaled-only` | participant features (local) |
| Baseline | `python scripts/06_baseline.py` | `T06_*` (EXP-010–013) |
| Probes | `python scripts/07_probes.py` | `T07_*`, F4 (EXP-020–022) |
| Control | `python scripts/08_control.py` | `T08_*` (EXP-030–032) |
| Primary + sensitivity | `python scripts/09_sensitivity.py` | `T09_*` (EXP-040–044) |
| Statistics | `python scripts/10_stats.py` | `T10_*` |
| Interpretation | `python scripts/11_data_amount.py`; `python scripts/11_random_epochs.py`; `python scripts/11_interpret.py` | `T11_*`, F7, F8 (EXP-050–054) |
| Review-prompted checks | `python scripts/13_review_analyses.py --part fixed_block`; `--part pooled` | `T13_*`, F9 (EXP-055, 056) |
| Report figures | `python scripts/12_figures.py` | F5, F6 |
| Results workbook | `python scripts/12_workbook.py` (needs `openpyxl`) | `results/experiments_summary.xlsx`, one sheet per experiment (not committed) |

`<c>` is each of `ds004504`, `ADFSU`, `APAVA`. The analysis seed is in `configs/analysis.yaml`. Steps 06–13
use 20 CPU workers by default (`--n-jobs`); the longest runs take one to two hours.

## Pipeline at a glance
1. Download and audit each cohort; resolve the ADSZ–ADFSU overlap.
2. Eyes-closed → 16 common channels → 0.5–30 Hz (zero-phase Butterworth) → average reference →
   200 Hz → 4-s epochs → amplitude-based rejection; all clean epochs kept (8-s crop as a sensitivity analysis).
3. Frozen LaBraM embeddings → participant-level representation **Z**.
4. **A** AD classifier · **B** probes for age, sex (ds004504) and cohort · **C** nuisance-controlled **Z\*** → AD classifier.
5. Leave-one-cohort-out over three cohorts; primary outcome = mean per-fold ΔAUROC(Z, Z\*).
6. After the review: the same comparison with the block held fixed, and a pooled positive control.

## Working together
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branches, commit messages, and how to log papers and experiments.

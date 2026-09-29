# Work plan

Every task is broken down to steps that can be done in one sitting. Each has an output and a
"done when" check. Tick the box when done; write your initials after the task ID when you take
it (e.g. `T2.1.3 (DE)`). Task IDs are referenced in `experiments/registry.csv` and commit
messages.

**Golden rules (apply to every phase)**
1. The participant is the unit. No epoch, trial or recording of a test participant may ever
   influence anything fitted on training data.
2. Everything learned from data (scalers, residualisers, cohort means, erasers, layer choice,
   pooling choice, hyperparameters) is fitted inside the training fold only.
3. Parameters are prespecified in `configs/` and `docs/decision_log.md` *before* results are seen.
   Git tag `analysis-plan-v1` marks the freeze (T4.0).
4. Nothing is reported unless it was produced by code in `src/` + `scripts/` and logged as an
   experiment.

---

## Timeline

Month numbers are relative to project start (fill the real start date: `M1 = ____`).

| Phase | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 | M10 | M11 | M12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 Setup & data terms | ■ | | | | | | | | | | | |
| 1 Literature | ■ | ■ | ■ | ■ | · | · | · | · | · | · | | |
| 2 Data acquisition & audit | ■ | ■ | ■ | | | | | | | | | |
| 3 Overlap check | | | ■ | | | | | | | | | |
| 4 Preprocessing | | | ■ | ■ | ■ | | | | | | | |
| 5 LaBraM representations | | | | | ■ | ■ | | | | | | |
| 6 O1 baseline | | | | | | ■ | ■ | | | | | |
| 7 O2 probes | | | | | | | ■ | ■ | | | | |
| 8 O3 nuisance control | | | | | | | ■ | ■ | ■ | | | |
| 9 O4 cross-cohort + sensitivity | | | | | | | | | ■ | ■ | | |
| 10 Statistics | | | | | | | | | ■ | ■ | ■ | |
| 11 O5 interpretation | | | | | | | | | | ■ | ■ | |
| 12 Writing & final report | | | | | | | | | ■ | ■ | ■ | ■ |

(■ main effort, · keep the matrix up to date)

### Milestones / gates
| Gate | End of | Must be true before moving on |
|---|---|---|
| G0 | M1 | Data-use terms read for every dataset; environment installs; all 4 dataset sources identified |
| G1 | M3 | Audit tables complete for all cohorts; overlap resolved; final participant counts known |
| G2 | M5 | Preprocessing QC passed; `analysis-plan-v1` tag pushed |
| G3 | M6 | Embeddings extracted and sanity-checked for every included participant |
| G4 | M8 | O1 + O2 results logged; mentor review |
| G5 | M10 | Primary outcome and sensitivity analyses complete |
| G6 | M12 | Final report/paper complete; repository reproduces all reported numbers |

---

## Resources needed

### Data
| Item | Where | Needed for |
|---|---|---|
| ds004504 (raw BIDS, not derivatives) | OpenNeuro `ds004504` | all |
| ADFSU recordings + labels + participant IDs + condition labels | source to be traced (T2.2.1) | all |
| ADSZ recordings + labels + participant IDs + condition labels | source to be traced (T2.3.1) | all |
| APAVA recordings + labels + participant IDs | source to be traced (T2.4.1) | all |
| LaBraM code + `labram-base` checkpoint | https://github.com/935963004/LaBraM | Phase 5 |

### Software (see `environment.yml`)
Python 3.11, MNE ≥ 1.7, mne-bids, openneuro-py, NumPy/SciPy/pandas, scikit-learn, statsmodels,
PyTorch, timm (version required by LaBraM), einops, specparam, concept-erasure (LEACE),
matplotlib, pytest, git.

### Compute and storage
- LaBraM-base is small; frozen inference for ~230 participants runs on a laptop CPU
  (GPU optional, speeds up perturbation analyses in Phase 11).
- ≥ 16 GB RAM recommended. Storage: ds004504 needs ~2.2 GB (see T2.1); check the other archive sizes before download (T2.x.3); keep
  `data/` outside cloud-synced folders if large.

### Documents
- Data-use terms for each dataset (saved in `docs/licences/`).
- TRIPOD+AI checklist and PROBAST form (Phase 12).

---

## Phase 0 – Setup and data-use terms (M1)

- [ ] **T0.1 Data-use terms** (all data are public and de-identified)
  - [ ] T0.1.1 For each dataset, find its licence / terms of use (OpenNeuro: `dataset_description.json` licence field; others: repository page or original paper).
  - [ ] T0.1.2 Record for each: licence name, whether redistribution is allowed (assume not), required citation(s), any restriction on commercial use or re-identification.
  - [ ] T0.1.3 Save a copy or link in `docs/licences/<cohort>_terms_<date>.pdf|md` and the licence field in `docs/datasets.md`.
  - [ ] T0.1.4 Add the required dataset citations to the literature matrix so they are cited in the write-up.
  - Done when: every dataset has a recorded licence and citation.
- [ ] **T0.2 Environment**
  - [ ] T0.2.1 Install Miniconda; `conda env create -f environment.yml`; `conda activate eegconf`.
  - [ ] T0.2.2 `python -c "import mne, sklearn, torch, specparam, concept_erasure"` runs without error.
  - [ ] T0.2.3 `pip freeze > docs/env_lock.txt`; commit.
  - Done when: both team members can import everything on their machines.
- [ ] **T0.3 Repository conventions**
  - [ ] T0.3.1 Agree branch model: `main` protected; work on `feature/<task-id>-short-name`; merge by pull request reviewed by the other person.
  - [ ] T0.3.2 Agree commit message style (see `CONTRIBUTING.md`).
  - [ ] T0.3.3 Create a shared calendar entry for a fortnightly mentor meeting; notes go in `reports/meetings/`.
- [ ] **T0.4 Leakage unit tests (write early, run forever)**
  - [ ] T0.4.1 `tests/test_splits.py`: for every split generator, assert the intersection of train and test participant IDs is empty.
  - [ ] T0.4.2 `tests/test_fit_on_train.py`: wrap each transformer so it records the row IDs it was fitted on; assert ⊆ training IDs.
  - [ ] T0.4.3 `tests/test_centring.py`: variant (i) must not read any test-cohort row.
  - [ ] T0.4.4 Add `pytest` to the pre-merge checklist.

## Phase 1 – Literature review (M1–M4, then continuous)

- [ ] **T1.1 Search**
  - [ ] T1.1.1 Define search strings and save them in `literature/search_log.md` (date, database, string, hits). Minimum strings:
    - `("EEG" AND "Alzheimer*") AND ("machine learning" OR "deep learning") AND ("leakage" OR "subject-independent" OR "cross-dataset" OR "external validation")`
    - `("EEG foundation model" OR "LaBraM" OR "CBraMod" OR "BIOT" OR "REVE" OR "LEAD") AND ("probing" OR "confound" OR "shortcut" OR "site" OR "dataset identity")`
    - `("concept erasure" OR "LEACE" OR "INLP" OR "ComBat" OR "harmonization") AND ("EEG" OR "neuroimaging")`
    - `("age" OR "sex") AND "EEG" AND ("confound" OR "brain age") AND ("dementia" OR "Alzheimer*")`
  - [ ] T1.1.2 Run in PubMed, Scopus/Web of Science, Google Scholar, arXiv; record hits.
  - [ ] T1.1.3 Screen titles/abstracts; add every candidate to `review_matrix.csv` with `status=to-read`.
- [ ] **T1.2 Read and extract** – for each paper marked relevant:
  - [ ] T1.2.1 Fill all matrix columns; `methods_terms` must use precise terms.
  - [ ] T1.2.2 For papers central to the argument (Brookshire, Miltiadous 2026, Lin 2026, Tang 2026, LaBraM, LEAD, LEACE), write a full note in `literature/notes/`.
  - [ ] T1.2.3 Check retraction/withdrawal status; record in the note.
- [ ] **T1.3 Resolve `literature/to_verify.md`** – one checkbox per claim.
- [ ] **T1.4 Harmonisation methods sub-review** – ComBat / neuroHarmonize, cohort centring, domain adaptation for EEG; decide whether ComBat should be an extra sensitivity analysis (log in decision log).
- [ ] **T1.5 AD EEG marker sub-review** – effect directions and typical sizes for theta power, alpha power, theta/alpha ratio, peak alpha frequency, aperiodic exponent in AD vs HC; these are the priors for O5.
- [ ] **T1.6 Update `gaps.md`** at the end of each month.
- [ ] **T1.7 Draft the literature review section** (Phase 12 input) from the matrix and notes.

## Phase 2 – Data acquisition and audit (M1–M3) → EXP-001

**Standard audit checklist (A1–A12)** – run for every cohort, record results in
`data/metadata/audit_<cohort>.csv` and a summary in `docs/datasets.md`:

| Check | How |
|---|---|
| A1 files | list every recording file; count per participant |
| A2 labels | map every recording to participant ID and diagnosis; count AD/HC |
| A3 channels | channel names and order per file; confirm the 16 target channels exist |
| A4 sampling rate | per file |
| A5 units | median per-channel SD; EEG should be ~5–100 µV (if ~1e-5 it is in V; if ~5000 it is in nV or scaled) |
| A6 duration | per file and total per participant |
| A7 condition | eyes open/closed label per file/segment; how it is encoded |
| A8 reference | from metadata or documentation |
| A9 prior processing | was it already filtered/resampled/cleaned at source? (compare PSD edges, check docs) |
| A10 bad data | NaN/Inf, flat channels (SD < 0.5 µV), clipping (runs of identical max values), extreme amplitude (> 500 µV) |
| A11 PSD | Welch PSD per channel (2-s Hann, 50% overlap), plot mean by group; look for line noise, roll-off, notch artefacts |
| A12 duplicates within cohort | pairwise correlation of per-recording PSD fingerprints within the cohort; flag r > 0.99 |

### T2.1 ds004504
Size check (done via the OpenNeuro API and public S3 bucket, snapshot 1.0.9): the full dataset is
~5.8 GB, of which derivatives/ ≈ 2.95 GB and FTD raw ≈ 0.67 GB. We need only AD + HC raw
≈ **2.16 GB (65 participants, 201 files, ~24 MB per recording)**. No account or API key is needed.

- [x] T2.1.1 Version and size recorded: snapshot **1.0.9** (doi:10.18112/openneuro.ds004504.v1.0.9), licence **CC0**.
- [ ] T2.1.2 Download only what we use: `python scripts/download_ds004504.py` (run with `--dry-run` first; it should print `65 participants, 201 files, 2.16 GB`). It reads `participants.tsv`, keeps Group A and C, skips FTD and `derivatives/`, resumes if interrupted, and writes `data/raw/ds004504/MANIFEST.tsv` with a sha256 per file. Record the download date in `docs/datasets.md`.
  - Low-disk alternative: process one participant at a time (download → T4 preprocessing → save processed epochs (< 1 MB) → delete raw). Peak disk ≈ 25 MB. If you use it, run the A1–A12 audit (T2.1.6) inside the same loop, before each raw file is deleted.
- [ ] T2.1.3 Keep `MANIFEST.tsv` local (it lives in `data/`, which is not committed); copy the sha256 of `participants.tsv` from it into the dataset card.
- [x] T2.1.4 `participants.tsv` columns confirmed: `participant_id, Gender, Age, Group, MMSE`; Group A = 36, C = 29, F = 23.
- [x] T2.1.5 Demographics recomputed from `participants.tsv`: female/male AD 24/12 vs HC 11/18 (Fisher's exact p = 0.026); age AD 66.4 ± 7.9 vs HC 67.9 ± 5.4 years (Mann–Whitney p = 0.38). Still to do: MMSE median (IQR) per group, and save the table to `results/tables/T01_cohort_summary.csv`.
- [ ] T2.1.6 Load every recording with `mne.io.read_raw_eeglab(..., preload=False)`; run A1–A12. Note the per-recording duration varies (sub-001 = 599.8 s), so record the range; the "~13 min" in the slides is an average to check.
- [x] T2.1.7 Reference and acquisition from `sub-001_task-eyesclosed_eeg.json`: reference **A1 A2** (linked ears), Nihon Kohden EEG 2100, 500 Hz, online filter 0.4–50 Hz, line frequency 50 Hz, channels in µV with old 10–20 names (T3, T4, T5, T6). Still to do: confirm these are identical in every participant's JSON (loop over files).
- [ ] T2.1.8 Confirm all recordings are eyes-closed (A7): every file is `task-eyesclosed`; check none is missing.
- [ ] T2.1.9 Write the dataset card fields and commit the audit summary CSV (no raw data).

### T2.2 ADFSU
- [ ] T2.2.1 Trace the source: read the data section of LEAD (Wang et al., 2025) and any paper that uses the name "ADFSU"; find the **original** recording study and its download location; record citation + URL + licence.
- [ ] T2.2.2 Decide raw vs already-preprocessed version: prefer the rawest available. If only preprocessed exists, record exactly what was done at source (A9) – it constrains what our pipeline controls.
- [ ] T2.2.3 Download to `data/raw/ADFSU`; record version/date + checksum.
- [ ] T2.2.4 Confirm participant IDs exist for every trial (needed for subject-level splits). If trials lack IDs → **stop and raise it with the mentor**: the cohort cannot be used without them.
- [ ] T2.2.5 Confirm condition labels per trial (eyes open vs closed). If absent → raise it with the mentor (see T4.1.3).
- [ ] T2.2.6 Run A1–A12. Confirm 80 AD / 12 HC, 19 channels, 128 Hz, 8-s trials, trials per participant.
- [ ] T2.2.7 Check the 0.5–30 Hz band limit claim from the PSD (A11); tick in `literature/to_verify.md`.
- [ ] T2.2.8 Fill the dataset card.

### T2.3 ADSZ
- [ ] T2.3.1 Trace source (as T2.2.1). Note whether it shares an origin with ADFSU (input for Phase 3).
- [ ] T2.3.2 Raw vs preprocessed decision (as T2.2.2).
- [ ] T2.3.3 Download to `data/raw/ADSZ`; version/date + checksum.
- [ ] T2.3.4 Participant IDs per trial (as T2.2.4).
- [ ] T2.3.5 Resolve the condition question (proposal: eyes open + closed; slides: resting) from files/documentation.
- [ ] T2.3.6 Run A1–A12. Confirm 24 AD / 24 HC, 19 channels, 128 Hz, 8-s trials.
- [ ] T2.3.7 Fill the dataset card.

### T2.4 APAVA
- [ ] T2.4.1 Trace source (as T2.2.1).
- [ ] T2.4.2 Raw vs preprocessed decision.
- [ ] T2.4.3 Download to `data/raw/APAVA`; version/date + checksum.
- [ ] T2.4.4 Participant IDs per trial.
- [ ] T2.4.5 Run A1–A12. Confirm 12 AD / 11 HC, 16 channels, 256 Hz, 5-s trials, trials per participant.
- [ ] T2.4.6 Confirm the channel set is exactly the 19-ch 10–20 set minus Fz, Cz, Pz; tick in `to_verify.md`.
- [ ] T2.4.7 Fill the dataset card.

### T2.5 Combined participants table
- [ ] T2.5.1 Build `data/metadata/participants_all.csv`: `cohort, participant_id, global_id, diagnosis, age, sex, mmse, n_trials_raw, n_trials_ec, total_ec_seconds` (age/sex/mmse empty outside ds004504).
- [ ] T2.5.2 `global_id = <cohort>-<participant_id>`; used everywhere downstream.
- [ ] T2.5.3 Save a summary table (counts only, no participant rows) to `results/tables/T01_cohort_summary.csv`.
- [ ] T2.5.4 Log EXP-001 as done.
- Done when (gate G1, part 1): every cohort has a complete audit and a card with no ❓ left in critical fields (IDs, labels, channels, rate, units, condition).

## Phase 3 – ADSZ–ADFSU overlap check (M3) → EXP-002

- [ ] T3.1 Compare metadata: participant counts, trial counts, trial lengths, any ID patterns, source papers.
- [ ] T3.2 Put both cohorts in the same units (µV) and channel order (16 target + the 3 midline channels available in both).
- [ ] T3.3 **Exact duplicates**: hash each trial array (float32, rounded to 0.01 µV) with SHA-1; intersect hash sets across cohorts.
- [ ] T3.4 **Near duplicates**: for each trial, Welch PSD (1–30 Hz, 0.5-Hz bins) per channel, log-power, flatten to a fingerprint; compute Pearson r between every ADSZ trial and every ADFSU trial; flag pairs with r > 0.99.
- [ ] T3.5 For flagged pairs, compute the maximum normalised cross-correlation of the time series over lags ±1 s per channel; confirm duplicates if median across channels > 0.95. Also check for resampled/scaled copies (correlation is invariant to scaling; check lag and sign).
- [ ] T3.6 Aggregate trial matches to participant matches (a participant is duplicated if ≥ 1 trial matches).
- [ ] T3.7 Check label consistency for each duplicated participant (AD in both?). Label conflict → exclude the participant from both cohorts.
- [ ] T3.8 Apply the prespecified rule (write it in the decision log **before** T3.3): a duplicated participant stays in the cohort where they have more eyes-closed data; tie → stay in ADSZ (keeps ADSZ balanced); remove from the other.
- [ ] T3.9 Run the same near-duplicate check within each cohort (same person under two IDs) and between ds004504/APAVA and the others (cheap; PSD fingerprints after resampling to a common rate).
- [ ] T3.10 Write `data/metadata/overlap_report.csv` and a short summary in EXP-002; update `participants_all.csv` (`included` column + `exclusion_reason`).
- [ ] T3.11 Draw the participant flow diagram numbers (downloaded → labelled → eyes-closed available → after overlap → after QC) for the write-up.

## Phase 4 – Harmonised preprocessing (M3–M5) → EXP-003

- [ ] **T4.0 Freeze the analysis plan**
  - [ ] T4.0.1 Re-read `configs/preprocessing.yaml`, `configs/analysis.yaml`, `docs/protocol.md` against the audit; adjust only with a decision-log entry.
  - [ ] T4.0.2 Mentor sign-off (email or meeting note).
  - [ ] T4.0.3 `git tag analysis-plan-v1 && git push --tags`.
- [ ] **T4.1 Condition selection**
  - [ ] T4.1.1 ds004504, APAVA: keep all (eyes-closed).
  - [ ] T4.1.2 ADFSU, ADSZ: keep only trials labelled eyes-closed.
  - [ ] T4.1.3 If condition labels are missing for a cohort: apply the proposal rule – the cohort is kept only in a prespecified sensitivity analysis. Log the decision; tell the mentor (it would remove the cohort from the primary LOCO).
  - [ ] T4.1.4 Save `data/interim/<cohort>/` as MNE Raw per trial/recording with the global participant ID in `raw.info['subject_info']` or a sidecar CSV.
- [ ] **T4.2 Channel mapping**
  - [ ] T4.2.1 Fill the channel mapping table in `docs/datasets.md` (dataset label → canonical → LaBraM label). Watch for T3/T7, T4/T8, T5/P7, T6/P8 and case/space differences ("FP1", "EEG Fp1-REF").
  - [ ] T4.2.2 Implement `eegconf.preprocessing.pick_channels(raw, cohort)` returning exactly the 16 channels in the order in `configs/preprocessing.yaml`.
  - [ ] T4.2.3 Unit test: every cohort returns identical names and order.
  - [ ] T4.2.4 Set the standard 10–20 montage (`mne.channels.make_standard_montage('standard_1020')`) for topographic plots later.
- [ ] **T4.3 Units** – convert to Volts internally (MNE convention) from the unit found in A5; assert median channel SD in 5–100 µV after conversion.
- [ ] **T4.4 Filtering**
  - [ ] T4.4.1 `raw.filter(0.5, 30, method='fir', phase='zero')` per continuous recording/trial, before any epoching.
  - [ ] T4.4.2 Short trials (5–8 s): check the FIR length MNE reports for the 0.5-Hz high-pass (it can exceed the trial length). If it does, pad (`pad='reflect_limited'`) and record the edge effect; alternative prespecified fallback: IIR Butterworth order 4, zero-phase (`method='iir'`) for all cohorts. Choose once, log in decision log, apply to every cohort.
  - [ ] T4.4.3 No notch filter (D-014). Verify on the PSD that no line-noise peak survives below 30 Hz.
- [ ] **T4.5 Re-reference** – common average over the 16 channels (`raw.set_eeg_reference('average')`), after channel selection so every cohort uses the same channel set.
- [ ] **T4.6 Resample** – `raw.resample(200)` after low-pass (anti-aliasing satisfied because 30 Hz < 100 Hz Nyquist). Note: 128-Hz cohorts are upsampled and have no content above 64 Hz; the 30-Hz low-pass makes this identical across cohorts.
- [ ] **T4.7 Epoching and artefact rejection**
  - [ ] T4.7.1 Fixed-length 4-s non-overlapping epochs (`mne.make_fixed_length_epochs(duration=4.0)`); drop incomplete tails.
  - [ ] T4.7.2 Reject epochs with any channel peak-to-peak > 150 µV or < 0.5 µV (flat).
  - [ ] T4.7.3 Log per participant: epochs before/after rejection, reasons.
  - [ ] T4.7.4 Check rejection rate by cohort and by diagnosis; a large imbalance is itself a confound – report it.
- [ ] **T4.8 Equal-length crop**
  - [ ] T4.8.1 Table of clean epochs per participant.
  - [ ] T4.8.2 Prespecified rule: exclude participants with fewer than 2 clean epochs; K = minimum clean-epoch count among the remaining participants; keep the first K clean epochs in time order (deterministic, not random).
  - [ ] T4.8.3 Write K into `configs/preprocessing.yaml` and the decision log.
  - [ ] T4.8.4 Save `data/processed/<cohort>/<global_id>-epo.fif`.
- [ ] **T4.9 Preprocessing QC (EXP-003)**
  - [ ] T4.9.1 Mean PSD per cohort × diagnosis on processed data (0.5–30 Hz) – one figure.
  - [ ] T4.9.2 Per-channel amplitude distribution per cohort.
  - [ ] T4.9.3 Visual check of 5 random participants per cohort (`epochs.plot()`).
  - [ ] T4.9.4 Quick classical-feature cohort probe (relative band power → cohort, grouped CV): records how much cohort information survives preprocessing *before* any foundation model. Save as reference value.
  - [ ] T4.9.5 Write `data/metadata/qc_report.csv`; commit figures to `results/figures/EXP-003_*`.
- Done when (G2): QC passed, K fixed, tag pushed.

## Phase 5 – Frozen LaBraM representations (M5–M6)

- [ ] **T5.1 Model setup**
  - [ ] T5.1.1 Clone https://github.com/935963004/LaBraM into `external/LaBraM` (git-ignored or as a submodule at a pinned commit; record the commit hash).
  - [ ] T5.1.2 Install its exact requirements (timm version) into the environment; re-run T0.2.2.
  - [ ] T5.1.3 From the code, confirm and write down in `docs/decision_log.md`: expected sampling rate (200 Hz), patch size (200 samples = 1 s), amplitude scaling (µV/100 in their data loaders), channel-name list used for positional embeddings (`standard_1020` list in `utils.py`), maximum number of patches, how `input_chans` is built.
  - [ ] T5.1.4 Download `labram-base.pth`; record sha256; load with the model constructor for the base model; `model.eval()`; confirm all weights loaded (no missing/unexpected keys other than the classification head).
- [ ] **T5.2 Extraction**
  - [ ] T5.2.1 For each epoch: shape (16, 800) → scale → reshape to (16, 4, 200) → batch.
  - [ ] T5.2.2 Build `input_chans` from our 16 LaBraM channel names (mapping table T4.2.1).
  - [ ] T5.2.3 Register forward hooks on every transformer block; for each block store the mean over all patch tokens (and the CLS token if the model has one) → vector of size d (200 for base; confirm).
  - [ ] T5.2.4 Run under `torch.no_grad()`, fp32, fixed seed; no dropout (eval mode).
  - [ ] T5.2.5 Save `data/embeddings/labram-base/<cohort>.npz` with arrays `Z[layer, epoch, d]`, `global_id[epoch]`, `epoch_idx[epoch]`.
- [ ] **T5.3 Participant pooling** – implement mean, median, mean ⊕ SD over a participant's K epochs; choice is made inside training folds (Phase 6), so store epoch-level embeddings.
- [ ] **T5.4 Sanity checks**
  - [ ] T5.4.1 Determinism: same input twice → identical output.
  - [ ] T5.4.2 No NaN/Inf; embedding norm distribution per cohort (a single cohort with a very different norm suggests a scaling/unit error).
  - [ ] T5.4.3 Shuffled-channel control: permute the channel order of a few epochs; embeddings should change (confirms `input_chans` is used).
  - [ ] T5.4.4 Random-weights baseline: extract the same features from a randomly initialised LaBraM (same architecture) – used later as a negative control for probes and classifiers.
- Done when (G3): embeddings for every included participant, all checks logged.

## Phase 6 – O1 Baseline classification (M6–M7) → EXP-010 to EXP-013

- [ ] **T6.1 Evaluation framework**
  - [ ] T6.1.1 `eegconf.evaluation.splits`: `StratifiedGroupKFold` (groups = global_id) for inner CV; repeated version for within-cohort; LOCO generator over cohorts.
  - [ ] T6.1.2 Pipeline object: pooling → StandardScaler → classifier, fitted per training fold.
  - [ ] T6.1.3 Nested selection inside each outer training fold: layer (all blocks) × pooling (3) × C (6) by inner-CV AUROC. Record the chosen values per outer fold.
  - [ ] T6.1.4 Save per-participant out-of-fold predicted probabilities (needed for bootstrap).
  - [ ] T6.1.5 Metrics: AUROC (primary), balanced accuracy, sensitivity, specificity, F1, PR-AUC; threshold for threshold-based metrics chosen on training data (Youden J), never on test.
- [ ] **T6.2 Within-cohort (EXP-010)** – for each cohort: repeated (10×) stratified grouped 5-fold; report mean AUROC and participant-bootstrap CI. APAVA/ADFSU small-class folds: check each test fold has ≥ 1 HC; if not, reduce to 3 folds (log it).
- [ ] **T6.3 LOCO (EXP-011)** – 4 folds; per-fold AUROC + CI; pooled AUROC secondary.
- [ ] **T6.4 Classical comparator (EXP-012)**
  - [ ] T6.4.1 Features per participant: relative power (delta 1–4, theta 4–8, alpha 8–13, beta 13–30 Hz; relative to 1–30 Hz) per channel from Welch PSD (2-s Hann, 50% overlap) averaged over the K epochs.
  - [ ] T6.4.2 Aperiodic exponent per channel: `specparam` fixed mode, 2–30 Hz fit range (avoids the 0.5-Hz filter edge), peak width limits 1–8 Hz, max 6 peaks; drop fits with R² < 0.9 and log them.
  - [ ] T6.4.3 Same classifier and same splits as T6.2/T6.3; compare AUROC paired per fold.
- [ ] **T6.5 Nuisance-only baselines (EXP-013)**
  - [ ] T6.5.1 ds004504: age + sex → AD, logistic regression, same grouped CV.
  - [ ] T6.5.2 Pooled cohorts: cohort one-hot → AD with participant-grouped CV over the pooled data (not LOCO).
  - [ ] T6.5.3 Random-weights LaBraM features → AD (negative control from T5.4.4).

## Phase 7 – O2 Probing nuisance information (M7–M8) → EXP-020 to EXP-022

- [ ] **T7.1 Age probe (ds004504)**
  - [ ] T7.1.1 Ridge regression Z → age, grouped 5-fold × 10 repeats, alpha by inner CV.
  - [ ] T7.1.2 Metrics: MAE and R²; baseline = predicting the training mean.
  - [ ] T7.1.3 Permutation test: 1000 label permutations through the full pipeline.
  - [ ] T7.1.4 Also run within HC only (separates age information from disease information, because AD and age are correlated).
- [ ] **T7.2 Sex probe (ds004504)** – logistic regression, AUROC + balanced accuracy, permutation test; also within each diagnostic group (because sex is imbalanced by diagnosis).
- [ ] **T7.3 Cohort probe (all cohorts)**
  - [ ] T7.3.1 Multinomial logistic regression Z → cohort, grouped stratified 5-fold (stratify on cohort × diagnosis).
  - [ ] T7.3.2 Balanced accuracy, macro-F1, confusion matrix; chance = 0.25.
  - [ ] T7.3.3 Same probe on classical features (T6.4) and on random-weights features (T5.4.4) as references.
  - [ ] T7.3.4 Probe per layer → layer profile of cohort information (figure).
- [ ] **T7.4 Nonlinear probes (EXP-022)** – one-hidden-layer MLP (64 units, early stopping on inner validation) for age, sex, cohort; compare with linear.
- [ ] **T7.5 (optional) Variance decomposition** – share of embedding variance explained by cohort, diagnosis, participant (following Lin2026identitytrap); compare with a random-Gaussian null.

## Phase 8 – O3 Nuisance control (M7–M9) → EXP-030 to EXP-032

- [ ] **T8.1 Demographic control within ds004504 (EXP-030)**
  - [ ] T8.1.1 Inside each training fold: OLS per embedding dimension Z_d ~ age + sex; store coefficients.
  - [ ] T8.1.2 Apply to training and test participants using their own age/sex → Z\*demo.
  - [ ] T8.1.3 Re-run the AD classifier on Z\*demo with identical splits; paired ΔAUROC.
  - [ ] T8.1.4 Sensitivity: fit the residualiser on training HC only (normative approach, avoids removing disease-correlated variance through age).
  - [ ] T8.1.5 Verify: re-run age and sex probes on Z\*demo (linear and MLP).
- [ ] **T8.2 Cohort centring in LOCO (EXP-031)**
  - [ ] T8.2.1 For each training cohort c: μ_c = ½(mean of AD participants + mean of HC participants) using training labels; subtract μ_c from that cohort's participants.
  - [ ] T8.2.2 Held-out cohort, variant (i): subtract the pooled training mean (mean of the μ_c) – no test data used.
  - [ ] T8.2.3 Held-out cohort, variant (ii): subtract the unweighted mean of the held-out cohort's own embeddings (no labels) – transductive, reported as such.
  - [ ] T8.2.4 Train the AD classifier on centred training data; evaluate on each variant; paired ΔAUROC against the original representation, per fold.
- [ ] **T8.3 Linear erasure (EXP-032)**
  - [ ] T8.3.1 LEACE (`concept_erasure.LeaceEraser`) fitted on training participants with cohort one-hot as the concept; apply to train and test.
  - [ ] T8.3.2 INLP: 20 iterations of linear SVM/logistic cohort classifier + nullspace projection on training data; apply the final projection to test.
  - [ ] T8.3.3 AD classifier on each; paired ΔAUROC per fold.
- [ ] **T8.4 Verification of removal** – on training folds (inner CV), re-run linear and MLP cohort probes on every controlled representation; report residual balanced accuracy vs chance. Linear probe should be ≈ chance after LEACE by construction; the MLP result is the informative one.
- [ ] **T8.5 Unit tests** – T0.4.2/T0.4.3 pass for every control method.

## Phase 9 – O4 Cross-cohort generalisation and sensitivity (M9–M10) → EXP-040 to EXP-042

- [ ] **T9.1 Primary outcome (EXP-040)**
  - [ ] T9.1.1 Collect per-fold out-of-fold predictions for original Z and cohort-controlled Z\* (variant (i) centring is the primary controlled representation; variant (ii), LEACE, INLP are secondary) – confirm this choice in the decision log at T4.0.
  - [ ] T9.1.2 Per-fold ΔAUROC with paired bootstrap CI (Phase 10).
  - [ ] T9.1.3 Mean ΔAUROC across the four folds with CI.
  - [ ] T9.1.4 Classify the pattern: A (little change), B (moderate drop, still above nuisance-only baseline), C (large drop) – define numeric thresholds in the decision log before running (e.g. A: CI includes 0; C: controlled AUROC CI includes the nuisance-only baseline).
- [ ] **T9.2 Sensitivity without ADFSU (EXP-041)** – repeat T9.1 with 3 cohorts (3 folds).
- [ ] **T9.3 Sensitivity with ADFSU subsampled (EXP-042)** – 100 draws, each subsampling ADFSU AD participants to the number of ADFSU HC (fixed seeds 1–100); rerun T9.1 per draw; report the distribution (median, 2.5–97.5 percentiles) of mean ΔAUROC.
- [ ] **T9.4 Summary table** `results/tables/T05_primary_and_sensitivity.csv`: rows = analysis, columns = per-fold AUROC(Z), AUROC(Z\*), ΔAUROC, CI, mean ΔAUROC.

## Phase 10 – Statistics (M9–M11)

- [ ] T10.1 Implement stratified participant bootstrap (resample participants with replacement within AD and within HC of the test set, B = 2000), percentile 95% CI.
- [ ] T10.2 Paired version: same resampled indices for both representations → ΔAUROC distribution.
- [ ] T10.3 Across-fold mean: for each bootstrap replicate resample every fold independently and average the fold ΔAUROCs.
- [ ] T10.4 Cross-check per-fold AUROC CIs with DeLong's method; report if they disagree materially.
- [ ] T10.5 Holm correction across secondary comparisons (list them in the decision log first).
- [ ] T10.6 Report effect sizes with CIs everywhere; p-values only where prespecified.
- [ ] T10.7 Reproduce every reported number from saved predictions with `scripts/07_stats.py` on a clean checkout.

## Phase 11 – O5 Neurophysiological interpretation (exploratory, M10–M11) → EXP-050 to EXP-052

- [ ] T11.1 Compute per participant: relative theta, relative alpha, theta/alpha ratio, peak alpha frequency (maximum of the periodic component in 7–13 Hz from specparam; fallback: centre of gravity 7–13 Hz), aperiodic exponent; posterior (O1, O2, P3, P4, T5, T6) and global averages.
- [ ] T11.2 **Band perturbation (EXP-050)**: band-stop filter one band (delta, theta, alpha, beta) in the preprocessed input, re-extract embeddings, apply the frozen controlled classifier, record change in predicted AD probability per participant.
- [ ] T11.3 **Channel occlusion (EXP-051)**: replace one channel at a time with zeros (after CAR) or the channel mean, re-extract, record change; topographic map with `mne.viz.plot_topomap`.
- [ ] T11.4 **Z\* vs classical markers (EXP-052)**: correlate the classifier decision score on Z\* with each marker (Spearman), and ridge-map Z\* → each marker (grouped CV R²); FDR correction.
- [ ] T11.5 Compare directions with the priors from T1.5 (expected: higher theta, lower alpha, higher theta/alpha, lower PAF in AD).
- [ ] T11.6 Write it up as plausibility, not proof of disease specificity.

## Phase 12 – Writing and reporting (M9–M12)

- [ ] T12.1 Fill the TRIPOD+AI checklist (`reports/checklists/tripod_ai.md`) item by item with section references.
- [ ] T12.2 PROBAST self-assessment (participants, predictors, outcome, analysis domains).
- [ ] T12.3 Figures: F1 pipeline; F2 participant flow; F3 PSD by cohort × diagnosis; F4 probe results by layer; F5 per-fold AUROC original vs controlled (forest plot); F6 sensitivity analyses; F7 interpretation topomaps/bands.
- [ ] T12.4 Tables: T1 cohort characteristics; T2 preprocessing parameters; T3 O1 results; T4 probes; T5 primary + sensitivity; T6 interpretation.
- [ ] T12.5 Sections of the final report/paper: Introduction, Literature review (from Phase 1), Methods (from protocol + decision log), Results (from experiments), Discussion (pattern A/B/C, limitations: small cohorts, demographics in one cohort only, cohort ≡ acquisition, one foundation model, clinical labels), Conclusion.
- [ ] T12.6 Update the slide deck to match the final design (title, conditions, primary outcome).
- [ ] T12.7 Reproducibility package: `README` run order, env lock, data download instructions, config tag, one command per figure/table.
- [ ] T12.8 Full read-through by both team members; draft to the mentor at least 4 weeks before the fellowship deadline.
- [ ] T12.9 Final version delivered; tag `final-v1`.

---

## Risks and mitigations
| Risk | Effect | Mitigation |
|---|---|---|
| A cohort lacks participant IDs or condition labels | cohort unusable / only in sensitivity | resolve in Phase 2 (T2.x.4–5); raise early |
| ADSZ and ADFSU largely overlap | fewer cohorts, fewer LOCO folds | rule fixed in T3.8; LOCO with 3 cohorts is still valid |
| Source data already preprocessed differently | acquisition differences we cannot undo | document (A9); it is part of "cohort" identity; discuss as limitation |
| 0.5-Hz high-pass on 5–8 s trials causes edge artefacts | spurious low-frequency differences | T4.4.2 padding/IIR decision; check PSD < 2 Hz; fit aperiodic from 2 Hz |
| Very small test folds (APAVA 23; ADFSU 12 HC) | wide CIs | report per-fold CIs; sensitivity analyses; no over-interpretation |
| LaBraM code/weights change or break | cannot extract | pin repo commit + checkpoint hash (T5.1) |
| Held-out results seen before plan freeze | analytic flexibility | T4.0 tag; decision log "before/after" column |

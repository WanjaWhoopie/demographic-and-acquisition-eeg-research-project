# Data audit report

**Date:** 29 September 2026 · **Covers:** ds004504, ADFSU, ADSZ, APAVA (+ ds006036, not used)
**Evidence:** EXP-001 (raw-data audit), EXP-002 (ADSZ–ADFSU overlap), direct inspection of every archive.
All numbers below come from the downloaded files unless marked *(from paper)*.

---

## 1. Summary

1. **ds004504 is clean and matches its documentation.** It has 65 AD + HC participants,
   eyes-closed, 19 channels at 500 Hz, and 5–21 min per person. It is the only cohort with age and sex.
2. **ADSZ is not an independent cohort.** 47 of its 48 files are exact copies of ADFSU recordings, and
   the 48th is a recording that ADFSU is missing. ADSZ's "24 AD + 24 HC" counts recordings: it holds
   12 AD + 12 HC people, each recorded eyes open and eyes closed.
3. **ADFSU needs cleaning before use.** One AD recording appears under five IDs (Paciente40–44), and two
   channel files (F1, F2) duplicate Fp1/Fp2. After cleaning it has **76 AD + 12 HC** unique people
   with 8 s of eyes-closed EEG each.
4. **APAVA is usable and now labelled.** The Google Drive copy (`APAVA.zip`) and the OSF copy hold
   identical signals. The Drive copy supplies the labels: 12 AD + 11 HC, 16 channels, 256 Hz,
   5-s trials, and 5–295 s per person.
5. **Decisions needed now (§6):**
   - **D-017:** drop ADSZ and run leave-one-cohort-out (LOCO) over **three** cohorts;
   - **D-018:** how much EEG per participant, since ADFSU caps it at 8 s;
   - **D-019:** how to handle the large amplitude differences between cohorts.

---

## 2. Cohorts at a glance

| | ds004504 | ADFSU | ADSZ | APAVA |
|---|---|---|---|---|
| Where | OpenNeuro ds004504 v1.0.9 | osf.io/2v5md (Vicchietti et al., 2023) | figshare 19091771 (Alves et al.) | Google Drive `APAVA.zip`; same data at osf.io/jbysn |
| Licence | CC0 | none stated on OSF | CC0 | not stated |
| Original recordings | AHEPA, Thessaloniki (Miltiadous et al., 2023) | Florida State Univ., Dr D. Duke (Pritchard et al., 1991) | **same FSU database** | Valladolid (Escudero et al., 2006) *(from LEAD)* |
| Format | BIDS, EEGLAB `.set` | one `.txt` per channel per recording | `.out` text, 19 columns, no header | `.npy` 1-s windows (50% overlap) + `label.npy`; OSF copy: FieldTrip `.mat` 5-s trials |
| People (AD / HC) | 36 / 29 (+23 FTD, excluded) | 80 folders → **76** unique / 12 | 12 / 12 (all also in ADFSU) | 12 / 11 |
| Channels | 19 (10–20) | 19 real (+ F1, F2 duplicates) | 19 | 16 (10–20 minus Fz, Cz, Pz) |
| Sampling rate | 500 Hz | 128 Hz | 128 Hz | 256 Hz |
| Reference | A1–A2 (linked ears) | linked mandible *(from paper)* | as ADFSU | common average (already applied) |
| Processing at source | online 0.4–50 Hz only (raw) | band-limited 0.5–30 Hz, artefacts removed by technician *(from paper)* | as ADFSU | re-referenced; artefact-free trials selected *(assumed)* |
| Condition | eyes closed | eyes closed **and** eyes open | eyes closed and eyes open | eyes closed *(from paper)* |
| Eyes-closed EEG per person | 307–1291 s (median 827) | 8 s (all) | 8 s | 5–295 s (median 140–168) |
| Demographics per person | age, sex, MMSE | none | none (group ages only) | none |
| Signal size (robust SD, 1–30 Hz) | 18.3 µV | 7.7 (AD) / 8.5 (HC), unit not stated | as ADFSU | 5.9 (AD) / 4.2 (HC), unit not stated |

---

## 3. Findings per dataset

### 3.1 ds004504 (primary cohort)
- **Download:** 65 AD + HC participants, 201 files, 2.1 GB (FTD and `derivatives/` skipped).
- **Consistency:** all recordings are `task-eyesclosed` with the same 19 channels in the same order,
  500 Hz, A1–A2 reference and 0.4–50 Hz online filter. All 16 target channels are present.
- **Signal quality:**
  - Units are plausible: 18.3 µV robust SD after 1–30 Hz (86.7 µV raw, inflated by slow drift).
  - No NaN, flat or clipped channels.
  - 13 recordings contain segments above 150 µV; epoch rejection will remove them.
  - Line noise at 50 Hz is strong (+19.6 dB) but lies outside the 0.5–30 Hz band.
- **Duplicates:** none. One spectral look-alike pair (sub-024/sub-028) was ruled out: different sex and
  age, and no time-domain match (r = 0.24).
- **Demographics:** female/male AD 24/12 vs HC 11/18 (Fisher p = 0.026). Age is balanced
  (66.4 ± 7.9 vs 67.9 ± 5.4, Mann–Whitney p = 0.38).
- **Spectra:** the expected AD slowing (more 4–8 Hz, weaker 10-Hz alpha). AD also has more power
  above 30 Hz (likely muscle); the 30-Hz low-pass removes it.

### 3.2 ADFSU
- **Source:** the link in our earlier notes (osf.io/jbysn) was the wrong dataset. The correct one,
  found through the paper's data statement, is osf.io/2v5md.
- **Contents:** 80 AD + 12 HC folders, each with eyes-closed and eyes-open 8-s recordings at 128 Hz.
- **Duplicate IDs:** AD Paciente40–44 are the same recording in every channel and both conditions.
  Keep one; 76 unique AD remain.
- **Duplicate channels:** `F1.txt` ≡ `Fp1.txt` and `F2.txt` ≡ `Fp2.txt` in all 182 recordings. Drop them.
- **Missing data:** Healthy/Eyes_open/Paciente5 is empty (the recording survives in ADSZ). That does
  not affect the eyes-closed primary analysis.
- **Quality:** no flat channels and no extreme segments. The data were cleaned at source.
- **Class balance:** 86% AD.

### 3.3 ADSZ
- **Contents:** 24 AD files (12 people × eyes closed/open) and 24 HC files (12 people × eyes closed/open).
- **Overlap:** 47/48 files are **exact** copies of ADFSU AD Paciente1–12 and Healthy Paciente1–12,
  with 0 label or condition disagreements.
- **Longer files:** 7 AD eyes-open files are 10–14 s; ADFSU keeps their first 8 s.
- **Correction:** an earlier reading of the AD file codes as "3 people × 4 segments" was wrong. The
  overlap check shows they are 12 different people.

### 3.4 APAVA
- **Two copies, identical signals.** `APAVA.zip` stores each 5-s trial as nine 1-s windows with
  50% overlap. Rebuilding the trials reproduces the OSF FieldTrip copy exactly (r = 1.000,
  scale = 1.000, all 23 participants).
  - Use the 5-s trials, **never the overlapping 1-s windows as separate samples**.
- **Labels** (`label.npy`, participant IDs 1–23 in order): 12 coded 1 and 11 coded 0, i.e. 1 = AD
  and 0 = HC (inferred from the published 12 AD / 11 HC).
- **Channels and processing:** 16 channels (C3 C4 F3 F4 F7 F8 Fp1 Fp2 O1 O2 P3 P4 T3 T4 T5 T6),
  256 Hz, already common-average referenced.
- **Recording time:** 1–59 trials per person (5–295 s). HC participant 05 has a single 5-s trial.
- **Quality:** no flat channels and no extreme segments.

### 3.5 ds006036 (not used)
It contains the same 88 AHEPA participants as ds004504, recorded eyes open with photic stimulation. It
is not an independent cohort (D-016).

---

## 4. Problems that cut across datasets

| Problem | Why it matters | Where handled |
|---|---|---|
| ADSZ ⊂ ADFSU | the same people would sit in training and test folds | D-017 |
| ADFSU gives only 8 s per person | the equal-length rule (T4.8) then limits **every** cohort to 8 s, discarding > 99% of ds004504 | D-018 |
| Amplitude differs about 2–4× between cohorts (18 vs 8 vs 5), and in APAVA between AD and HC | LaBraM is amplitude-sensitive, so amplitude alone could reveal cohort (and, in APAVA, diagnosis) | D-019 |
| Different processing at source (raw vs band-limited and cleaned vs average-referenced) | a cohort signature we cannot undo; our common pipeline narrows it | preprocessing + limitations |
| Different references (linked ears / linked mandible / average) | our common average reference over 16 channels makes them comparable | D-012 |
| Class imbalance (ADFSU 86% AD) | inflates accuracy-type metrics; confounds cohort with diagnosis | AUROC primary; ADFSU sensitivity analyses (D-011) |
| Demographics only in ds004504 | age/sex effects can only be tested there | D-007 |
| Units undocumented for FSU and APAVA | LaBraM expects µV/100 | D-019; check with sources |

---

## 5. Cohorts after the proposed decisions

| Cohort | AD | HC | Eyes-closed EEG per person | Role |
|---|---|---|---|---|
| ds004504 | 36 | 29 | 5–21 min | primary; the only cohort with demographics |
| ADFSU (deduplicated) | 76 | 12 | 8 s | external cohort |
| APAVA | 12 | 11 (10 if HC-05 is excluded, D-018) | 5–295 s | external cohort |
| **Total** | **124** | **52 (51)** | | 3 LOCO folds |

(The proposal said 228 people across four cohorts. After removing ADSZ and the ADFSU duplicates,
the total is 176, or 175 if HC-05 is excluded.)

---

## 6. Decisions needed

### D-017 – ADSZ and ADFSU are the same source (**recommend: drop ADSZ**)

**The problem.** The design treats each cohort as an independent recording site, so that
leave-one-cohort-out tests generalisation to people, equipment and protocols the model has never seen.
ADSZ breaks this: all 24 ADSZ people are also in ADFSU. The same person's EEG would be in the training
set when the other cohort is held out, which is exactly the subject leakage the project is designed to
avoid. It would also inflate the apparent number of independent cohorts from three to four.

**Options.**

| Option | What it means | Verdict |
|---|---|---|
| **A. Drop ADSZ; keep deduplicated ADFSU (76 AD / 12 HC)** | one FSU cohort; LOCO over ds004504, ADFSU, APAVA | **Recommended.** No overlap, keeps all FSU people, and ADFSU's imbalance is already covered by D-011 sensitivity analyses (AD subsampled to the HC count is essentially a balanced ADSZ-like set) |
| B. Keep ADSZ; remove its 24 people from ADFSU | ADFSU would keep 64 AD and **0 HC** | Not viable: AUROC cannot be computed for an AD-only fold |
| C. Keep both as "cohorts" | two folds from one site, one system, same people | Not valid: violates the independence LOCO relies on |

**Consequences of A.**
- LOCO has 3 folds instead of 4, so the fold-averaged ΔAUROC rests on fewer folds; report every fold.
- ADFSU becomes the largest external cohort, but with only 12 HC. Its per-fold AUROC CI will be wide.
- **Update the proposal, slides and configs:** cohort list, the "228 participants" figure and the
  LOCO diagram (4 → 3 folds).
- ADSZ is still worth one line in the write-up, as a documented example of hidden duplication
  between public AD-EEG datasets. It supports the project's leakage argument.

### D-018 – How much EEG per participant (**recommend: 8 s for the primary analysis**)
ADFSU has exactly 8 s per person, so the prespecified equal-length rule (T4.8: same number of clean
epochs for everyone) sets K = 2 epochs of 4 s for all cohorts.
- **Recommended:** keep K = 2 (8 s) for the primary cross-cohort analysis, so that recording length
  cannot act as a shortcut.
- **Recommended:** exclude APAVA HC-05 (only 5 s, i.e. 1 epoch) under the "fewer than 2 clean epochs"
  rule.
- **Add a within-ds004504 sensitivity analysis** using longer data (e.g. 60 s) to show how much
  signal the 8-s cap costs.
- If ADFSU epochs are rejected for artefacts, that person has fewer than 2 epochs and is excluded.
  ADFSU was cleaned at source, so few rejections are expected.

### D-019 – Amplitude differences between cohorts (**recommend: decide before preprocessing**)
After 1–30 Hz filtering, typical signal size is 18.3 µV (ds004504), about 8 (ADFSU) and about 5 (APAVA,
AD 5.9 vs HC 4.2). The FSU and APAVA units are undocumented. Options:
1. keep physical units (µV/100 for LaBraM) and treat amplitude as part of "acquisition", which the
   cohort control should then remove;
2. scale each recording to unit variance before LaBraM, which removes absolute amplitude from every
   cohort (including any genuine AD amplitude effect).

**Suggested approach:** option 1 as primary, because it matches the model's training convention and
lets the cohort probe measure the effect. Run option 2 as a prespecified sensitivity analysis. First
confirm the units with the dataset sources, or at least sanity-check them against typical elderly EEG
amplitudes.

---

## 7. Status and next steps

| Done | Next |
|---|---|
| ds004504 downloaded and audited (EXP-001) | agree D-017, D-018, D-019 with the mentor; log them as decided |
| ADFSU, ADSZ, APAVA downloaded and inspected | write loaders for ADFSU and APAVA (APAVA: rebuild 5-s trials) and run the A1–A12 audit script on them |
| ADSZ ⊂ ADFSU shown exactly (EXP-002) | update the proposal, slides and `configs/datasets.yaml` for three cohorts |
| APAVA labels obtained; copies shown identical | confirm FSU/APAVA amplitude units; freeze the analysis plan (T4.0) |

## Appendix – files and checksums
| File | Size | sha256 (first 12 characters) |
|---|---|---|
| ds004504 `participants.tsv` | 1.7 kB | `bd17cf02ec97` |
| ADFSU `EEG_data.zip` (osf.io/download/heaw6) | 6.6 MB | `f5b30df4fd0d` |
| ADSZ `dataset.zip` (figshare file 33928037) | 18.3 MB | `bfa0306a0fd6` |
| APAVA OSF `AD_Data.tar.gz` (osf.io/download/xy8qa) | 51.1 MB | `125b85ae83c5` |
| APAVA `APAVA.zip` (Google Drive) | 187 MB unpacked | manual download |

Participant-level tables stay local in `data/metadata/`. The aggregate tables are
`results/tables/T00_audit_ds004504_summary.csv` and `T02_overlap_summary.csv`.

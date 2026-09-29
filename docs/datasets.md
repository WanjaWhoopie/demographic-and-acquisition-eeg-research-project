# Dataset cards

Fill every `TODO` during the data audit (WORKPLAN Phase 2). A field is only "confirmed" once
someone has checked it in the downloaded files, not in a paper.

Legend: ✅ confirmed in files · 📄 from paper/descriptor only · ❓ unknown

---

## ds004504 (AHEPA)
| Field | Value | Status |
|---|---|---|
| Source | OpenNeuro `ds004504` – https://openneuro.org/datasets/ds004504 | 📄 |
| Descriptor | Miltiadous et al. (2023), *Data*, 8(6), 95. doi:10.3390/data8060095 | 📄 |
| Version / download date | snapshot 1.0.9 (doi:10.18112/openneuro.ds004504.v1.0.9) / downloaded 2026-09-29 | ✅ |
| Licence | CC0 (dataset_description.json) | ✅ |
| Groups | 36 AD, 23 FTD, 29 HC | 📄 |
| Montage | 19-ch 10–20; labels Fp1 Fp2 F3 F4 C3 C4 P3 P4 O1 O2 F7 F8 T3 T4 T5 T6 Fz Cz Pz; units µV | ✅ (sub-001) |
| Sampling rate | 500 Hz | ✅ (all 65) |
| Reference | A1 A2 (linked ears) | ✅ (all 65) |
| Hardware / online filter | Nihon Kohden EEG 2100; 0.4–50 Hz; line frequency 50 Hz | ✅ (all 65) |
| Condition | resting, eyes closed | 📄 |
| Recording length | 307.1–1291.1 s, median 826.7 s (AD + HC, from sidecars) | ✅ |
| Demographics | participants.tsv: participant_id, Gender, Age, Group (A/F/C), MMSE | ✅ |
| Derivatives | preprocessed version (ASR + ICA) also released – **not used for the primary pipeline** | 📄 |
| Known issues | Sex imbalance: female/male AD 24/12 vs HC 11/18 (Fisher p = 0.026); age balanced (66.4 ± 7.9 vs 67.9 ± 5.4, Mann–Whitney p = 0.38) | ✅ |
| Size used | AD + HC raw = 2.16 GB, 201 files (FTD 0.67 GB and derivatives 2.95 GB skipped) | ✅ |
| Download | `python scripts/download_ds004504.py` → MANIFEST.tsv with sha256 per file | |
| Checksum | participants.tsv sha256 `bd17cf02ec9733c9029d4a6d977b2918309b3c667ff9ceb1b5dce6e3cebccbc1`; all files in local MANIFEST.tsv | ✅ |

### Related dataset not used: ds006036
Eyes-open photic-stimulation recordings (5–30 Hz) of the **same** 88 participants as ds004504, recorded after the
eyes-closed session (OpenNeuro ds006036 v1.0.6, CC0, 1.13 GB). Not an independent cohort – excluded from the design (D-016).

## ADFSU
| Field | Value | Status |
|---|---|---|
| Original recordings | Florida State University database, provided by Dr Dennis Duke (Pritchard, Duke & Coburn, 1991) | 📄 |
| Name "ADFSU" from | LEAD (Wang et al., 2025) → Vicchietti et al. (2023), *Sci Rep* 13:8184, doi:10.1038/s41598-023-32664-8 | 📄 |
| Download link | https://osf.io/2v5md – "Data from: Computational methods of EEG signals analysis for Alzheimer's disease classification" (Vicchietti et al., created 2023-01-25), `EEG_data.zip` 6.6 MB; no licence set on OSF | ✅ exists (not yet downloaded) |
| ⚠️ Link in our notes | https://osf.io/jbysn exists but is a different dataset (Smith, 2017: Escudero et al. 2006 AD data + NBT healthy data) | ✅ |
| Licence / access terms | TODO | ❓ |
| Groups | 80 probable AD, 12 HC (NINCDS-ADRDA, DSM-III-R) | 📄 |
| Channels | 19: Fp1 Fp2 F3 F4 F7 F8 Fz C3 C4 Cz P3 P4 Pz T3 T4 T5 T6 O1 O2 | 📄 |
| Sampling rate | 128 Hz | 📄 |
| Condition | each participant recorded eyes open (visual fixation) **and** eyes closed; reference linked mandible (Pineda et al., 2020) | 📄 |
| Trial length | 8 s segments | 📄 |
| Band limits at source | 0.5–30 Hz; movement artefacts removed by an EEG technician | 📄 |
| Distributed as raw or already preprocessed? | Preprocessed at source (band-limited, artefact-cleaned segments) | 📄 |
| Participant IDs available? | TODO – needed for subject-level splits | ❓ |
| Demographics | none per participant | 📄 |
| Known issues | severe class imbalance; **same source database as ADSZ** – overlap likely (Phase 3) | 📄 |

## ADSZ
| Field | Value | Status |
|---|---|---|
| Download | figshare "Alzheimer's disease and Schizophrenia" – https://doi.org/10.6084/m9.figshare.19091771.v1 (`dataset.zip`, 18.3 MB, published 2022-01-29) | ✅ exists |
| Licence | CC0 | ✅ |
| Paper | Alves, C. L., Pineda, A. M., et al. – arXiv:2110.06140 ("EEG functional connectivity and deep learning for automatic diagnosis of brain disorders: Alzheimer's disease and schizophrenia"); LEAD cites it as Alves et al. (2022) | 📄 |
| Original recordings | FSU / Dennis Duke database (cited via Pineda et al., 2020 and Pritchard et al., 1991) – **same origin as ADFSU** | 📄 |
| Groups | 24 AD, 24 HC; group ages only (HC 72 ± 11, AD 69 ± 16 years) | 📄 |
| Channels | 19 | 📄 |
| Sampling rate | 128 Hz | 📄 |
| Files (checked 2026-09-29) | `dataset/alzheimer/AD/`: `ec0101`–`ec0304` + `eo0101`–`eo0304` (24 files); `dataset/alzheimer/Healthy/`: `eeg20`–`eeg35` × {`c1`, `o1`} (24 files, 12 people). Each file = 1024 samples × 19 channels (8 s at 128 Hz), plain text; robust SD ≈ 8.5 (units not stated). Also a schizophrenia set (not used). | ✅ |
| Condition | `ec`/`c1` = eyes closed, `eo`/`o1` = eyes open – **each person appears in both** | ✅ |
| Trial length | 8 s per file | ✅ |
| ⚠️ Participant count | Healthy = **12 people** (not 24). AD codes `01xx`–`03xx` look like **3 people × 4 consecutive 8-s segments**: segment boundaries are continuous (e.g. ec0102→ec0103) and spectra correlate within a code group (r = 0.50) but not between groups (r = −0.01). So ADSZ may be only **3 AD + 12 HC people** – confirm against ADFSU in Phase 3. | ✅ (inferred) |
| Raw or preprocessed? | preprocessed at source (artefact-free segments) | 📄 |
| Known issues | ⚠️ may be 12 + 12 people each recorded eyes open and eyes closed (Pineda et al., 2020 count "24 healthy subjects (groups A and B)"); overlap with ADFSU likely | 📄 |

## APAVA
| Field | Value | Status |
|---|---|---|
| Original recordings | Escudero et al. (2006), *Physiological Measurement* 27(11):1091–1106 (Valladolid) – as cited by LEAD | 📄 |
| Download | Google Drive `APAVA.zip` (team link) – **requires Google sign-in**; download manually | ✅ exists (contents not checked) |
| Other copy | OSF https://osf.io/jbysn → `AD_Data.tar.gz` (51 MB, sha256 `125b85ae…d0812`), Smith (2017). Checked 2026-09-29: 23 FieldTrip files `preproctrials01–23.mat`, 16 channels (C3 C4 F3 F4 F7 F8 Fp1 Fp2 O1 O2 P3 P4 T3 T4 T5 T6 = 10–20 minus Fz/Cz/Pz), 256 Hz, 5-s trials (1280 samples), 1–59 trials per participant, already re-referenced to the common average. **No diagnosis labels in the files.** | ✅ |
| Licence / access terms | TODO | ❓ |
| Groups | 12 AD, 11 HC | 📄 |
| Channels | 16 – 10–20 without Fz, Cz, Pz (per slides) – TODO confirm labels | 📄 |
| Sampling rate | 256 Hz | 📄 |
| Condition | eyes closed | 📄 |
| Trial length | 5 s, multiple trials per participant | 📄 |
| Raw or preprocessed? | TODO | ❓ |
| Known issues | smallest cohort; wide CIs | 📄 |

---

## Channel mapping (fill in T4.2)
| Canonical (old 10–20) | ds004504 label | ADFSU label | ADSZ label | APAVA label | LaBraM label |
|---|---|---|---|---|---|
| Fp1 | | | | | |
| Fp2 | | | | | |
| F7 | | | | | |
| F3 | | | | | |
| F4 | | | | | |
| F8 | | | | | |
| T3 (=T7) | | | | | |
| C3 | | | | | |
| C4 | | | | | |
| T4 (=T8) | | | | | |
| T5 (=P7) | | | | | |
| P3 | | | | | |
| P4 | | | | | |
| T6 (=P8) | | | | | |
| O1 | | | | | |
| O2 | | | | | |

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
| Version / download date | snapshot 1.0.9 (doi:10.18112/openneuro.ds004504.v1.0.9) / download date TODO | ✅ / ❓ |
| Licence | CC0 (dataset_description.json) | ✅ |
| Groups | 36 AD, 23 FTD, 29 HC | 📄 |
| Montage | 19-ch 10–20; labels Fp1 Fp2 F3 F4 C3 C4 P3 P4 O1 O2 F7 F8 T3 T4 T5 T6 Fz Cz Pz; units µV | ✅ (sub-001) |
| Sampling rate | 500 Hz | ✅ (sub-001) |
| Reference | A1 A2 (linked ears) | ✅ (sub-001) |
| Hardware / online filter | Nihon Kohden EEG 2100; 0.4–50 Hz; line frequency 50 Hz | ✅ (sub-001) |
| Condition | resting, eyes closed | 📄 |
| Recording length | sub-001 = 599.8 s; range across participants TODO (slides say ~13 min) | ✅ / ❓ |
| Demographics | participants.tsv: participant_id, Gender, Age, Group (A/F/C), MMSE | ✅ |
| Derivatives | preprocessed version (ASR + ICA) also released – **not used for the primary pipeline** | 📄 |
| Known issues | Sex imbalance: female/male AD 24/12 vs HC 11/18 (Fisher p = 0.026); age balanced (66.4 ± 7.9 vs 67.9 ± 5.4, Mann–Whitney p = 0.38) | ✅ |
| Size used | AD + HC raw = 2.16 GB, 201 files (FTD 0.67 GB and derivatives 2.95 GB skipped) | ✅ |
| Download | `python scripts/download_ds004504.py` → MANIFEST.tsv with sha256 per file | |
| Checksum | TODO (sha256 of participants.tsv from MANIFEST.tsv) | ❓ |

## ADFSU
| Field | Value | Status |
|---|---|---|
| Original source + citation | TODO – trace from the paper that named the cohort (check LEAD, Wang et al., 2025, data section) back to the original recording study | ❓ |
| Licence / access terms | TODO | ❓ |
| Groups | ~80 AD, ~12 HC | 📄 |
| Channels | 19 (10–20) | 📄 |
| Sampling rate | 128 Hz | 📄 |
| Condition | eyes open + eyes closed – **are trials labelled by condition?** TODO | ❓ |
| Trial length / trials per participant | 8 s / TODO | 📄/❓ |
| Band limits at source | 0.5–30 Hz (per notes) | 📄 |
| Distributed as raw or already preprocessed? | TODO – decides what our pipeline can still control | ❓ |
| Participant IDs available? | TODO – needed for subject-level splits | ❓ |
| Known issues | severe class imbalance; possible overlap with ADSZ | 📄 |

## ADSZ
| Field | Value | Status |
|---|---|---|
| Original source + citation | TODO | ❓ |
| Licence / access terms | TODO | ❓ |
| Groups | 24 AD, 24 HC | 📄 |
| Channels | 19 | 📄 |
| Sampling rate | 128 Hz | 📄 |
| Condition | eyes open + closed (proposal) / "resting" (slides) – TODO resolve | ❓ |
| Trial length | 8 s | 📄 |
| Raw or preprocessed? | TODO | ❓ |
| Known issues | possible overlap with ADFSU | 📄 |

## APAVA
| Field | Value | Status |
|---|---|---|
| Original source + citation | TODO | ❓ |
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

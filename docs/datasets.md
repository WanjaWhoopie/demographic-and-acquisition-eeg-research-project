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
| Version / download date | TODO | ❓ |
| Licence | TODO (check dataset_description.json) | ❓ |
| Groups | 36 AD, 23 FTD, 29 HC | 📄 |
| Montage | 19-ch 10–20, monopolar | 📄 |
| Sampling rate | 500 Hz | 📄 |
| Reference | TODO (check channels.tsv / sidecar JSON) | ❓ |
| Condition | resting, eyes closed | 📄 |
| Recording length | ~13 min (per slides) | 📄 |
| Demographics | age, sex, MMSE in participants.tsv | 📄 |
| Derivatives | preprocessed version (ASR + ICA) also released – **not used for the primary pipeline** | 📄 |
| Known issues | Sex imbalance: ~67% female AD vs ~38% HC (Fisher p ≈ 0.026) | 📄 |
| Checksum | TODO | ❓ |

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

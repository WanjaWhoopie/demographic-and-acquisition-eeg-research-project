# Claims to verify against a primary source

Tick when checked and write where (paper + page/table, or file + command).

- [ ] **Martin2023interpretable** – proposal §2.7 says "only a minority of studies explicitly
      evaluated generalizability using external datasets". Abstract reports 45/92 used a hold-out
      set (internal or independent). Find the external-only count in the full text.
- [ ] **ADFSU** band-limited to 0.5–30 Hz at source (slides/notes). Check original source + PSD.
- [ ] **APAVA** has exactly the 19-ch 10–20 set minus Fz, Cz, Pz. Check channel labels in files.
- [x] **ADSZ** condition and counting: 12 AD + 12 HC people, each recorded eyes open and eyes closed (EXP-002).
- [x] **ADSZ–ADFSU overlap** – ADSZ is a subset of ADFSU: 47/48 files identical (EXP-002).
- [ ] **FSU amplitude unit** – stored values have robust SD ≈ 7.8; confirm µV (or scale) before LaBraM scaling.
- [x] **ADFSU download link** – https://osf.io/2v5md (`EEG_data.zip`).
- [x] **APAVA copies** – Google Drive APAVA.zip and OSF jbysn hold identical signals; labels from APAVA.zip (12 AD / 11 HC).
- [ ] **APAVA label coding** – 1 = AD inferred from counts; confirm against the source paper or the Medformer/LEAD data loader.
- [ ] **Escudero et al. (2006)** – confirm the citation and cohort description from the paper itself.
- [x] **ds004504 sex split** – confirmed from participants.tsv: 24/36 vs 11/29 female, Fisher p = 0.026 (T2.1.5).
- [ ] **LaBraM** input convention: 200 Hz, 1-s patches, µV/100 scaling, channel-name list, max
      patches per sample – check the official code (T5.1).
- [ ] **LEAD** – read the data section; does it define ADFSU/ADSZ/APAVA and how were they preprocessed?
- [x] **Slide 7 "Negative-control audit (2026)"** – Zare (2026), arXiv:2607.24519, "A Negative-Control Protocol for Clinical EEG Foundation-Model Benchmarks".
- [ ] **LinHou2026labramdementia** – which dataset, and does "dementia" pool AD with FTD? (full text)
- [ ] **Zare2026negcontrol** – was LaBraM among the five encoders?
- [ ] **LaBraM pretraining size** – "over 2,500 hours" (quoted by Lin, Hou & Jung) – confirm in Jiang et al. (2024).
- [ ] **ds006036 citation** – author list and year for the dataset reference.
- [ ] Primary sources for AD EEG markers and ageing-related EEG change (draft lit review §2, §4).
- [ ] Full author lists for entries ending in "et al." in the proposal reference list.

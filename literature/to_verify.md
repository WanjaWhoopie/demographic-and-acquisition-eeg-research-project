# Claims to verify against a primary source

Tick when checked and write where (paper + page/table, or file + command).

- [x] **Martin2023interpretable** – full text (PMC10955773), Results 4.1: "Only 17 studies used data from external sources to create an independent test set" (of 92); 45/92 used any hold-out set.
- [x] **ADFSU** band-limited to 0.5–30 Hz at source – stated in Vicchietti et al. (2023) and visible in the PSD (40–48 Hz is 7 dB below 20–30 Hz).
- [x] **APAVA** channels confirmed from the OSF copy's labels: 10–20 minus Fz, Cz, Pz.
- [x] **ADSZ** condition and counting: 12 AD + 12 HC people, each recorded eyes open and eyes closed (EXP-002).
- [x] **ADSZ–ADFSU overlap** – ADSZ is a subset of ADFSU: 47/48 files identical (EXP-002).
- [ ] **FSU amplitude unit** – stored values have robust SD ≈ 7.8; confirm µV (or scale) before LaBraM scaling.
- [x] **ADFSU download link** – https://osf.io/2v5md (`EEG_data.zip`).
- [x] **APAVA copies** – Google Drive APAVA.zip and OSF jbysn hold identical signals; labels from APAVA.zip (12 AD / 11 HC).
- [ ] **APAVA label coding** – 1 = AD inferred from counts; confirm against the source paper or the Medformer/LEAD data loader.
- [x] **Escudero et al. (2006)** – citation confirmed: *Physiol. Meas.* 27(11):1091–1106, doi:10.1088/0967-3334/27/11/004. The abstract reports 11 AD + 11 controls, 19 electrodes; APAVA has 12 AD + 11 HC, 16 channels, so the match to APAVA is still unconfirmed (noted in the report).
- [x] **ds004504 sex split** – confirmed from participants.tsv: 24/36 vs 11/29 female, Fisher p = 0.026 (T2.1.5).
- [ ] **LaBraM** input convention: 200 Hz, 1-s patches, µV/100 scaling, channel-name list, max
      patches per sample – check the official code (T5.1).
- [x] **LEAD** – v5 (TMLR 2026), Table 2 and §5.1: ADFSU (92), ADSZ (48), APAVA (23) and ADFTD (= ds004504, 88) are downstream fine-tune sets only; pretraining uses 9 non-AD sets plus AD-Auditory, BrainLat, P-ADIC and CAUEEG. Table 3: 100% subject-level F1 on both ADFSU and ADSZ, for LEAD and the compared models.
- [x] **Slide 7 "Negative-control audit (2026)"** – Zare (2026), arXiv:2607.24519, "A Negative-Control Protocol for Clinical EEG Foundation-Model Benchmarks".
- [x] **LinHou2026labramdementia** – private four-centre Taiwanese cohort (30 ch, 120 s eyes open, 2021–2022; 206 after excluding MCI); "Dementia" subtype never stated; random forest AUROC 0.89, logistic regression and linear SVM near chance (arXiv 2608.27719 HTML). Report §2.2 updated.
- [x] **Zare2026negcontrol** – yes: §1.1 of v3 lists LaBraM, EEGMamba, CBraMod, REVE, BIOT with frozen probes; LaBraM ds004504 AD vs HC AUROC 75.3 ± 6.5 (Table 3); LaBraM not in controls 2–4.
- [x] **LaBraM pretraining size** – Jiang et al. (2024) abstract: "about 2,500 hours of various types of EEG signals from around 20 datasets"; Appendix D: 2534.78 hours.
- [ ] **ds006036 citation** – author list and year for the dataset reference.
- [x] Primary sources for AD EEG markers and ageing-related EEG change: Jeong (2004); Babiloni et al. (2020); Ishii et al. (2017); Voytek et al. (2015) – added to the final report.
- [x] **Pritchard, Duke & Coburn (1991)** – *Dementia* 2(2):102–105, doi:10.1159/000107183.
- [x] **Vicchietti et al. (2023)** – *Sci Rep* 13:8184, doi:10.1038/s41598-023-32664-8 (160 AD and 24 HC records, i.e. 80 AD + 12 HC × eyes open/closed).
- [x] Report reference authors confirmed on Crossref (Vicchietti 2023; Voytek 2015, full list; Ishii 2017; Pritchard, Duke & Coburn 1991 order).
- [x] **APAVA source** – matches Smith, Abásolo & Escudero (2017) PLOS ONE e0186164: AFAVA association, University Hospital of Valladolid, 16 ch, 5-s epochs of 1280 points; OSF jbysn says "based on Escudero et al.". Recording years not stated anywhere.
- [ ] Full author lists for entries ending in "et al." in the proposal reference list.

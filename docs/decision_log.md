# Decision log

Every methodological choice that could change a result goes here **before** the result is
seen. After the analysis-plan freeze (git tag `analysis-plan-v1`), a change needs a new entry
that says why and whether it was made before or after looking at held-out results.

| ID | Date | Decision | Reason | Before/after seeing results |
|---|---|---|---|---|
| D-001 | proposal | Participant is the unit of splitting and inference | Epoch-level splits inflate performance (Brookshire et al., 2024; Miltiadous et al., 2026) | before |
| D-002 | proposal | Eyes-closed recordings only in the primary analysis | Avoid recording-condition shortcuts | before |
| D-003 | proposal | 16 common channels (19-ch 10–20 minus Fz, Cz, Pz) | APAVA lacks midline channels | before |
| D-004 | proposal | 0.5–30 Hz band-pass for all cohorts | Narrowest source band (ADFSU); stops high-frequency content revealing cohort | before |
| D-005 | proposal | Resample to 200 Hz | LaBraM input rate | before |
| D-006 | proposal | Frozen LaBraM, linear classifiers | Measure what is already encoded; avoid new shortcuts | before |
| D-007 | proposal | Age/sex probing and control within ds004504 only | Only cohort with demographics | before |
| D-008 | proposal | No combined demographic + cohort control in LOCO | Held-out cohorts lack age/sex | before |
| D-009 | proposal | Prevalence-balanced cohort means; two test-time variants (pooled training mean; label-free test mean) | Avoid removing diagnosis with cohort; avoid test-label leakage | before |
| D-010 | proposal | Primary outcome = mean per-fold ΔAUROC over LOCO folds | AUROC is prevalence-independent; folds differ in size/balance | before |
| D-011 | proposal | Sensitivity: LOCO without ADFSU; ADFSU AD subsampled to HC count | ADFSU 87% AD confounds cohort with diagnosis | before |
| D-012 | workplan | Common average reference after channel selection | Source references differ; CAR is cohort-agnostic | before |
| D-013 | workplan | No ICA; amplitude-based epoch rejection for all cohorts | 5–8 s trials too short for stable ICA; same rule for every cohort | before |
| D-014 | workplan | No notch filter by default | Line noise (50/60 Hz) is above the 30 Hz low-pass | before |
| D-015 | workplan | 4-s epochs | Fits 8-s and 5-s trials; 16 ch × 4 patches per LaBraM input | before |
| D-017 | 2026-09-29 | **PROPOSED – needs team/mentor agreement.** Drop ADSZ as a cohort; use ADFSU as the single FSU cohort. Remove ADFSU AD Paciente41–44 (duplicates of 40) and the F1/F2 channels. Primary LOCO becomes 3 cohorts: ds004504, ADFSU, APAVA | EXP-002: ADSZ is a subset of ADFSU, so keeping both would put the same people in train and test folds | before |
| D-018 | 2026-09-29 | **PROPOSED.** Equal-length rule gives K = 2 × 4-s epochs (8 s) for every cohort, set by ADFSU; exclude APAVA HC-05 (one 5-s trial); add a within-ds004504 sensitivity analysis with longer data | ADFSU has exactly 8 s per person | before |
| D-019 | 2026-09-29 | **PROPOSED.** Keep physical units (µV/100) for LaBraM as primary; per-recording variance scaling as a sensitivity analysis; confirm FSU/APAVA units first | Robust SD 18.3 µV (ds004504) vs ~8 (ADFSU) vs ~5 (APAVA), and APAVA AD > HC | before |
| D-016 | lit review | ds006036 not used as a cohort | Same 88 participants as ds004504 (eyes open, photic stimulation); using it as a held-out cohort would leak subjects and add a photic-driving signal. Possible subject-grouped condition-shift extension only | before |

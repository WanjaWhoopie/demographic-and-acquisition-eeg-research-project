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
| D-016 | lit review | ds006036 not used as a cohort | Same 88 participants as ds004504 (eyes open, photic stimulation); using it as a held-out cohort would leak subjects and add a photic-driving signal. Possible subject-grouped condition-shift extension only | before |
| D-017 | 2026-10-27 | Drop ADSZ as a cohort; use deduplicated ADFSU (drop AD Paciente41–44, drop F1/F2 channels). Primary LOCO over 3 cohorts: ds004504, ADFSU, APAVA | EXP-002: ADSZ is a subset of ADFSU; keeping both leaks people across folds | before |
| D-018 | 2026-10-27 | Use **all available eyes-closed data** per participant in the primary analysis (team decision; replaces the equal-length rule T4.8). Participant pooling restricted to mean and median (mean ⊕ SD dropped, its noise depends on epoch count). Sensitivity analysis: every participant cropped to 8 s (2 epochs), APAVA HC-05 then excluded | More signal for ds004504/APAVA. Risk recorded: epoch count differs by cohort (ADFSU 2, APAVA ~1–59, ds004504 ~75–320), so embedding noise level could itself reveal cohort; the 8-s sensitivity tests this | before |
| D-019 | 2026-10-27 | Keep physical units (µV, scaled by 1/100 for LaBraM) in the primary analysis; per-recording variance scaling as a sensitivity analysis. ADFSU and APAVA stored values treated as µV (undocumented; plausible range) | Robust SD 18.3 µV (ds004504) vs ~8 (ADFSU) vs ~5 (APAVA); matches LaBraM's training convention while letting probes measure the amplitude effect | before |
| D-020 | 2026-10-27 | Band-pass 0.5–30 Hz with a 4th-order zero-phase Butterworth (second-order sections, forward–backward) applied per continuous segment, for every cohort (resolves T4.4.2) | An FIR 0.5-Hz high-pass needs ~6.6 s, longer than APAVA's 5-s trials; one IIR design works for all segment lengths | before |
| D-021 | 2026-10-27 | Epochs never span two source segments; APAVA's 5-s trials each give one 4-s epoch (last 1 s dropped); ADFSU's 8-s recordings give two | APAVA trials are not contiguous in time | before |

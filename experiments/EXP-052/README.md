# EXP-052 – Classifier score vs classical EEG markers (exploratory)

## Before running (committed before results were seen; D-036)
- **Objective:** O5 · **Question:** Does the cross-cohort AD score from LaBraM track the known EEG markers of AD?
- **Markers per participant** (preprocessed epochs): relative theta, relative alpha, theta/alpha ratio and peak alpha frequency (centre of gravity 7–13 Hz), each as the global mean and the posterior mean (O1, O2, P3, P4, T5, T6); plus the global aperiodic exponent from the Phase 6 features (9 markers).
- **Score:** logit of the out-of-fold LOCO probability from EXP-031, for the original and the centred (i) classifier.
- **Analysis:** Spearman correlation of score with each marker *within* each held-out cohort, so cohort differences in markers cannot create the correlation. Benjamini–Hochberg FDR across 9 markers × 3 cohorts, separately per classifier. As a reference, each marker's own Spearman correlation with diagnosis is reported alongside.
- **Expected (T11.5):** score correlates positively with theta and the theta/alpha ratio, and negatively with alpha and peak alpha frequency. No directional prior for the aperiodic exponent.
- **Reading:** correlations in the expected direction across cohorts support the view that the score tracks EEG slowing. Correlations of the same size as the marker–diagnosis correlation could arise just because both relate to diagnosis, so this shows plausibility, not mechanism (T11.6).
- **Script:** `scripts/11_interpret.py --part markers` → `results/tables/T11_markers.csv`

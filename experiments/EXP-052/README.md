# EXP-052 – Classifier score vs classical EEG markers (exploratory)

## Before running (committed before results were seen; D-036)
- **Objective:** O5 · **Question:** Does the cross-cohort AD score from LaBraM track the known EEG markers of AD?
- **Markers per participant** (preprocessed epochs): relative theta, relative alpha, theta/alpha ratio and peak alpha frequency (centre of gravity 7–13 Hz), each as the global mean and the posterior mean (O1, O2, P3, P4, T5, T6); plus the global aperiodic exponent from the Phase 6 features (9 markers).
- **Score:** logit of the out-of-fold LOCO probability from EXP-031, for the original and the centred (i) classifier.
- **Analysis:** Spearman correlation of score with each marker *within* each held-out cohort, so cohort differences in markers cannot create the correlation. Benjamini–Hochberg FDR across 9 markers × 3 cohorts, separately per classifier. As a reference, each marker's own Spearman correlation with diagnosis is reported alongside.
- **Expected (T11.5):** score correlates positively with theta and the theta/alpha ratio, and negatively with alpha and peak alpha frequency. No directional prior for the aperiodic exponent.
- **Reading:** correlations in the expected direction across cohorts support the view that the score tracks EEG slowing. Correlations of the same size as the marker–diagnosis correlation could arise just because both relate to diagnosis, so this shows plausibility, not mechanism (T11.6).
- **Script:** `scripts/11_interpret.py --part markers` → `results/tables/T11_markers.csv`

## Run record
- **Date:** 2026-11-12 · same run as EXP-050 (`python scripts/11_interpret.py`)
- **Output:** `results/tables/T11_markers.csv`

## Results
Spearman ρ between the cross-cohort AD score (centred classifier) and each marker, within each held-out cohort. For comparison, each marker's own correlation with diagnosis is given in brackets. n = 88 ADFSU, 23 APAVA, 65 ds004504.

| Marker | ADFSU | APAVA | ds004504 |
|---|---|---|---|
| Theta/alpha ratio, posterior | 0.51 (0.47) | 0.89 (0.67) | 0.91 (0.66) |
| Theta/alpha ratio, global | 0.52 (0.48) | 0.91 (0.71) | 0.90 (0.65) |
| Relative theta, posterior | 0.64 (0.56) | 0.84 (0.68) | 0.86 (0.62) |
| Relative theta, global | 0.59 (0.57) | 0.84 (0.67) | 0.84 (0.61) |
| Relative alpha, posterior | −0.42 (−0.34) | −0.64 (−0.46) | −0.79 (−0.57) |
| Relative alpha, global | −0.45 (−0.35) | −0.62 (−0.45) | −0.78 (−0.55) |
| Peak alpha frequency, posterior | −0.60 (−0.47) | −0.78 (−0.60) | −0.58 (−0.37) |
| Peak alpha frequency, global | −0.56 (−0.46) | −0.73 (−0.62) | −0.62 (−0.42) |
| Aperiodic exponent, global | 0.37 (0.21) | 0.76 (0.52) | 0.75 (0.53) |

All 27 correlations are significant after Benjamini–Hochberg FDR (largest adjusted p = 0.002). The original classifier gives the same picture (27 of 27; ρ up to 0.89).

## Interpretation (exploratory)
- **Every marker moves in the expected direction in every cohort.** A higher AD score goes with more theta, a higher theta/alpha ratio, less alpha and a slower alpha peak. A higher score also goes with a steeper aperiodic exponent, for which there was no prior.
- **The score tracks these markers more closely than diagnosis does.** In ds004504 the theta/alpha ratio correlates 0.90 with the score but only 0.65 with diagnosis. So the classifier is not just inheriting the marker–diagnosis link: its output behaves like a continuous EEG-slowing index.
- This is plausibility, not mechanism (T11.6). Together with EXP-050 and EXP-012, it says that what LaBraM transfers across cohorts is largely the classical slowing signature of AD, read through a frozen pretrained network.
- Correlations are weakest in ADFSU (8 s per person, pre-cleaned, 128 Hz), where markers estimated from 8 s of EEG are noisier.

## Addendum, pre-registered before running (14 November 2026, D-039): within-group correlations
The review noted that "the score tracks the marker more closely than diagnosis does" compares a
continuous score with a binary label, which is expected, and that ρ = 0.91 is the best cohort
(ADFSU is 0.51). The stricter test is whether the score tracks the markers *within* a diagnostic
group, where diagnosis cannot drive the correlation. **Added analysis:** Spearman ρ between the score
and each marker within AD participants and within HC participants of each held-out cohort (9
markers × 3 cohorts × 2 groups = 54 per classifier), BH-FDR per classifier over the 54. Small groups
(ADFSU 12 HC, APAVA 11 HC) are reported with their n. **Reading (fixed now):** the score behaves as a
slowing index beyond diagnosis if, for the theta/alpha ratio (posterior), the within-AD and within-HC
correlations are positive in all three cohorts; otherwise the report says that the marker
correlations are explained by diagnosis. Output: `results/tables/T11_markers_within_group.csv`.

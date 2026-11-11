# EXP-042 – Sensitivity: ADFSU AD subsampled

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does ADFSU's diagnostic imbalance (76 AD / 12 HC) drive the primary result?
- **Method (T9.3, D-033):** 100 draws with seeds 1–100. In each draw, 12 of the 76 ADFSU AD participants are kept at random (matching the 12 HC) and the rest are dropped from training and testing. Original vs centring (i) LOCO is refitted on the 112 remaining participants. Per-draw point estimates only, with no per-draw bootstrap.
- **Outcome:** distribution of mean ΔAUROC over draws: median, 2.5–97.5 percentiles and the share of draws with Δ < 0. This is a distribution, not a test (D-028 item 8).
- **Output:** also `results/tables/T09_adfsu_subsample_draws.csv`.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

## Run record
- **Date:** 2026-11-11 · after tag `analysis-plan-v1`; design committed in 3e07a74 before the run
- **Command:** `python scripts/09_sensitivity.py` (20 parallel workers). The first attempt stopped before any sensitivity result because the participant ID column was not loaded. It was fixed and re-run in full; the primary numbers were identical.
- **Output:** `results/tables/T09_primary_and_sensitivity.csv`; per-draw values `results/tables/T09_adfsu_subsample_draws.csv`

## Results
100 draws, each with 12 ADFSU AD + 12 ADFSU HC + all of ds004504 and APAVA (112 participants).

| Quantity over draws | Median | 2.5–97.5 percentile | Min–max |
|---|---|---|---|
| Original mean LOCO AUROC | 0.878 | – | 0.826–0.927 |
| Centred mean LOCO AUROC | 0.895 | – | 0.802–0.944 |
| Mean ΔAUROC | −0.017 | [−0.063, 0.031] | −0.079 to 0.041 |
| Share of draws with ΔAUROC < 0 | 0.80 | | |

## Interpretation
- With ADFSU balanced, centring still tends to improve transfer (80% of draws), but by half as much as in the primary analysis, and the middle 95% of draws spans 0.
- ADFSU's imbalance therefore accounts for part of the primary improvement. It does not reverse it: no draw configuration makes control clearly harmful.
- These percentiles describe variation over subsamples, not sampling uncertainty, as planned (D-028 item 8).

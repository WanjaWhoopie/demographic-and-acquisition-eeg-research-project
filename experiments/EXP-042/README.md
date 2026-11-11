# EXP-042 – Sensitivity: ADFSU AD subsampled

## Before running (committed before results were seen, after tag analysis-plan-v1)
- **Objective:** O4 · **Question:** Does ADFSU's diagnostic imbalance (76 AD / 12 HC) drive the primary result?
- **Method (T9.3, D-033):** 100 draws with seeds 1–100. In each draw, 12 of the 76 ADFSU AD participants are kept at random (matching the 12 HC) and the rest are dropped from training and testing. Original vs centring (i) LOCO is refitted on the 112 remaining participants. Per-draw point estimates only, with no per-draw bootstrap.
- **Outcome:** distribution of mean ΔAUROC over draws: median, 2.5–97.5 percentiles and the share of draws with Δ < 0. This is a distribution, not a test (D-028 item 8).
- **Output:** also `results/tables/T09_adfsu_subsample_draws.csv`.
- **Script:** `scripts/09_sensitivity.py` → `results/tables/T09_primary_and_sensitivity.csv`

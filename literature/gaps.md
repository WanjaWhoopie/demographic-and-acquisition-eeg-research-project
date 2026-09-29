# Gap synthesis

Update this whenever a paper changes the picture. Each gap names the papers that establish
it and the objective that addresses it.

| # | Gap | Evidence so far | Addressed by |
|---|---|---|---|
| G1 | AD-EEG ML reports *how well* a model classifies, rarely *what information* it uses | Miltiadous2026ahepa (accuracy-centred benchmark); Ehteshamzad2024review | O2, O3 |
| G2 | Leakage work focuses on **subject identity**; **demographic** (age, sex) and **cohort/acquisition** shortcuts are rarely quantified | Brookshire2024leakage; Ugail2026subjectidentity; Lin2026identitytrap | O2 |
| G3 | Frozen EEG foundation-model audits exist but are **within-cohort**; none test whether erasing nuisance information changes **cross-cohort** AD performance | Lin2026identitytrap; Tang2026whatcapture | O3, O4 |
| G4 | External / cross-configuration validation is rare in dementia ML | Miltiadous2026ahepa ("lack of cross-configuration generalization"); Martin2023interpretable (to verify) | O4 |
| G5 | "Decodable" is often read as "used"; few studies test necessity by removal | Tang2026whatcapture (encoded vs representation-causal); Lin2026identitytrap | O3 |
| G6 | Residual FM signal is rarely linked back to known AD EEG markers (theta increase, alpha decrease, slowed PAF, aperiodic change) | Gebregergis2026reliability (theta ranks first for AD) | O5 |

## One-sentence positioning
Prior work shows that EEG models exploit subject identity within a cohort; we test whether a
frozen EEG foundation model's AD signal survives removal of demographic and cohort
information and still transfers to unseen cohorts.

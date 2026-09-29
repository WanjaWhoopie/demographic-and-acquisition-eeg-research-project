# Lin2026identitytrap – The Identity Trap in EEG Foundation Models: A Diagnostic Audit

**Citation:** Lin, J.-Y., Wu, Y. C., Jung, T.-P., et al. (2026). arXiv:2606.06647
**Link:** https://doi.org/10.48550/arXiv.2606.06647
**Read by / date:** abstract + excerpts only – full read pending

## Question they ask
Does high subject-disjoint accuracy of EEG foundation models on clinical resting-state EEG
reflect a clinical marker or subject-identity features correlated with the label, and can this
be diagnosed from frozen representations before fine-tuning?

## Data
- Four public resting-state datasets (mental arithmetic, sleep deprivation, AD/FTD, trait stress),
  N ≤ 65 each, 19–30 channels, resampled to 200 Hz, 1–45 Hz.

## Method (precise terms)
- Models: LaBraM, CBraMod, REVE (frozen and fine-tuned).
- FMScope protocol: variance decomposition of frozen embeddings (subject vs label share,
  against a random-Gaussian null); subject-axis erasure with LEACE; aperiodic 1/f ablation;
  layer-wise label probing; within-subject direction consistency.
- Design: a priori 2 × 2 layout – label varies within vs between subjects × consensus
  cross-subject EEG marker exists or not.

## Claims and the evidence for each
| Claim | Evidence | Convincing? |
|---|---|---|
| Subject identity dominates frozen FM variance | subject fraction 13–89× null in 12/12 model–dataset pairs; rises with fine-tuning | check in full text |
| The identity axis is linearly removable and removing it helps within-subject labels | +6 to +12 pp in primary cells | |
| Aperiodic 1/f carries identity in LaBraM/CBraMod but not REVE | subject probe drops 9–19 pp after 1/f removal | ablation is input-level, not causal (their caveat) |

## Techniques worth reusing
- Variance decomposition against a random-representation null → apply to **cohort** instead of subject (O2).
- LEACE erasure followed by re-probing → our O3 verification step.
- 1/f ablation → O5: is cohort identity carried by aperiodic slope?

## Gap relative to our project
Within-cohort, subject identity only. Does not test demographics, cohort/acquisition identity or
cross-cohort AD transfer after erasure.

## How we use it
§2.4 motivation; O2/O3 method template.

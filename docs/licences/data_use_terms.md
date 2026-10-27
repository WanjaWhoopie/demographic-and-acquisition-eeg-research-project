# Data-use terms (WORKPLAN T0.1)

Checked 2026-10-27. All four sources are public and de-identified. None of them is
redistributed from this repository: `data/` is git-ignored and only aggregate tables are committed.

| Dataset | Where obtained | Licence | Redistribution | Citations required | Other terms |
|---|---|---|---|---|---|
| ds004504 | OpenNeuro, snapshot 1.0.9 | **CC0 1.0** (`dataset_description.json`) | allowed under CC0, but we do not | Miltiadous et al. (2023), *Data* 8(6):95; dataset DOI 10.18112/openneuro.ds004504.v1.0.9 (listed in `ReferencesAndLinks`) | none |
| ADFSU | OSF project 2v5md (Vicchietti et al.) | **none stated** on the OSF project | assume not allowed | Vicchietti et al. (2023), *Sci Rep* 13:8184; original recordings: Pritchard, Duke & Coburn (1991) | the paper states the data were "made freely available"; OSF project is public |
| ADSZ | figshare 19091771 | **CC0 1.0** (figshare record) | allowed under CC0, but we do not | Alves et al. (arXiv:2110.06140); Pineda et al. (2020), *PLoS ONE* 15(6):e0231169 | not used as a cohort (D-017); kept only as the overlap record |
| APAVA | Google Drive copy shared with the team; identical signals on OSF jbysn (Smith, 2017) | **none stated** on either copy | assume not allowed | Escudero et al. (2006), *Physiol Meas* 27(11):1091–1106 (to verify); Smith (2017) OSF project if the OSF copy is referenced | provenance of the Google Drive copy (who prepared `APAVA.zip`) should be recorded: ask the person who shared the link |

## Actions
- [ ] Record who prepared the APAVA Google Drive copy and under what terms (T2.4).
- [ ] Add `Escudero2006apava` and `Pritchard1991fsu` full references to the literature matrix once verified (both are present as `secondary`).
- All other required citations are already in `literature/review_matrix.csv`.

## Re-identification
No attempt will be made to identify participants. Participant IDs used in this project are the
dataset's own anonymous codes (`sub-NNN`, `PacienteN`, `01–23`).

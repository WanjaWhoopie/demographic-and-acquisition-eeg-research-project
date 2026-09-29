# Literature review

Two layers:

1. **`review_matrix.csv`** – one row per paper, the table we sort and filter. Open it in
   Excel/Sheets; keep it UTF-8 and comma-separated.
2. **`notes/<id>.md`** – one file per paper that is read in full, using `notes/_template.md`.

`gaps.md` synthesises the gaps across papers and says which ones this project addresses.
`to_verify.md` lists claims we currently make that still need a primary source.

## Columns in `review_matrix.csv`
| Column | What to write |
|---|---|
| `id` | `FirstAuthorYEARkeyword`, e.g. `Brookshire2024leakage` (also the notes filename) |
| `citation` | APA short form |
| `doi_or_url` | DOI link preferred |
| `type` | empirical · benchmark · review · method · dataset · guideline |
| `datasets` | datasets used, with n |
| `models` | models / feature sets |
| `validation` | exact scheme: epoch-level k-fold, subject-level k-fold, LOSO, held-out cohort, … |
| `main_claim` | one sentence, what they say they showed |
| `key_numbers` | the numbers that support it |
| `methods_terms` | the *cool things they did*, in precise terms (e.g. "least-squares concept erasure", "variance decomposition of frozen embeddings", "subject-based vs segment-based holdout") |
| `limitations` | what weakens the claim |
| `gap_for_us` | what they did **not** do that we do |
| `objectives` | which of O1–O5 it informs |
| `used_in` | proposal / write-up section where it is cited |
| `status` | to-read · skimmed · read · noted |
| `source_check` | `primary` (we read the paper) or `secondary` (only seen quoted elsewhere) |

## Rules
- Never cite a paper whose `source_check` is `secondary` for a specific number.
- Check for retraction / withdrawal before citing (e.g. on the publisher page or scite).
- Add the paper to the matrix the day you find it, even if `status = to-read`.

# Working conventions

## Branches
- `main` always runs. Work on `feature/<task-id>-<short-name>`, e.g. `feature/T3-overlap-check`.
- Merge through a pull request reviewed by the other team member. Run `pytest` before asking for review.

## Commit messages
- Subject line: imperative, ≤ 72 characters, says *what changed*:
  `Add ADSZ–ADFSU PSD fingerprint check`, not `updates` or `fixed stuff`.
- Optional body after a blank line: *why*, and the task or experiment ID (`T3.4`, `EXP-002`).
- No names, initials or author credits in messages – git already records who committed.
- One logical change per commit (code + its config + its test together).

## Adding a paper
1. Add a row to `literature/review_matrix.csv` the day you find it (`status=to-read`).
2. When read, fill every column; write `methods_terms` in precise technical language.
3. Central papers get a note from `literature/notes/_template.md`.
4. If it changes a gap, update `literature/gaps.md`.

## Running an experiment
1. Pick the ID in `experiments/registry.csv` (or add one).
2. Copy `experiments/_template/` to `experiments/EXP-xxx/`, fill the *before running* half, commit.
3. Run from a clean commit; outputs to `results/runs/EXP-xxx/`.
4. Fill results + interpretation; update the registry row (status, commit, one-line result).

## Changing a prespecified choice
Add a row to `docs/decision_log.md` first (what, why, before/after seeing results), then change
the config in the same commit.

## Data
Never commit data, embeddings or participant-level tables. Only aggregate tables go into
`results/tables/`.

"""Independent re-check of the ADSZ–ADFSU duplication before it is reported as a finding (EXP-002).

    python scripts/02_overlap_recheck.py

EXP-002 found the overlap with hashed, rounded channel vectors and an offset scan
(eegconf.overlap). This script shares none of that code: it reads the raw text files with numpy
only and compares every ADSZ file against every ADFSU recording of the same diagnosis and
condition by direct float equality of all 19 channels over the first 1024 samples (8 s at 128 Hz;
ADFSU holds 1024 samples per recording, ADSZ files are 1024 samples or longer). The ADSZ column
order is taken from EXP-002 (F1 F2 F7 F3 Fz F4 F8 T3 C3 Cz C4 T4 T5 P3 Pz P4 T6 O1 O2, where
F1/F2 are ADFSU's duplicate Fp1/Fp2). A match is declared only when every channel is equal to
within 5e-6 at every sample (ADFSU values have six decimals, ADSZ five, so ADSZ is ADFSU rounded), and the number of ADFSU recordings that match each ADSZ file is
counted, so a file matching two recordings, or none, would show. A second, order-free test then
asks whether every ADSZ column equals *some* channel of the recording (the same 19 channels in a
different order; Healthy/Eyes_closed/Paciente6 is stored that way).

Output: results/tables/T02_overlap_recheck.csv (one row per ADSZ file: n_adfsu_matches, the match,
max |difference| at the match, and whether it agrees with the EXP-002 mapping) and a summary.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ADSZ_COLS = ["F1", "F2", "F7", "F3", "Fz", "F4", "F8", "T3", "C3", "Cz", "C4", "T4", "T5", "P3", "Pz", "P4", "T6", "O1", "O2"]
N = 1024
TOL = 5e-6          # ADFSU files carry six decimals, ADSZ five: half a unit of the fifth decimal


def adfsu_recordings():
    """{(group, condition, 'PacienteN'): (19, 1024) array in ADSZ_COLS order}."""
    out = {}
    base = ROOT / "data/raw/ADFSU/EEG_data"
    for group in ("AD", "Healthy"):
        for cond in ("Eyes_closed", "Eyes_open"):
            for folder in sorted((base / group / cond).glob("Paciente*")):
                files = {f.stem: f for f in folder.glob("*.txt")}
                if not files:
                    continue                                         # Healthy/Eyes_open/Paciente5 is empty
                # Healthy/Eyes_closed/Paciente6 ships without the F1/F2 copies; F1 ≡ Fp1, F2 ≡ Fp2 (EXP-002)
                files.setdefault("F1", files.get("Fp1"))
                files.setdefault("F2", files.get("Fp2"))
                assert set(ADSZ_COLS) <= set(files), f"{folder}: missing channels"
                out[(group, cond, folder.name)] = np.vstack([np.loadtxt(files[c])[:N] for c in ADSZ_COLS])
    return out


def adsz_files():
    """Yield (group, condition, file name, (19, n_samples) array)."""
    base = ROOT / "data/raw/ADSZ/dataset/alzheimer"
    for group in ("AD", "Healthy"):
        for f in sorted((base / group).glob("*.out")):
            cond = re.match(r"e([co])\d{4}$|eeg\d+([co])1$", f.stem)
            c = (cond.group(1) or cond.group(2))
            yield group, "Eyes_closed" if c == "c" else "Eyes_open", f.name, np.loadtxt(f).T


def main():
    ref = adfsu_recordings()
    prior = pd.read_csv(ROOT / "data/metadata/overlap_adsz_adfsu.csv")       # EXP-002 mapping, local
    prior = dict(zip(prior.adsz_file, prior.adfsu_recording))
    rows = []
    for group, cond, name, X in adsz_files():
        assert X.shape[0] == 19 and X.shape[1] >= N, f"{name}: shape {X.shape}"
        hits, perm_hits = [], []
        for (g, c, pac), R in ref.items():
            if (g, c) != (group, cond):
                continue
            d = np.abs(X[:, :N] - R).max()
            if d <= TOL:
                hits.append((pac, d))
            else:
                # order-free: each ADSZ column must equal one channel of R, every channel used once
                pairs = [(i, j) for i in range(19) for j in range(19) if np.abs(X[i, :N] - R[j]).max() <= TOL]
                if len(pairs) == 19 and len({i for i, _ in pairs}) == 19 and len({j for _, j in pairs}) == 19:
                    perm_hits.append(pac)
        exp002 = prior.get(f"{group}/{name}")
        got = f"{group}/{cond}/{hits[0][0]}" if hits else (f"{group}/{cond}/{perm_hits[0]}" if perm_hits else None)
        rows.append({"adsz_file": f"{group}/{name}", "condition": cond, "n_samples": X.shape[1],
                     "n_adfsu_matches": len(hits), "n_matches_up_to_channel_order": len(perm_hits), "adfsu_match": got,
                     "max_abs_diff": hits[0][1] if hits else np.nan,
                     "agrees_with_EXP002": (got == exp002) if (got or isinstance(exp002, str)) else True})
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "results/tables/T02_overlap_recheck.csv", index=False)
    n1, nmulti = (df.n_adfsu_matches == 1).sum(), (df.n_adfsu_matches > 1).sum()
    nperm = ((df.n_adfsu_matches == 0) & (df.n_matches_up_to_channel_order == 1)).sum()
    n0 = ((df.n_adfsu_matches == 0) & (df.n_matches_up_to_channel_order == 0)).sum()
    print(df.to_string(index=False))
    print(f"\n{len(df)} ADSZ files: {n1} match exactly one ADFSU recording in the standard channel order, "
          f"{nperm} match one recording up to channel order, {n0} match none, {nmulti} match several")
    print(f"largest |difference| over matched files: {df.max_abs_diff.max():.2e}")
    print(f"agrees with the EXP-002 mapping in every file: {df.agrees_with_EXP002.all()}")
    print(f"unmatched: {df[(df.n_adfsu_matches == 0) & (df.n_matches_up_to_channel_order == 0)].adsz_file.tolist()}")
    m = df[df.adfsu_match.notna()]
    print(f"distinct ADFSU recordings matched: {m.adfsu_match.nunique()} "
          f"({m.adfsu_match.str.rsplit('/', n=1).str[1].nunique()} distinct Paciente folders across conditions)")


if __name__ == "__main__":
    main()

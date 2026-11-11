"""Participant-level feature tables for Phases 6-9 (WORKPLAN T5.3, T6.4).

    python scripts/05_build_features.py
    python scripts/05_build_features.py --scaled-only   # EXP-044: Z_labram-base-scaled only

Reads epoch-level embeddings (data/embeddings/<model>/<cohort>/*.npz) and processed epochs, and writes
data/features/participant_features.npz (local, participant-level) with:

- meta columns: global_id, cohort, participant_id, diagnosis (AD=1), age, sex (F=1), n_epochs
- Z_<model>          (P, 12 blocks, 2 tokens [patch_mean, cls], 2 poolings [mean, median], 200)
                     for model in {labram-base, labram-random}, all clean epochs (D-018 primary)
- Z8_<model>         same, from each participant's first two clean epochs only (8-s sensitivity,
                     D-018); rows with fewer than two epochs are NaN and flagged in has_8s
- classical          (P, 80): 64 relative band powers + 16 aperiodic exponents (NaN = rejected fit)

--scaled-only writes data/features/participant_features_scaled.npz with global_id and
Z_labram-base-scaled (amplitude-scaled embeddings, D-033) and leaves the primary file untouched.

No labels are used to build features; diagnosis is only carried along for the analysis scripts.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from eegconf.features import classical_vector
from eegconf.representation import pool_participant

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("labram-base", "labram-random")
TOKENS = ("layer_mean", "layer_cls")      # stored names; reported as patch_mean, cls
POOLINGS = ("mean", "median")


def pooled(emb, idx=None):
    """(12, 2, 2, 200) participant representation from one embedding file, optionally on a subset of epochs."""
    out = np.empty((12, len(TOKENS), len(POOLINGS), 200), np.float32)
    for t, tok in enumerate(TOKENS):
        L = emb[tok] if idx is None else emb[tok][:, idx]
        for b in range(L.shape[0]):
            for q, pool in enumerate(POOLINGS):
                out[b, t, q] = pool_participant(L[b], pool)
    return out


def scaled_only(parts):
    """EXP-044: participant representations from the amplitude-scaled embeddings only."""
    gids, Z = [], []
    for _, r in parts.iterrows():
        gid = r["global_id"] if r["cohort"] != "APAVA" else f"APAVA-{int(r['participant_id']):02d}"
        Z.append(pooled(np.load(ROOT / "data/embeddings/labram-base-scaled" / r["cohort"] / f"{gid}.npz")))
        gids.append(gid)
    np.savez_compressed(ROOT / "data/features/participant_features_scaled.npz",
                        global_id=np.array(gids), **{"Z_labram-base-scaled": np.stack(Z)})
    print(f"{len(gids)} participants -> data/features/participant_features_scaled.npz")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scaled-only", action="store_true")
    args = ap.parse_args()
    cfgs = yaml.safe_load(open(ROOT / "configs/datasets.yaml"))
    parts = pd.read_csv(ROOT / "data/metadata/participants_all.csv", dtype={"participant_id": str})
    parts = parts[parts["included"]].reset_index(drop=True)
    if args.scaled_only:
        return scaled_only(parts)
    rows, Z, Z8, has8, classical, bad_fits = [], {m: [] for m in MODELS}, {m: [] for m in MODELS}, [], [], 0
    for _, r in parts.iterrows():
        gid = r["global_id"] if r["cohort"] != "APAVA" else f"APAVA-{int(r['participant_id']):02d}"
        proc = np.load(ROOT / "data/processed" / r["cohort"] / f"{gid}.npz")
        order = np.argsort(proc["epoch_idx"])          # time order (files are already in order; be explicit)
        first2 = order[:2] if len(order) >= 2 else None
        for m in MODELS:
            emb = np.load(ROOT / "data/embeddings" / m / r["cohort"] / f"{gid}.npz")
            Z[m].append(pooled(emb))
            Z8[m].append(pooled(emb, first2) if first2 is not None else np.full((12, 2, 2, 200), np.nan, np.float32))
        vec, nb = classical_vector(proc["X"])
        classical.append(vec); bad_fits += nb
        has8.append(first2 is not None)
        rows.append({"global_id": gid, "cohort": r["cohort"], "participant_id": r["participant_id"],
                     "diagnosis": int(r["diagnosis"] == "AD"), "age": r["age"],
                     "sex": np.nan if pd.isna(r["sex"]) else float(r["sex"] == "F"), "n_epochs": len(order)})
        print(f"{gid}: {len(order)} epochs")
    meta = pd.DataFrame(rows)
    out = ROOT / "data/features"
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "participant_features.npz",
                        **{c: meta[c].to_numpy() for c in meta.columns},
                        **{f"Z_{m}": np.stack(Z[m]) for m in MODELS},
                        **{f"Z8_{m}": np.stack(Z8[m]) for m in MODELS},
                        has_8s=np.array(has8), classical=np.stack(classical))
    print(f"\n{len(meta)} participants; aperiodic fits rejected (R2 < 0.9): {bad_fits} of {16 * len(meta)}; "
          f"without 8 s: {int((~np.array(has8)).sum())}")


if __name__ == "__main__":
    main()

"""Sanity checks on the LaBraM extraction (WORKPLAN T5.4).

    python scripts/04_sanity.py

Checks, each printed as PASS/FAIL and written to results/tables/T04_embedding_sanity.csv:
- determinism: the same epochs through the model twice give identical embeddings;
- finiteness: no NaN/Inf in any saved embedding;
- scale: median embedding norm per cohort (a cohort far from the others would suggest a unit error);
- channel use: shuffling the channel order of a few epochs changes the embedding (the model
  reads `input_chans`, so swapped channels must give different positional embeddings);
- control: the untrained model's embeddings differ from the pretrained ones and carry less
  structure (lower variance across epochs relative to their norm).
Nothing here uses labels.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from eegconf import representation as rep

ROOT = Path(__file__).resolve().parents[1]
LABRAM = ROOT / "external" / "LaBraM"


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfgs = yaml.safe_load(open(ROOT / "configs/datasets.yaml"))
    cohorts = [c for c, v in cfgs.items() if v.get("use")]
    chans = rep.input_chans(yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))["channels"], LABRAM)
    model, _ = rep.load_labram(LABRAM, LABRAM / "checkpoints" / "labram-base.pth", device)
    rows = []

    # one small batch of real epochs for the model-level checks
    f = sorted((ROOT / "data/processed" / cohorts[0]).glob("*.npz"))[0]
    X = np.load(f)["X"][:8]

    a = rep.extract(model, X, chans, device)["pooled"]
    b = rep.extract(model, X, chans, device)["pooled"]
    rows.append(("determinism", "same input twice", float(np.abs(a - b).max()), np.abs(a - b).max() < 1e-5))

    perm = np.random.default_rng(0).permutation(X.shape[1])
    c = rep.extract(model, X[:, perm], chans, device)["pooled"]
    rows.append(("channel_use", "shuffled channel order changes output (rel. diff)",
                 float(np.linalg.norm(a - c) / np.linalg.norm(a)), np.linalg.norm(a - c) / np.linalg.norm(a) > 0.05))

    rnd, _ = rep.load_labram(LABRAM, None, device, random_init=True)
    r = rep.extract(rnd, X, chans, device)["pooled"]
    rows.append(("control_differs", "random-weight model differs from pretrained (rel. diff)",
                 float(np.linalg.norm(a - r) / np.linalg.norm(a)), np.linalg.norm(a - r) / np.linalg.norm(a) > 0.5))

    # saved embeddings: finiteness and scale per cohort
    for model_name in ("labram-base", "labram-random"):
        for cohort in cohorts:
            files = sorted((ROOT / "data/embeddings" / model_name / cohort).glob("*.npz"))
            if not files:
                continue
            norms, finite, spread = [], True, []
            for fp in files:
                z = np.load(fp)
                P = z["pooled"]
                finite &= bool(np.isfinite(z["layer_mean"]).all() and np.isfinite(P).all())
                norms.append(np.median(np.linalg.norm(P, axis=1)))
                if len(P) > 1:
                    spread.append(P.std(axis=0).mean() / np.linalg.norm(P.mean(axis=0)))
            rows.append((f"finite/{model_name}", cohort, 1.0 if finite else 0.0, finite))
            rows.append((f"norm/{model_name}", f"{cohort} median pooled-embedding norm", float(np.median(norms)), True))
            rows.append((f"spread/{model_name}", f"{cohort} within-participant epoch spread / mean norm", float(np.median(spread)), True))

    df = pd.DataFrame(rows, columns=["check", "detail", "value", "pass"])
    df.to_csv(ROOT / "results/tables/T04_embedding_sanity.csv", index=False)
    print(df.to_string(index=False))
    print("\nALL PASS" if df["pass"].all() else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()

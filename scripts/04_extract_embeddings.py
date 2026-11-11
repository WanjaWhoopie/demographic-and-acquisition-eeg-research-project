"""Extract frozen LaBraM embeddings for every processed participant of a cohort (WORKPLAN T5.2).

    python scripts/04_extract_embeddings.py --cohort ds004504            # pretrained weights
    python scripts/04_extract_embeddings.py --cohort ds004504 --random   # untrained control (T5.4.4)
    python scripts/04_extract_embeddings.py --cohort ds004504 --amplitude-scaled   # D-019 sensitivity (EXP-044)

Reads data/processed/<cohort>/<global_id>.npz and writes
    data/embeddings/<model>/<cohort>/<global_id>.npz with
        layer_mean (12, n_epochs, 200), layer_cls (12, n_epochs, 200), pooled (n_epochs, 200),
        epoch_idx, segment_idx
where <model> is labram-base, labram-random or labram-base-scaled. Uses the GPU when one is available.

--amplitude-scaled (D-019, D-033): every participant's clean epochs are multiplied by
AMP_REF_UV / SD, where SD is the standard deviation over all of that participant's epochs, channels
and samples. All recordings then have the same overall amplitude (10 µV SD, inside LaBraM's
training range), so between-cohort amplitude differences can no longer reach the model.
No labels are read here, so this stage can run before the analysis-plan freeze.
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import yaml

from eegconf import representation as rep

ROOT = Path(__file__).resolve().parents[1]
LABRAM = ROOT / "external" / "LaBraM"
AMP_REF_UV = 10.0          # common per-recording SD for the amplitude-scaled sensitivity (D-033)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--random", action="store_true", help="untrained LaBraM (negative control)")
    ap.add_argument("--amplitude-scaled", action="store_true", help="per-recording variance scaling (D-019)")
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(20261001)
    assert not (args.random and args.amplitude_scaled), "the scaled sensitivity uses pretrained weights only"
    model_name = "labram-random" if args.random else ("labram-base-scaled" if args.amplitude_scaled else "labram-base")
    print(f"device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if device == "cuda" else ""))

    # Pin exactly which code and weights produced these embeddings.
    commit = subprocess.run(["git", "-C", str(LABRAM), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    model, report = rep.load_labram(LABRAM, LABRAM / "checkpoints" / "labram-base.pth", device, random_init=args.random)
    assert not report["missing"] and not report["unexpected"], report
    print(f"model: {model_name}, LaBraM commit {commit[:12]}, torch {torch.__version__}, "
          f"tensors loaded: {report.get('loaded', 0)}")

    pp_cfg = yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))
    chans = rep.input_chans(pp_cfg["channels"], LABRAM)
    print(f"input_chans: {chans}")

    src = ROOT / "data/processed" / args.cohort
    dst = ROOT / "data/embeddings" / model_name / args.cohort
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*.npz"))[: args.limit]
    t0, n_epochs = time.time(), 0
    for f in files:
        z = np.load(f)
        if not len(z["X"]):
            continue
        X = z["X"]
        if args.amplitude_scaled:
            X = X * (AMP_REF_UV / X.std())                 # one factor per participant (recording)
        out = rep.extract(model, X, chans, device, args.batch_size)
        np.savez_compressed(dst / f.name, **out, epoch_idx=z["epoch_idx"], segment_idx=z["segment_idx"])
        n_epochs += len(z["X"])
        print(f"{f.stem}: {len(z['X'])} epochs")
    elapsed = time.time() - t0
    meta = {"model": model_name, "labram_commit": commit, "torch": torch.__version__, "device": device,
            "checkpoint_sha256": "7c50583826afac76c4ab18f43d958df40496c8229accc09ed6a227c9bb57c37c",
            "input_chans": chans, "channels": pp_cfg["channels"], "scale": rep.SCALE,
            "amplitude_scaled_to_sd_uv": AMP_REF_UV if args.amplitude_scaled else None,
            "n_participants": len(files), "n_epochs": n_epochs, "seconds": round(elapsed, 1)}
    (dst / "_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\n{len(files)} participants, {n_epochs} epochs in {elapsed:.0f} s -> {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

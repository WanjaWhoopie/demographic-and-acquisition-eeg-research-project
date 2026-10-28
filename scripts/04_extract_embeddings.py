"""Extract frozen LaBraM embeddings for every processed participant of a cohort (WORKPLAN T5.2).

    python scripts/04_extract_embeddings.py --cohort ds004504            # pretrained weights
    python scripts/04_extract_embeddings.py --cohort ds004504 --random   # untrained control (T5.4.4)

Reads data/processed/<cohort>/<global_id>.npz and writes
    data/embeddings/<model>/<cohort>/<global_id>.npz with
        layer_mean (12, n_epochs, 200), layer_cls (12, n_epochs, 200), pooled (n_epochs, 200),
        epoch_idx, segment_idx
where <model> is labram-base or labram-random. Uses the GPU when one is available.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--random", action="store_true", help="untrained LaBraM (negative control)")
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(20261001)
    model_name = "labram-random" if args.random else "labram-base"
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
        out = rep.extract(model, z["X"], chans, device, args.batch_size)
        np.savez_compressed(dst / f.name, **out, epoch_idx=z["epoch_idx"], segment_idx=z["segment_idx"])
        n_epochs += len(z["X"])
        print(f"{f.stem}: {len(z['X'])} epochs")
    elapsed = time.time() - t0
    meta = {"model": model_name, "labram_commit": commit, "torch": torch.__version__, "device": device,
            "checkpoint_sha256": "7c50583826afac76c4ab18f43d958df40496c8229accc09ed6a227c9bb57c37c",
            "input_chans": chans, "channels": pp_cfg["channels"], "scale": rep.SCALE,
            "n_participants": len(files), "n_epochs": n_epochs, "seconds": round(elapsed, 1)}
    (dst / "_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\n{len(files)} participants, {n_epochs} epochs in {elapsed:.0f} s -> {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

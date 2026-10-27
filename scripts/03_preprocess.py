"""Harmonised preprocessing of one cohort (WORKPLAN Phase 4).

    python scripts/03_preprocess.py --cohort ds004504   # or ADFSU, APAVA

Reads raw data through eegconf.io, runs eegconf.preprocessing.preprocess_participant on every
included participant and writes:

- data/processed/<cohort>/<global_id>.npz   X (n_epochs, 16, 800) float32 µV at 200 Hz,
                                            epoch_idx, segment_idx, ch_names   (local)
- data/metadata/preproc_<cohort>.csv        per-participant epoch counts and rejection reasons (local)

Settings come from configs/preprocessing.yaml and are printed at the start so a run log shows
exactly what was applied. Nothing is fitted on the data here, so there is no train/test issue.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from eegconf.io import get_loader
from eegconf.preprocessing import preprocess_participant

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--limit", type=int, default=None, help="process only the first N participants (quick test)")
    args = ap.parse_args()

    pp_cfg = yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))
    ds_cfg = yaml.safe_load(open(ROOT / "configs/datasets.yaml"))[args.cohort]
    print("preprocessing config:", json.dumps({k: pp_cfg[k] for k in ("channels", "filter", "reference", "resample_hz", "epoch", "artefact_rejection")}))

    loader = get_loader(args.cohort)
    raw_root = ROOT / ds_cfg["raw_path"]
    participants = loader.load_participants(raw_root, ds_cfg)
    if args.limit:
        participants = participants.head(args.limit)
    dx = participants.set_index("participant_id")["diagnosis"]

    out_dir = ROOT / "data/processed" / args.cohort
    out_dir.mkdir(parents=True, exist_ok=True)

    # Segments arrive one participant at a time (loaders iterate in participant order), so we
    # collect a participant's segments until the ID changes, then process that participant.
    rows = []
    current, buffer = None, []

    def flush():
        if not buffer:
            return
        pid = buffer[0].participant_id
        epochs, info = preprocess_participant(buffer, pp_cfg)
        gid = f"{args.cohort}-{pid}"
        np.savez_compressed(out_dir / f"{gid}.npz", X=epochs, epoch_idx=info["epoch_idx"],
                            segment_idx=info["segment_idx"], ch_names=np.array(info["ch_names"]),
                            sfreq=pp_cfg["resample_hz"])
        rows.append({"cohort": args.cohort, "participant_id": pid, "global_id": gid, "diagnosis": dx[pid],
                     "n_segments": info["n_segments"], "epochs_before": info["epochs_before"],
                     "epochs_after": info["epochs_after"], "rejected_ptp_max": info["rejected_ptp_max"],
                     "rejected_flat": info["rejected_flat"]})
        print(f"{gid}: {info['epochs_after']}/{info['epochs_before']} epochs kept "
              f"(ptp>{pp_cfg['artefact_rejection']['peak_to_peak_uv']}: {info['rejected_ptp_max']}, flat: {info['rejected_flat']})")

    for seg in loader.iter_segments(raw_root, participants, ds_cfg):
        if seg.participant_id != current:
            flush()
            current, buffer = seg.participant_id, []
        buffer.append(seg)
    flush()

    df = pd.DataFrame(rows)
    meta = ROOT / "data/metadata"
    meta.mkdir(exist_ok=True)
    df.to_csv(meta / f"preproc_{args.cohort}.csv", index=False)
    tot_b, tot_a = df["epochs_before"].sum(), df["epochs_after"].sum()
    print(f"\n{len(df)} participants; {tot_a}/{tot_b} epochs kept ({100 * (tot_b - tot_a) / max(tot_b, 1):.1f}% rejected); "
          f"participants with 0 epochs: {int((df['epochs_after'] == 0).sum())}; with < 2: {int((df['epochs_after'] < 2).sum())}")


if __name__ == "__main__":
    main()

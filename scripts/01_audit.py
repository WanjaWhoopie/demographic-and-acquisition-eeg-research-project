"""Raw-data audit for one cohort (WORKPLAN Phase 2, checks A1-A12; EXP-001).

    python scripts/01_audit.py --cohort ds004504

Outputs
- data/metadata/audit_<cohort>.csv          one row per recording (participant-level: stays local)
- data/metadata/duplicates_<cohort>.csv     near-duplicate recording pairs (A12)
- data/metadata/psd_<cohort>.npz            Welch PSD per recording, for later plots / overlap checks
- results/tables/T00_audit_<cohort>_summary.csv   aggregate counts only (safe to commit)
- results/figures/EXP-001_<cohort>_psd.png        mean log-PSD by diagnosis (safe to commit)
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from eegconf import audit
from eegconf.io import get_loader

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--limit", type=int, default=None, help="audit only the first N participants (quick test)")
    args = ap.parse_args()

    ds_cfg = yaml.safe_load(open(ROOT / "configs/datasets.yaml"))[args.cohort]
    target = yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))["channels"]
    raw_root = ROOT / ds_cfg["raw_path"]
    loader = get_loader(args.cohort)

    participants = loader.load_participants(raw_root)
    if args.limit:
        participants = participants.head(args.limit)
    meta = participants.set_index("participant_id")

    rows, fps, ids, psds, freqs_ref, first_order = [], [], [], [], None, None
    for rec in loader.iter_recordings(raw_root, participants):
        row = {"cohort": rec.cohort, "participant_id": rec.participant_id,
               "diagnosis": meta.loc[rec.participant_id, "diagnosis"], "file": rec.path.name}
        if rec.raw is None:
            row["flags"] = "A1_missing_file"
            rows.append(row)
            continue
        raw = rec.raw
        data = raw.get_data(picks="eeg") * 1e6  # MNE stores volts
        ch = [raw.ch_names[i] for i in mne_eeg_picks(raw)]
        first_order = first_order or ch
        sc = rec.sidecar
        row.update({
            "sfreq": float(raw.info["sfreq"]),
            "duration_s": raw.n_times / raw.info["sfreq"],
            "condition": sc.get("TaskName", ""),
            "reference": sc.get("EEGReference", ""),
            "online_filter": str(sc.get("SoftwareFilters", "")),
            "line_freq": sc.get("PowerLineFrequency", np.nan),
            "channel_order_matches_first": ch == first_order,
            **audit.channel_check(ch, target),
            **audit.amplitude_checks(data, raw.info["sfreq"]),
        })
        f, p = audit.psd(data, raw.info["sfreq"])
        row.update(audit.spectral_checks(f, p, line_freq=float(sc.get("PowerLineFrequency", 50))))
        row["flags"] = audit.flags(row, ds_cfg.get("sfreq_expected"),
                                   str(ds_cfg.get("condition", "")).replace("_", "") if isinstance(ds_cfg.get("condition"), str) else None)
        rows.append(row)

        sel = f <= 60
        freqs_ref = f[sel] if freqs_ref is None else freqs_ref
        if len(f[sel]) == len(freqs_ref):
            psds.append(p[:, sel])
            fps.append(audit.fingerprint(f, p))
            ids.append(rec.participant_id)
        print(f"{rec.participant_id}: {row['duration_s']:.0f}s  sd={row['robust_sd_uv_median']:.1f}uV  flags={row['flags'] or '-'}")

    df = pd.DataFrame(rows)
    meta_dir = ROOT / "data/metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(meta_dir / f"audit_{args.cohort}.csv", index=False)

    dups = audit.near_duplicates(fps, ids) if len(fps) > 1 else []
    pd.DataFrame(dups, columns=["id_a", "id_b", "r"]).to_csv(meta_dir / f"duplicates_{args.cohort}.csv", index=False)
    np.savez_compressed(meta_dir / f"psd_{args.cohort}.npz", freqs=freqs_ref, psd=np.array(psds), participant_id=np.array(ids))

    write_summary(df, dups, args.cohort)
    plot_psd(freqs_ref, np.array(psds), ids, meta, args.cohort)
    print(f"\n{len(df)} recordings audited; {int((df['flags'].fillna('') != '').sum())} flagged; {len(dups)} possible duplicate pairs")


def mne_eeg_picks(raw):
    import mne
    return mne.pick_types(raw.info, eeg=True)


def write_summary(df, dups, cohort):
    d = df.copy()
    summary = {
        "cohort": cohort,
        "n_recordings": len(d),
        "n_AD": int((d["diagnosis"] == "AD").sum()),
        "n_HC": int((d["diagnosis"] == "HC").sum()),
        "sfreq_values": " ".join(sorted({f"{v:g}" for v in d["sfreq"].dropna()})),
        "n_channels_values": " ".join(sorted({str(int(v)) for v in d["n_channels"].dropna()})),
        "all_channel_orders_match": bool(d["channel_order_matches_first"].all()),
        "recordings_missing_target_channels": int((d["n_missing_target"] > 0).sum()),
        "reference_values": "; ".join(sorted(set(d["reference"].astype(str)))),
        "condition_values": "; ".join(sorted(set(d["condition"].astype(str)))),
        "duration_s_min": d["duration_s"].min(),
        "duration_s_median": d["duration_s"].median(),
        "duration_s_max": d["duration_s"].max(),
        "raw_robust_sd_uv_median": d["raw_robust_sd_uv_median"].median(),
        "bandpassed_1_30Hz_robust_sd_uv_median": d["robust_sd_uv_median"].median(),
        "recordings_units_implausible": int((~d["units_plausible"].astype(bool)).sum()),
        "recordings_with_flat_channels": int((d["n_flat_channels"] > 0).sum()),
        "recordings_with_clipping": int((d["n_clipped_channels"] > 0).sum()),
        "recordings_with_nan_inf": int(((d["n_nan"] + d["n_inf"]) > 0).sum()),
        "recordings_extreme_amplitude": int(d["flags"].fillna("").str.contains("A10_extreme").sum()),
        "line_noise_db_median": d["line_noise_db"].median(),
        "hf_rolloff_db_median": d["hf_rolloff_db"].median(),
        "possible_duplicate_pairs": len(dups),
        "recordings_flagged": int((d["flags"].fillna("") != "").sum()),
    }
    out = ROOT / "results/tables" / f"T00_audit_{cohort}_summary.csv"
    pd.DataFrame([summary]).T.rename(columns={0: "value"}).to_csv(out)
    print(f"summary -> {out.relative_to(ROOT)}")


def plot_psd(freqs, psds, ids, meta, cohort):
    if not len(psds):
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    logp = 10 * np.log10(psds.mean(axis=1))  # mean over channels, dB
    diag = meta.loc[ids, "diagnosis"].to_numpy()
    for g, color in [("AD", "#c0392b"), ("HC", "#2471a3")]:
        m = logp[diag == g]
        if len(m):
            mu, sd = m.mean(axis=0), m.std(axis=0)
            ax.plot(freqs, mu, color=color, label=f"{g} (n={len(m)})")
            ax.fill_between(freqs, mu - sd, mu + sd, color=color, alpha=0.15)
    ax.set(xlabel="Frequency (Hz)", ylabel="Power (dB re 1 µV²/Hz)", xlim=(0, 60),
           title=f"{cohort}: raw PSD, mean over channels (±1 SD across participants)")
    ax.axvspan(0.5, 30, color="grey", alpha=0.07, label="analysis band 0.5–30 Hz")
    ax.legend()
    fig.tight_layout()
    out = ROOT / "results/figures" / f"EXP-001_{cohort}_psd.png"
    fig.savefig(out, dpi=150)
    print(f"figure -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

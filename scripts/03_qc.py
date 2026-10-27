"""Preprocessing QC across cohorts (WORKPLAN T4.9, EXP-003).

    python scripts/03_qc.py

Reads data/processed/<cohort>/*.npz and data/metadata/preproc_<cohort>.csv for every cohort in
use and writes aggregate outputs only (safe to commit):

- results/tables/T03_preprocessing_qc.csv      participants, epochs kept/rejected, amplitude per cohort x diagnosis
- results/tables/T03_cohort_probe_classical.csv how well cohort identity is decoded from classical
                                                spectral features AFTER preprocessing (reference
                                                value for the LaBraM cohort probe, O2)
- results/figures/EXP-003_psd_processed.png     mean PSD per cohort x diagnosis on processed epochs
- results/figures/EXP-003_snippets.png          4-s traces of two random participants per cohort (visual check)

The cohort probe uses participant-grouped, stratified 5-fold CV (eegconf.evaluation.splits), so
its balanced accuracy is a fair estimate; chance is 1/3 for three cohorts.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.signal import welch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from eegconf.audit import robust_sd
from eegconf.evaluation import splits

ROOT = Path(__file__).resolve().parents[1]
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}
SFREQ = 200.0


def load_cohort(cohort):
    """Yield (global_id, X) for every processed participant with at least one epoch."""
    for f in sorted((ROOT / "data/processed" / cohort).glob("*.npz")):
        z = np.load(f)
        if len(z["X"]):
            yield f.stem, z["X"]


def participant_psd(X):
    """Mean Welch PSD over a participant's epochs: (n_channels, n_freqs), 0.5-Hz bins."""
    f, p = welch(X, fs=SFREQ, window="hann", nperseg=400, noverlap=200, axis=2)
    return f, p.mean(axis=0)


def relative_band_power(f, p):
    """Per-channel relative power in four bands (fraction of 1-30 Hz power) -> 64 features,
    plus log total 1-30 Hz power per channel (16 features) kept separately as 'amplitude'."""
    tot = p[:, (f >= 1) & (f < 30)].sum(axis=1)
    rel = np.concatenate([p[:, (f >= lo) & (f < hi)].sum(axis=1) / tot for lo, hi in BANDS.values()])
    return rel, np.log10(tot)


def main():
    cfgs = yaml.safe_load(open(ROOT / "configs/datasets.yaml"))
    cohorts = [c for c, v in cfgs.items() if v.get("use")]
    pre = pd.concat([pd.read_csv(ROOT / "data/metadata" / f"preproc_{c}.csv") for c in cohorts], ignore_index=True)

    # ---- per-participant spectra, amplitude and classical features
    rows, feats, amps, meta = [], [], [], []
    psd_store = {}
    for c in cohorts:
        dx = pre.set_index("global_id")["diagnosis"]
        for gid, X in load_cohort(c):
            f, p = participant_psd(X)
            rel, amp = relative_band_power(f, p)
            feats.append(rel); amps.append(amp)
            meta.append({"cohort": c, "participant_id": gid, "diagnosis": dx[gid]})
            psd_store[gid] = p.mean(axis=0)              # mean over channels for the figure
            rows.append({"global_id": gid, "robust_sd_uv": float(np.median(robust_sd(X.transpose(1, 0, 2).reshape(16, -1))))})
    amp_df = pd.DataFrame(rows)
    meta = pd.DataFrame(meta)
    F = np.array(feats); A = np.array(amps)

    # ---- T03 QC table: counts, rejection, amplitude per cohort x diagnosis
    q = pre.merge(amp_df, on="global_id")
    qc = q.groupby(["cohort", "diagnosis"]).agg(
        participants=("global_id", "count"),
        epochs_before=("epochs_before", "sum"), epochs_after=("epochs_after", "sum"),
        rejected_ptp=("rejected_ptp_max", "sum"), rejected_flat=("rejected_flat", "sum"),
        epochs_per_participant_min=("epochs_after", "min"), epochs_per_participant_median=("epochs_after", "median"),
        epochs_per_participant_max=("epochs_after", "max"),
        robust_sd_uv_median=("robust_sd_uv", "median"),
    ).reset_index()
    qc["pct_rejected"] = (100 * (qc["epochs_before"] - qc["epochs_after"]) / qc["epochs_before"]).round(1)
    qc["robust_sd_uv_median"] = qc["robust_sd_uv_median"].round(2)
    qc.to_csv(ROOT / "results/tables/T03_preprocessing_qc.csv", index=False)
    print(qc.to_string(index=False))

    # ---- cohort probe on classical features (participant-grouped stratified CV)
    strat = meta.assign(diagnosis=meta["cohort"] + "/" + meta["diagnosis"])   # stratify on cohort x dx
    y = meta["cohort"].to_numpy()
    out = []
    for name, Xf in [("relative band power (shape only)", F), ("+ log total power (amplitude)", np.hstack([F, A]))]:
        accs = []
        for rep, fold, tr, te in splits.participant_kfold(strat, n_splits=5, n_repeats=5, seed=20261001):
            clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced"))
            clf.fit(Xf[tr], y[tr])
            accs.append(balanced_accuracy_score(y[te], clf.predict(Xf[te])))
        out.append({"features": name, "n_features": Xf.shape[1], "balanced_accuracy_mean": round(float(np.mean(accs)), 3),
                    "balanced_accuracy_sd": round(float(np.std(accs)), 3), "chance": round(1 / len(cohorts), 3)})
    probe = pd.DataFrame(out)
    probe.to_csv(ROOT / "results/tables/T03_cohort_probe_classical.csv", index=False)
    print("\ncohort probe on classical features:\n" + probe.to_string(index=False))

    # ---- figure: processed PSD per cohort x diagnosis
    fig, axes = plt.subplots(1, len(cohorts), figsize=(4.5 * len(cohorts), 3.8), sharey=True)
    for ax, c in zip(np.atleast_1d(axes), cohorts):
        for g, color in [("AD", "#c0392b"), ("HC", "#2471a3")]:
            ids = meta[(meta.cohort == c) & (meta.diagnosis == g)]["participant_id"]
            m = 10 * np.log10(np.array([psd_store[i] for i in ids]))
            ax.plot(f, m.mean(0), color=color, label=f"{g} (n={len(ids)})")
            ax.fill_between(f, m.mean(0) - m.std(0), m.mean(0) + m.std(0), color=color, alpha=0.15)
        ax.set(title=c, xlabel="Frequency (Hz)", xlim=(0, 40))
        ax.axvspan(0.5, 30, color="grey", alpha=0.07)
        ax.legend()
    np.atleast_1d(axes)[0].set_ylabel("Power (dB re 1 µV²/Hz), processed")
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-003_psd_processed.png", dpi=150)

    # ---- figure: raw traces for a visual check (2 random participants per cohort, 4 channels, 4 s)
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(len(cohorts), 2, figsize=(11, 2.6 * len(cohorts)), squeeze=False)
    for r, c in enumerate(cohorts):
        ids = list(meta[meta.cohort == c]["participant_id"])
        for k, gid in enumerate(rng.choice(ids, 2, replace=False)):
            X = np.load(ROOT / "data/processed" / c / f"{gid}.npz")["X"]
            ep = X[len(X) // 2]
            t = np.arange(ep.shape[1]) / SFREQ
            ax = axes[r, k]
            for j, ch in enumerate([0, 7, 11, 14]):        # Fp1, C3, P3, O1
                ax.plot(t, ep[ch] - 60 * j, lw=0.6)
            ax.set(title=f"{gid} ({meta.set_index('participant_id').loc[gid, 'diagnosis']})", yticks=[0, -60, -120, -180],
                   yticklabels=["Fp1", "C3", "P3", "O1"], xlabel="s")
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-003_snippets.png", dpi=130)
    print("\nfigures -> results/figures/EXP-003_*.png")


if __name__ == "__main__":
    main()

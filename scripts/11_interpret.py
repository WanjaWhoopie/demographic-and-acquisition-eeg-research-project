"""Phase 11 interpretation (exploratory): EXP-050 band perturbation, EXP-051 channel occlusion,
EXP-052 classifier score vs classical EEG markers (D-036, D-038).

    python scripts/11_interpret.py [--part all|bands|channels|markers]

EXP-050 needs the band-stopped embeddings first (GPU, ~2 min per band):
    python scripts/04_extract_embeddings.py --cohort <cohort> --band-stop <band>
for every cohort and band in eegconf.features.BANDS.

EXP-050 band perturbation
  For every LOCO fold and for the original and the centred (variant i) classifier, the EXP-031
  classifier (same configuration and C, refitted on the training cohorts' unperturbed data) is
  applied to the held-out cohort twice: unperturbed and with one band removed from the input.
  Unperturbed predictions must reproduce the saved EXP-031 predictions. Reported per band:
  mean over folds of AUROC(unperturbed) − AUROC(band removed), paired bootstrap CI, and the mean
  change in predicted AD probability among AD and among HC participants.
EXP-051 channel occlusion (D-038)
  Same procedure as EXP-050, with the held-out input occluded instead of band-stopped: one of the 16
  channels, or one region (eegconf.features.REGIONS), set to zero after average referencing.
  Embeddings: python scripts/04_extract_embeddings.py --cohort <cohort> --occlude <condition>.
  Reported per condition as for EXP-050, plus topographic maps of the single-channel ΔAUROC.
EXP-052 markers
  Per participant from the preprocessed epochs: relative theta, relative alpha, theta/alpha ratio
  and peak alpha frequency (centre of gravity 7-13 Hz), each as the global mean and the posterior
  mean (O1, O2, P3, P4, T5, T6), plus the global aperiodic exponent (Phase 6 features). Spearman
  correlation with the out-of-fold classifier score (logit of the EXP-031 probability) within each
  held-out cohort; Benjamini-Hochberg FDR across markers × cohorts, separately per classifier.

Outputs: results/tables/T11_band_perturbation.csv, T11_channel_occlusion.csv, T11_markers.csv,
results/figures/EXP-050_band_perturbation.png, EXP-051_channel_occlusion.png
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.stats import false_discovery_control, spearmanr

from eegconf import stats
from eegconf.control import make_control
from eegconf.evaluation import model, splits
from eegconf.features import BANDS, REGIONS, participant_psd, relative_band_power
from eegconf.representation import participant_tensor

ROOT = Path(__file__).resolve().parents[1]
TOKENS, POOLINGS = ("patch_mean", "cls"), ("mean", "median")
POSTERIOR = ("O1", "O2", "P3", "P4", "T5", "T6")
CONTROLS = ("none", "centring_i")


def config_slice(Z, name):
    """'b11_cls_mean' -> Z[:, 10, 1, 0, :]"""
    b, rest = name.split("_", 1)
    tok = "patch_mean" if rest.startswith("patch_mean") else "cls"
    pool = rest[len(tok) + 1:]
    return Z[:, int(b[1:]) - 1, TOKENS.index(tok), POOLINGS.index(pool), :]


def frozen_predict(Z_orig, Z_test, cfg_row, ctrl_name, y, cohort, tr, te):
    """Refit the fold's chosen classifier on unperturbed training rows; predict test rows of Z_test."""
    X0, Xt = config_slice(Z_orig, cfg_row["selected"]), config_slice(Z_test, cfg_row["selected"])
    ctrl = make_control(ctrl_name, cohort, y)
    if ctrl is None:
        Xa, Xb = X0[tr], Xt[te]
    else:
        c = ctrl().fit(X0[tr], tr)
        Xa, Xb = c.transform(X0[tr], tr), c.transform(Xt[te], te)
    m = model.make_clf(cfg_row["C"]).fit(Xa, y[tr])
    return m.predict_proba(Xb)[:, 1]


def boot_mean(v, seed, n=2000):
    rng = np.random.default_rng(seed)
    reps = [rng.choice(v, len(v)).mean() for _ in range(n)]
    return v.mean(), *np.percentile(reps, [2.5, 97.5])


def perturbation(meta, z, seed, conditions, model_dir, key):
    """Apply each LOCO fold's EXP-031 classifiers to the held-out cohort intact and perturbed.

    conditions: perturbation names; model_dir(name) gives the embeddings folder under data/embeddings;
    key: name of the condition column in the output ("band" for EXP-050, "condition" for EXP-051).
    Returns one row per condition × classifier × fold, plus a "MEAN over folds" row with the
    paired-bootstrap CI and the mean change in P(AD) among AD and among HC participants."""
    y, cohort = meta["diagnosis"].to_numpy(), meta["cohort"].to_numpy()
    folds = list(splits.leave_one_cohort_out(meta))
    t08 = pd.read_csv(ROOT / "results/tables/T08_loco.csv")
    saved = pd.read_csv(ROOT / "results/runs/EXP-031/predictions.csv")
    Z0 = z["Z_labram-base"]
    rows = []
    for name in conditions:
        Zb = np.stack([participant_tensor(np.load(ROOT / "data/embeddings" / model_dir(name) / c / f"{g}.npz"))
                       for g, c in zip(meta["global_id"], cohort)])
        for ctrl in CONTROLS:
            per, dps = [], []
            for held, tr, te in folds:
                cfg_row = t08[(t08.control == ctrl) & (t08.held_out == held)].iloc[0]
                p0 = frozen_predict(Z0, Z0, cfg_row, ctrl, y, cohort, tr, te)
                ref = saved[(saved.control == ctrl) & (saved.cohort == held)]["proba"].to_numpy()
                # Same model as EXP-031: AUROC must be identical. Probabilities can differ slightly in
                # weakly regularised folds (C = 100: the solver stops at a marginally different point;
                # largest difference seen 0.012), so they are checked to 0.02.
                assert stats.metrics(y[te], p0)["auroc"] == stats.metrics(y[te], ref)["auroc"], f"{ctrl} {held}: AUROC differs"
                assert np.abs(p0 - ref).max() < 0.02, f"{ctrl} {held}: refit does not reproduce EXP-031"
                p1 = frozen_predict(Z0, Zb, cfg_row, ctrl, y, cohort, tr, te)
                per.append((y[te], p0, p1))
                d, lo, hi = stats.paired_delta(y[te], p0, p1, seed=seed)
                rows.append({key: name, "classifier": ctrl, "held_out": held, "delta_auroc": d, "ci_low": lo, "ci_high": hi})
                dps.append(pd.DataFrame({"diagnosis": y[te], "dp": p1 - p0}))
            d, lo, hi = stats.mean_over_folds(per, seed=seed)
            dp = pd.concat(dps)
            ad, hc = boot_mean(dp[dp.diagnosis == 1].dp.to_numpy(), seed), boot_mean(dp[dp.diagnosis == 0].dp.to_numpy(), seed)
            rows.append({key: name, "classifier": ctrl, "held_out": "MEAN over folds", "delta_auroc": d, "ci_low": lo,
                         "ci_high": hi, "mean_dp_AD": ad[0], "mean_dp_AD_ci": f"[{ad[1]:+.3f}, {ad[2]:+.3f}]",
                         "mean_dp_HC": hc[0], "mean_dp_HC_ci": f"[{hc[1]:+.3f}, {hc[2]:+.3f}]"})
            print(f"{name:16s} {ctrl:10s} ΔAUROC (intact − perturbed) {d:+.3f} [{lo:+.3f}, {hi:+.3f}]  "
                  f"Δp AD {ad[0]:+.3f}  Δp HC {hc[0]:+.3f}")
    return pd.DataFrame(rows)


def bands(meta, z, seed):
    """EXP-050: one frequency band removed from the held-out input."""
    out = perturbation(meta, z, seed, BANDS, lambda b: f"labram-base-stop-{b}", "band")
    out.round(4).to_csv(ROOT / "results/tables/T11_band_perturbation.csv", index=False)

    m = out[(out.held_out == "MEAN over folds")]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    x = np.arange(len(BANDS))
    for k, ctrl in enumerate(CONTROLS):
        d = m[m.classifier == ctrl].set_index("band").loc[list(BANDS)]
        ax[0].errorbar(x + 0.15 * (k - 0.5), d.delta_auroc, yerr=[d.delta_auroc - d.ci_low, d.ci_high - d.delta_auroc],
                       fmt="o", capsize=3, label="original" if ctrl == "none" else "centred (i)")
        ax[1].bar(x + 0.2 * (2 * k - 1) - 0.1, d.mean_dp_AD, 0.2, label=f"AD, {'original' if ctrl == 'none' else 'centred'}")
        ax[1].bar(x + 0.2 * (2 * k - 1) + 0.1, d.mean_dp_HC, 0.2, label=f"HC, {'original' if ctrl == 'none' else 'centred'}")
    for a in ax:
        a.axhline(0, color="k", lw=0.8)
        a.set_xticks(x, list(BANDS))
    ax[0].set(ylabel="ΔAUROC (intact − band removed)", title="Loss of discrimination")
    ax[1].set(ylabel="mean change in P(AD)", title="Shift in predicted AD probability")
    ax[0].legend(fontsize=8); ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/EXP-050_band_perturbation.png", dpi=150)


def channels(meta, z, seed):
    """EXP-051: one channel or one region zeroed in the held-out input (D-038)."""
    import mne
    chans = yaml.safe_load(open(ROOT / "configs/preprocessing.yaml"))["channels"]
    conditions = list(REGIONS) + chans
    out = perturbation(meta, z, seed, conditions, lambda c: f"labram-base-occ-{c}", "condition")
    out.insert(1, "kind", np.where(out.condition.isin(list(REGIONS)), "region", "channel"))
    out.round(4).to_csv(ROOT / "results/tables/T11_channel_occlusion.csv", index=False)

    m = out[out.held_out == "MEAN over folds"]
    # Reading rule fixed in D-038, applied to the original classifier
    reg = m[(m.kind == "region") & (m.classifier == "none")].set_index("condition")
    post = reg.loc["posterior"]
    if post.ci_low > 0 and post.delta_auroc == reg.delta_auroc.max():
        verdict = "posterior emphasis"
    elif (reg.ci_low <= 0).all():
        verdict = "spatially distributed"
    else:
        verdict = "mixed"
    print(f"EXP-051 reading rule (original classifier): {verdict}")

    # Figure: single-channel topomaps (diverging, centred on 0) and region estimates with CIs
    info = mne.create_info(chans, sfreq=200.0, ch_types="eeg")
    info.set_montage("standard_1020")
    single = m[m.kind == "channel"]
    lim = float(np.abs(single.delta_auroc).max())
    fig, ax = plt.subplots(1, 3, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1, 1.4], "wspace": 0.35})
    colours = {"none": "#2a78d6", "centring_i": "#eb6834"}            # same categorical slots as F5/F6
    for k, ctrl in enumerate(CONTROLS):
        v = single[single.classifier == ctrl].set_index("condition").loc[chans, "delta_auroc"].to_numpy()
        im, _ = mne.viz.plot_topomap(v, info, axes=ax[k], show=False, cmap="RdBu_r", vlim=(-lim, lim),
                                     names=chans, sensors=True, contours=0)
        ax[k].set_title(("original" if ctrl == "none" else "centred (i)") + ": single channels")
    fig.colorbar(im, ax=ax[:2], orientation="horizontal", shrink=0.6, pad=0.05, label="ΔAUROC (intact − occluded)")
    y0 = np.arange(len(REGIONS))
    for k, ctrl in enumerate(CONTROLS):
        d = m[(m.kind == "region") & (m.classifier == ctrl)].set_index("condition").loc[list(REGIONS)]
        ax[2].errorbar(d.delta_auroc, y0 + 0.15 * (k - 0.5), xerr=[d.delta_auroc - d.ci_low, d.ci_high - d.delta_auroc],
                       fmt="o", capsize=3, color=colours[ctrl], label="original" if ctrl == "none" else "centred (i)")
    ax[2].axvline(0, color="k", lw=0.8)
    ax[2].set_yticks(y0, [r.replace("_", "-" + chr(10)) for r in REGIONS])     # "central-" / "temporal" on two lines
    ax[2].set(xlabel="ΔAUROC (intact − occluded)", title="Region occluded")
    ax[2].legend(fontsize=8)
    fig.savefig(ROOT / "results/figures/EXP-051_channel_occlusion.png", dpi=150, bbox_inches="tight")


def markers(meta, z):
    """EXP-052: per-participant classical markers vs the out-of-fold classifier score."""
    rows = []
    for g, c in zip(meta["global_id"], meta["cohort"]):
        proc = np.load(ROOT / "data/processed" / c / f"{g}.npz")
        names = [str(n) for n in proc["ch_names"]]
        post = [names.index(ch) for ch in POSTERIOR]
        f, p = participant_psd(proc["X"])
        # relative_band_power is band-major (delta ch1..16, theta ch1..16, ...) -> channels × bands
        rel = relative_band_power(f, p).reshape(len(BANDS), len(names)).T
        th, al = rel[:, list(BANDS).index("theta")], rel[:, list(BANDS).index("alpha")]
        a = (f >= 7) & (f <= 13)
        cog = lambda P: float((f[a] * P[a]).sum() / P[a].sum())                # centre of gravity 7-13 Hz
        r = {"global_id": g}
        for region, idx in (("global", slice(None)), ("posterior", post)):
            r[f"rel_theta_{region}"] = th[idx].mean()
            r[f"rel_alpha_{region}"] = al[idx].mean()
            r[f"theta_alpha_ratio_{region}"] = th[idx].mean() / al[idx].mean()
            r[f"paf_{region}"] = cog(p[idx].mean(0))
        rows.append(r)
    mk = pd.DataFrame(rows)
    mk["aperiodic_exponent_global"] = np.nanmean(z["classical"][:, 64:80], axis=1)  # 16 exponents (Phase 6)
    preds = pd.read_csv(ROOT / "results/runs/EXP-031/predictions.csv")
    out = []
    names = [c for c in mk.columns if c != "global_id"]
    for ctrl in CONTROLS:
        d = preds[preds.control == ctrl].merge(mk, on="global_id")
        d["score"] = np.log(d.proba.clip(1e-6, 1 - 1e-6) / (1 - d.proba.clip(1e-6, 1 - 1e-6)))
        block = []
        for c, g in d.groupby("cohort"):
            for name in names:
                ok = g[name].notna()
                rho, p = spearmanr(g.loc[ok, "score"], g.loc[ok, name])
                rho_dx = spearmanr(g.loc[ok, "diagnosis"], g.loc[ok, name])[0]      # marker vs diagnosis itself
                block.append({"classifier": ctrl, "cohort": c, "marker": name, "n": int(ok.sum()), "spearman_rho": rho,
                              "p": p, "rho_marker_vs_diagnosis": rho_dx})
        block = pd.DataFrame(block)
        block["p_fdr"] = false_discovery_control(block.p.to_numpy(), method="bh")
        out.append(block)
    out = pd.concat(out)
    out.round(4).to_csv(ROOT / "results/tables/T11_markers.csv", index=False)
    s = out[(out.classifier == "centring_i") & (out.p_fdr < 0.05)]
    print(f"markers: {len(s)} of {len(out) // 2} correlations significant after FDR (centred classifier)")
    print(out[out.classifier == "centring_i"].pivot(index="marker", columns="cohort", values="spearman_rho").round(2).to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all", choices=["all", "bands", "channels", "markers"])
    args = ap.parse_args()
    seed = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))["seed"]
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "participant_id", "diagnosis")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    if args.part in ("all", "bands"):
        bands(meta, z, seed)
    if args.part in ("all", "channels"):
        channels(meta, z, seed)
    if args.part in ("all", "markers"):
        markers(meta, z)


if __name__ == "__main__":
    main()

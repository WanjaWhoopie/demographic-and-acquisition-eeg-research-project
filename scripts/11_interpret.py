"""Phase 11 interpretation (exploratory): EXP-050 band perturbation, EXP-052 classifier score vs
classical EEG markers (D-036).

    python scripts/11_interpret.py [--part all|bands|markers]

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
EXP-052 markers
  Per participant from the preprocessed epochs: relative theta, relative alpha, theta/alpha ratio
  and peak alpha frequency (centre of gravity 7-13 Hz), each as the global mean and the posterior
  mean (O1, O2, P3, P4, T5, T6), plus the global aperiodic exponent (Phase 6 features). Spearman
  correlation with the out-of-fold classifier score (logit of the EXP-031 probability) within each
  held-out cohort; Benjamini-Hochberg FDR across markers × cohorts, separately per classifier.

Outputs: results/tables/T11_band_perturbation.csv, T11_markers.csv,
results/figures/EXP-050_band_perturbation.png
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
from eegconf.features import BANDS, participant_psd, relative_band_power
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


def bands(meta, z, seed):
    y, cohort = meta["diagnosis"].to_numpy(), meta["cohort"].to_numpy()
    folds = list(splits.leave_one_cohort_out(meta))
    t08 = pd.read_csv(ROOT / "results/tables/T08_loco.csv")
    saved = pd.read_csv(ROOT / "results/runs/EXP-031/predictions.csv")
    Z0 = z["Z_labram-base"]
    rows, dp_all = [], []
    for band in BANDS:
        Zb = np.stack([participant_tensor(np.load(ROOT / f"data/embeddings/labram-base-stop-{band}" / c / f"{g}.npz"))
                       for g, c in zip(meta["global_id"], cohort)])
        for ctrl in CONTROLS:
            per, dps = [], []
            for held, tr, te in folds:
                cfg_row = t08[(t08.control == ctrl) & (t08.held_out == held)].iloc[0]
                p0 = frozen_predict(Z0, Z0, cfg_row, ctrl, y, cohort, tr, te)
                ref = saved[(saved.control == ctrl) & (saved.cohort == held)]["proba"].to_numpy()
                assert np.allclose(p0, ref, atol=1e-6), f"{ctrl} {held}: refit does not reproduce EXP-031"
                p1 = frozen_predict(Z0, Zb, cfg_row, ctrl, y, cohort, tr, te)
                per.append((y[te], p0, p1))
                d, lo, hi = stats.paired_delta(y[te], p0, p1, seed=seed)
                rows.append({"band": band, "classifier": ctrl, "held_out": held, "delta_auroc": d, "ci_low": lo, "ci_high": hi})
                dps.append(pd.DataFrame({"band": band, "classifier": ctrl, "cohort": held, "diagnosis": y[te], "dp": p1 - p0}))
            d, lo, hi = stats.mean_over_folds(per, seed=seed)
            dp = pd.concat(dps)
            ad, hc = boot_mean(dp[dp.diagnosis == 1].dp.to_numpy(), seed), boot_mean(dp[dp.diagnosis == 0].dp.to_numpy(), seed)
            rows.append({"band": band, "classifier": ctrl, "held_out": "MEAN over folds", "delta_auroc": d, "ci_low": lo,
                         "ci_high": hi, "mean_dp_AD": ad[0], "mean_dp_AD_ci": f"[{ad[1]:+.3f}, {ad[2]:+.3f}]",
                         "mean_dp_HC": hc[0], "mean_dp_HC_ci": f"[{hc[1]:+.3f}, {hc[2]:+.3f}]"})
            dp_all.append(dp)
            print(f"{band:6s} {ctrl:10s} ΔAUROC (intact − removed) {d:+.3f} [{lo:+.3f}, {hi:+.3f}]  "
                  f"Δp AD {ad[0]:+.3f}  Δp HC {hc[0]:+.3f}")
    out = pd.DataFrame(rows)
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
    ap.add_argument("--part", default="all", choices=["all", "bands", "markers"])
    args = ap.parse_args()
    seed = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))["seed"]
    z = np.load(ROOT / "data/features/participant_features.npz", allow_pickle=True)
    meta = pd.DataFrame({k: z[k] for k in ("global_id", "cohort", "participant_id", "diagnosis")})
    meta["diagnosis"] = meta["diagnosis"].astype(int)
    if args.part in ("all", "bands"):
        bands(meta, z, seed)
    if args.part in ("all", "markers"):
        markers(meta, z)


if __name__ == "__main__":
    main()

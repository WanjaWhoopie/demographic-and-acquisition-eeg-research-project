"""Phase 10: statistics from saved predictions only (T10.4, T10.5, T10.7; D-034).

    python scripts/10_stats.py

Nothing is refitted. The script reads the participant predictions saved by Phases 8 and 9
(results/runs/EXP-0xx/predictions.csv, local) and

1. reproduces every headline ΔAUROC and CI in T08_loco_deltas.csv, T08_demographic.csv and
   T09_primary_and_sensitivity.csv, and stops if any value differs by more than 1e-4 (T10.7);
2. computes the two-sided bootstrap p-value of the primary outcome (tested alone) and of the six
   estimable secondary comparisons, with Holm adjustment across those six (D-028, D-034);
3. cross-checks every per-fold bootstrap AUROC CI against DeLong's analytic CI and flags any limit
   that differs by more than 0.05 (T10.4).

Outputs: results/tables/T10_reproduction.csv, T10_tests.csv, T10_delong.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from eegconf import stats

ROOT = Path(__file__).resolve().parents[1]
RUNS, TABLES = ROOT / "results/runs", ROOT / "results/tables"
TOL = 1e-4


def folds_from(pred, control):
    """{held_out: (y, p)} in the order the folds were written (the bootstrap draws depend on it)."""
    d = pred[pred.control == control]
    return {h: (g["diagnosis"].to_numpy(), g["proba"].to_numpy()) for h, g in d.groupby("cohort", sort=False)}


def loco_delta(pred, ctrl, seed):
    """Mean over folds of AUROC(none) − AUROC(ctrl) with CI and the bootstrap replicates."""
    f0, f1 = folds_from(pred, "none"), folds_from(pred, ctrl)
    return stats.mean_over_folds([(f0[h][0], f0[h][1], f1[h][1]) for h in f0], seed=seed, return_reps=True)


def main():
    seed = yaml.safe_load(open(ROOT / "configs/analysis.yaml"))["seed"]
    p31 = pd.read_csv(RUNS / "EXP-031/predictions.csv")
    p30 = pd.read_csv(RUNS / "EXP-030/predictions.csv")
    sens = {"without ADFSU (EXP-041)": pd.read_csv(RUNS / "EXP-041/predictions.csv"),
            "8-s equal length (EXP-043)": pd.read_csv(RUNS / "EXP-043/predictions.csv"),
            "amplitude-scaled (EXP-044)": pd.read_csv(RUNS / "EXP-044/predictions.csv")}
    t08 = pd.read_csv(TABLES / "T08_loco_deltas.csv")
    t08d = pd.read_csv(TABLES / "T08_demographic.csv")
    t09 = pd.read_csv(TABLES / "T09_primary_and_sensitivity.csv")

    # ------------------------------------------------ 1. recompute every headline ΔAUROC
    rec, reps = [], {}

    def check(label, new, table_row):
        est, lo, hi = new[:3]
        # T08_demographic has both an AUROC CI (ci_low) and a ΔAUROC CI (delta_ci_low); use the latter
        lo_col = "delta_ci_low" if "delta_ci_low" in table_row.index else "ci_low"
        hi_col = "delta_ci_high" if "delta_ci_high" in table_row.index else "ci_high"
        old = (table_row["delta_auroc"], table_row[lo_col], table_row[hi_col])
        diff = max(abs(a - b) for a, b in zip((est, lo, hi), old))
        rec.append({"quantity": label, "delta_auroc": est, "ci_low": lo, "ci_high": hi, "max_abs_diff_vs_table": diff})
        assert diff <= TOL, f"{label} not reproduced: {diff}"

    for ctrl in ("centring_i", "centring_ii", "leace", "inlp"):
        r = loco_delta(p31, ctrl, seed)
        reps[ctrl] = r[3]
        check(f"LOCO {ctrl}", r, t08[(t08.control == ctrl) & (t08.held_out == "MEAN over folds")].iloc[0])
    y30 = p30[p30.control == "none"]["diagnosis"].to_numpy()
    for ctrl in ("resid_all", "resid_hc"):
        r = stats.paired_delta(y30, p30[p30.control == "none"]["proba"].to_numpy(),
                               p30[p30.control == ctrl]["proba"].to_numpy(), seed=seed, return_reps=True)
        reps[ctrl] = r[3]
        check(f"ds004504 {ctrl}", r, t08d[t08d.control == ctrl].iloc[0])
    for name, pred in sens.items():
        r = loco_delta(pred, "centring_i", seed)
        reps[name] = r[3]
        check(name, r, t09[(t09.analysis == name) & (t09.held_out == "MEAN over folds")].iloc[0])
    check("primary (EXP-040)", loco_delta(p31, "centring_i", seed),
          t09[(t09.analysis == "primary (EXP-040)") & (t09.held_out == "MEAN over folds")].iloc[0])
    pd.DataFrame(rec).round(4).to_csv(TABLES / "T10_reproduction.csv", index=False)
    print(f"reproduced {len(rec)} headline values from saved predictions (max difference "
          f"{max(r['max_abs_diff_vs_table'] for r in rec):.1e})")

    # ------------------------------------------------ 2. p-values and Holm (D-028, D-034)
    family = [("1 centring variant (ii)", "centring_ii"), ("2 LEACE", "leace"), ("3 INLP", "inlp"),
              ("4 age/sex residualisation, ds004504", "resid_all"), ("5 8-s equal length", "8-s equal length (EXP-043)"),
              ("6 amplitude-scaled", "amplitude-scaled (EXP-044)")]
    est = {r["quantity"].replace("LOCO ", "").replace("ds004504 ", ""): r for r in rec}
    rows = [{"comparison": "PRIMARY: centring variant (i), EXP-040", "family": "primary (alone)",
             "delta_auroc": est["primary (EXP-040)"]["delta_auroc"], "ci_low": est["primary (EXP-040)"]["ci_low"],
             "ci_high": est["primary (EXP-040)"]["ci_high"], "p": stats.bootstrap_p(reps["centring_i"]), "p_holm": np.nan}]
    fam_p = [stats.bootstrap_p(reps[k]) for _, k in family]
    adj = stats.holm(fam_p)
    for (label, k), p, pa in zip(family, fam_p, adj):
        e = est[k]
        rows.append({"comparison": label, "family": "secondary (Holm, m = 6)", "delta_auroc": e["delta_auroc"],
                     "ci_low": e["ci_low"], "ci_high": e["ci_high"], "p": p, "p_holm": pa})
    rows.append({"comparison": "7 without ADFSU", "family": "secondary", "note": "not estimable (D-033)"})
    rows.append({"comparison": "8 ADFSU AD subsampled", "family": "secondary", "note": "distribution, not tested (EXP-042)"})
    tests = pd.DataFrame(rows)
    tests.round(4).to_csv(TABLES / "T10_tests.csv", index=False)
    for r in rows:
        if "p" in r and not pd.isna(r.get("p")):
            print(f"{r['comparison']:40s} Δ {r['delta_auroc']:+.3f} [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]  "
                  f"p {r['p']:.4f}  Holm {r['p_holm']:.4f}" if not pd.isna(r["p_holm"]) else
                  f"{r['comparison']:40s} Δ {r['delta_auroc']:+.3f} [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]  p {r['p']:.4f}")

    # ------------------------------------------------ 3. DeLong cross-check of per-fold AUROC CIs
    dl = []
    for analysis, pred in [("primary (EXP-040)", p31)] + list(sens.items()):
        for ctrl in ("none", "centring_i"):
            for h, (y, p) in folds_from(pred, ctrl).items():
                b = stats.bootstrap_auc(y, p, seed=seed)
                d = stats.delong_ci(y, p)
                diff = max(abs(b[1] - d[1]), abs(b[2] - d[2]))
                dl.append({"analysis": analysis, "control": ctrl, "held_out": h, "auroc": b[0],
                           "boot_ci": f"[{b[1]:.3f}, {b[2]:.3f}]", "delong_ci": f"[{d[1]:.3f}, {d[2]:.3f}]",
                           "max_limit_diff": diff, "material": diff > 0.05})
    dl = pd.DataFrame(dl)
    dl.round(4).to_csv(TABLES / "T10_delong.csv", index=False)
    print(f"DeLong vs bootstrap: {len(dl)} fold CIs, largest limit difference {dl.max_limit_diff.max():.3f}, "
          f"material (> 0.05): {int(dl.material.sum())}")
    if dl.material.any():
        print(dl[dl.material][["analysis", "control", "held_out", "auroc", "boot_ci", "delong_ci"]].to_string(index=False))


if __name__ == "__main__":
    main()

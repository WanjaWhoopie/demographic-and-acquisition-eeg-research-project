"""Phase 12 report figures F5 and F6 (T12.3), drawn only from committed result tables.

    python scripts/12_figures.py

Nothing is refitted. Inputs: results/tables/T08_loco.csv, T08_loco_deltas.csv, T08_demographic.csv,
T09_primary_and_sensitivity.csv, T09_adfsu_subsample_draws.csv.

F5  Per-fold and mean LOCO AUROC with 95% CI for the original representation and the three cohort
    controls (centring variant i, LEACE, INLP).
F6  ΔAUROC = AUROC(original) − AUROC(controlled) with 95% CI for the primary analysis, the other
    controls, the sensitivity analyses and the ds004504 age/sex residualisation; the ADFSU
    subsampling analysis is shown as its 2.5–97.5 percentile range over 100 draws (not a CI).

The other report figures already exist: F3 = EXP-003_psd_processed.png, F4 = EXP-021_layer_profile.png,
F7 = EXP-050_band_perturbation.png; EXP-053/054 figures support the exploratory section.
F1 (pipeline) and F2 (participant flow) are diagrams in the report text.
Outputs: results/figures/F5_loco_auroc.png, results/figures/F6_delta_auroc.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T, FIG = ROOT / "results/tables", ROOT / "results/figures"

# categorical slots 1-4 of the validated reference palette, in fixed order (never cycled)
COLOURS = {"none": "#2a78d6", "centring_i": "#eb6834", "leace": "#1baf7a", "inlp": "#eda100"}
LABELS = {"none": "Original", "centring_i": "Centring (i)", "leace": "LEACE", "inlp": "INLP"}
INK, MUTED = "#222222", "#888888"


def style(ax):
    """Recessive axes: no top/right spines, light grid on the value axis only."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=9)
    ax.grid(axis="x", color="#e6e6e6", lw=0.8)
    ax.set_axisbelow(True)


def f5():
    d = pd.read_csv(T / "T08_loco.csv")
    folds = ["ADFSU", "APAVA", "ds004504", "MEAN over folds"]
    names = {"ADFSU": "ADFSU (76 AD / 12 HC)", "APAVA": "APAVA (12 / 11)", "ds004504": "ds004504 (36 / 29)",
             "MEAN over folds": "Mean over folds"}
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    style(ax)
    offs = np.linspace(-0.27, 0.27, len(COLOURS))
    for k, (ctrl, col) in enumerate(COLOURS.items()):
        for i, h in enumerate(folds):
            r = d[(d.control == ctrl) & (d.held_out == h)].iloc[0]
            y = len(folds) - 1 - i + offs[::-1][k]
            ax.plot([r.ci_low, r.ci_high], [y, y], color=col, lw=2, solid_capstyle="round")
            ax.plot(r.auroc, y, "o", ms=8 if h.startswith("MEAN") else 6, color=col, mec="white", mew=1.5,
                    label=LABELS[ctrl] if i == 0 else None)
    ax.axhline(0.5, color=MUTED, lw=0.8, ls=":")                  # separates mean row from folds
    ax.set_yticks(range(len(folds)), [names[h] for h in folds[::-1]])
    ax.set_xlim(0.6, 1.0)
    ax.set_xlabel("AUROC on the held-out cohort (95% participant-bootstrap CI)", color=INK)
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4)
    ax.set_title("F5  Cross-cohort AD classification before and after cohort control", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "F5_loco_auroc.png", dpi=200)


def f6():
    deltas = pd.read_csv(T / "T08_loco_deltas.csv")
    sens = pd.read_csv(T / "T09_primary_and_sensitivity.csv")
    demo = pd.read_csv(T / "T08_demographic.csv")
    draws = pd.read_csv(T / "T09_adfsu_subsample_draws.csv")
    mean = lambda df, c: df[(df.control == c) & (df.held_out == "MEAN over folds")].iloc[0]
    srow = lambda a: sens[(sens.analysis.str.startswith(a)) & (sens.held_out == "MEAN over folds")].iloc[0]
    dcol = [c for c in draws.columns if "delta" in c][0]

    rows = []   # (label, estimate, low, high, kind)
    p = srow("primary")
    rows.append(("Primary: centring (i), LOCO", p.delta_auroc, p.delta_ci_low, p.delta_ci_high, "ci"))
    for c in ("leace", "inlp"):
        r = mean(deltas, c)
        rows.append((f"{LABELS[c]}, LOCO", r.delta_auroc, r.ci_low, r.ci_high, "ci"))
    for a, lab in (("8-s", "8 s per participant (centring i)"), ("amplitude", "Amplitude-scaled (centring i)")):
        r = srow(a)
        rows.append((lab, r.delta_auroc, r.delta_ci_low, r.delta_ci_high, "ci"))
    v = draws[dcol].to_numpy()
    rows.append(("ADFSU AD subsampled, 100 draws", np.median(v), *np.percentile(v, [2.5, 97.5]), "range"))
    r = demo[demo.control == "resid_all"].iloc[0]
    rows.append(("Age/sex residualisation, ds004504", r.delta_auroc, r.delta_ci_low, r.delta_ci_high, "ci"))

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    style(ax)
    for i, (lab, e, lo, hi, kind) in enumerate(rows):
        y = len(rows) - 1 - i
        col = COLOURS["none"] if i == 0 else INK
        ax.plot([lo, hi], [y, y], color=col, lw=2, ls="-" if kind == "ci" else (0, (2, 1.5)), solid_capstyle="round")
        ax.plot(e, y, "D" if i == 0 else "o", ms=8 if i == 0 else 6, color=col, mec="white", mew=0.8)
    ax.axvline(0, color=INK, lw=0.9)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows[::-1]])
    ax.set_xticks(np.arange(-0.1, 0.151, 0.05))
    ax.set_xlabel("ΔAUROC = original − controlled (negative: control improved transfer)", color=INK, fontsize=9)
    ax.set_title("F6  Effect of removing nuisance information", fontsize=10, color=INK, loc="left")
    ax.text(1.0, -0.30, "Solid: 95% bootstrap CI. Dashed: 2.5–97.5 percentile over draws (not a CI).",
            transform=ax.transAxes, ha="right", fontsize=7, color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG / "F6_delta_auroc.png", dpi=200)


if __name__ == "__main__":
    f5()
    f6()
    print("figures -> results/figures/F5_loco_auroc.png, F6_delta_auroc.png")

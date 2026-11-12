"""Consolidated Excel workbook of every experiment's results (Phase 12, reporting aid).

    python scripts/12_workbook.py          # needs pandas and openpyxl

Reads only committed files: experiments/registry.csv and results/tables/*.csv. Nothing is
recomputed, so every number in the workbook is the number in the committed table it came from.

Layout
  Overview      one row per experiment from the registry (question, method, status, result)
  EXP-xxx       one sheet per run experiment: its registry entry, then every result table that
                belongs to it, each under a caption naming the source CSV (and the row filter,
                where one table holds several experiments)
  Phase5-embed  embedding sanity checks (Phase 5 has no experiment ID)

Output: results/experiments_summary.xlsx. Office files are git-ignored; rebuild with this script.
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results/tables"
OUT = ROOT / "results/experiments_summary.xlsx"

FONT, BOLD = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True)
TITLE = Font(name="Arial", size=13, bold=True)
CAPTION = Font(name="Arial", size=10, bold=True, color="1F4E79")
HEAD_FILL = PatternFill("solid", fgColor="DDEBF7")
THIN = Border(bottom=Side(style="thin", color="9BC2E6"))
WRAP = Alignment(wrap_text=True, vertical="top")


def tab(name, filt=None, note=None):
    """One result table: (caption, DataFrame). `filt` is a row filter for shared tables."""
    d = pd.read_csv(T / f"{name}.csv")
    if filt is not None:
        d = d[filt(d)]
    cap = f"{name}.csv" + (f"  ({note})" if note else "")
    return cap, d.reset_index(drop=True)


def col(c, *vals):
    """Row filter: first-named column equals one of vals."""
    return lambda d: d[c].astype(str).isin(vals)


def startswith(c, prefix):
    return lambda d: d[c].astype(str).str.startswith(prefix)


# experiment -> list of result tables; filters split tables that hold several experiments
SHEETS = {
    "EXP-001": [tab("T00_audit_ds004504_summary"), tab("T00_audit_ADFSU_summary"), tab("T00_audit_APAVA_summary"),
                tab("T01_cohort_summary")],
    "EXP-002": [tab("T02_overlap_summary")],
    "EXP-003": [tab("T03_preprocessing_qc"), tab("T03_cohort_probe_classical")],
    "EXP-010": [tab("T06_within_cohort", col("representation", "labram"), "LaBraM rows"),
                tab("T06_selected_configs", lambda d: (d.representation == "labram") & d.analysis.str.startswith("within"),
                    "LaBraM, within-cohort")],
    "EXP-011": [tab("T06_loco", col("representation", "labram"), "LaBraM rows"),
                tab("T06_selected_configs", lambda d: (d.representation == "labram") & d.analysis.str.startswith("loco"),
                    "LaBraM, LOCO")],
    "EXP-012": [tab("T06_within_cohort", col("representation", "classical", "labram"), "classical vs LaBraM"),
                tab("T06_loco", col("representation", "classical", "labram"), "classical vs LaBraM"),
                tab("T06_loco_deltas", col("comparison", "labram - classical"))],
    "EXP-013": [tab("T06_nuisance_baselines"),
                tab("T06_within_cohort", col("representation", "random", "labram"), "random weights vs pretrained"),
                tab("T06_loco", col("representation", "random", "labram"), "random weights vs pretrained"),
                tab("T06_loco_deltas", col("comparison", "labram - random"))],
    "EXP-020": [tab("T07_age_sex_probes"), tab("T07_permutation_tests"),
                tab("T07_selected_configs", col("probe", "age", "sex"), "age and sex probes")],
    "EXP-021": [tab("T07_cohort_probe"), tab("T07_cohort_confusion"), tab("T07_cohort_layer_profile"),
                tab("T07_selected_configs", col("probe", "cohort"), "cohort probe")],
    "EXP-022": [tab("T07_mlp_probes")],
    "EXP-030": [tab("T08_demographic"),
                tab("T08_verification_probes", col("check", "age, ds004504", "sex, ds004504"), "age and sex checks")],
    "EXP-031": [tab("T08_loco", col("control", "none", "centring_i", "centring_ii"), "original and centring"),
                tab("T08_loco_deltas", col("control", "centring_i", "centring_ii"))],
    "EXP-032": [tab("T08_loco", col("control", "none", "leace", "inlp"), "original, LEACE, INLP"),
                tab("T08_loco_deltas", col("control", "leace", "inlp")),
                tab("T08_verification_probes", startswith("check", "cohort"), "cohort removal checks")],
    "EXP-040": [tab("T09_primary_and_sensitivity", startswith("analysis", "primary")),
                tab("T10_tests"), tab("T10_reproduction"), tab("T10_delong")],
    "EXP-041": [tab("T09_primary_and_sensitivity", startswith("analysis", "without ADFSU"))],
    "EXP-042": [tab("T09_primary_and_sensitivity", startswith("analysis", "ADFSU subsampled")),
                tab("T09_adfsu_subsample_draws", note="100 draws")],
    "EXP-043": [tab("T09_primary_and_sensitivity", startswith("analysis", "8-s"))],
    "EXP-044": [tab("T09_primary_and_sensitivity", startswith("analysis", "amplitude"))],
    "EXP-050": [tab("T11_band_perturbation")],
    "EXP-052": [tab("T11_markers")],
    "EXP-053": [tab("T11_data_amount"), tab("T11_data_amount_paired"), tab("T11_dispersion")],
    "EXP-054": [tab("T11_random_epochs"), tab("T11_random_epochs_contrasts")],
    "Phase5-embed": [tab("T04_embedding_sanity")],
}


def write_table(ws, r, caption, d):
    """Caption, header row and data rows starting at row r; returns the next free row."""
    ws.cell(r, 1, caption).font = CAPTION
    r += 1
    if d.empty:
        ws.cell(r, 1, "(no rows)").font = FONT
        return r + 2
    for j, h in enumerate(d.columns, 1):
        c = ws.cell(r, j, "" if str(h).startswith("Unnamed") else str(h))
        c.font, c.fill, c.border = BOLD, HEAD_FILL, THIN
    for row in d.itertuples(index=False):
        r += 1
        for j, v in enumerate(row, 1):
            c = ws.cell(r, j, None if pd.isna(v) else (v.item() if hasattr(v, "item") else v))
            c.font = FONT
    return r + 2


def fit_columns(ws, first_row, max_width=60):
    """Column width from the longest value in each column, from first_row down (the descriptive
    block above it wraps instead); table captions in column A are excluded."""
    widths = {}
    for row in ws.iter_rows(min_row=first_row):
        for c in row:
            if c.value is None or (c.column == 1 and c.font.bold and c.font.color is not None):
                continue
            widths[c.column] = max(widths.get(c.column, 8), min(len(str(c.value)) + 2, max_width))
    for j, w in widths.items():
        ws.column_dimensions[get_column_letter(j)].width = w


def main():
    reg = pd.read_csv(ROOT / "experiments/registry.csv")
    wb = Workbook()
    ov = wb.active
    ov.title = "Overview"
    ov.cell(1, 1, "Experiments: overview").font = TITLE
    ov.cell(2, 1, "One sheet per experiment follows. Every value is copied from the committed table named "
                  "above it (results/tables/). Built by scripts/12_workbook.py.").font = FONT
    cols = ["exp_id", "objective", "title", "question", "method", "status", "result_summary"]
    r = write_table(ov, 4, "experiments/registry.csv", reg[cols])
    for row in ov.iter_rows(min_row=6):
        for c in row:
            c.alignment = WRAP
    for j, w in zip(range(1, 8), (10, 10, 34, 50, 40, 11, 80)):
        ov.column_dimensions[get_column_letter(j)].width = w
    ov.freeze_panes = "B6"

    for name, tables in SHEETS.items():
        ws = wb.create_sheet(name)
        e = reg[reg.exp_id == name]
        ws.cell(1, 1, f"{name} – {e.title.iloc[0]}" if len(e) else "Phase 5 – embedding sanity checks (T5.4)").font = TITLE
        r = 2
        if len(e):
            for label, key in (("Question", "question"), ("Data", "data"), ("Method", "method"),
                               ("Primary metric", "primary_metric"), ("Status", "status"), ("Result", "result_summary")):
                ws.cell(r, 1, label).font = BOLD
                text = "" if pd.isna(e[key].iloc[0]) else str(e[key].iloc[0])
                c = ws.cell(r, 2, text)
                c.font, c.alignment = FONT, WRAP
                ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=9)   # wrap over B:I
                ws.row_dimensions[r].height = 14 * (1 + len(text) // 110)
                r += 1
            ws.cell(r, 1, "Details").font = BOLD
            ws.cell(r, 2, f"experiments/{name}/README.md").font = FONT
            r += 2
        first_table_row = r
        for cap, d in tables:
            r = write_table(ws, r, cap, d)
        fit_columns(ws, first_table_row)
        ws.column_dimensions["A"].width = max(ws.column_dimensions["A"].width or 0, 16)
    wb.save(OUT)
    print(f"{OUT.relative_to(ROOT)}: {len(wb.sheetnames)} sheets ({', '.join(wb.sheetnames)})")


if __name__ == "__main__":
    main()

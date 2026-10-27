"""Build the combined participant table (WORKPLAN T2.5, T3.10).

    python scripts/00_participants.py

Outputs
- data/metadata/participants_all.csv   one row per participant across the cohorts in use
                                        (participant-level: stays local). Columns:
                                        cohort, participant_id, global_id, diagnosis, age, sex,
                                        mmse, n_segments, total_ec_seconds, included, exclusion_reason
- results/tables/T01_cohort_summary.csv counts and recording time per cohort x diagnosis
                                        (aggregate only: safe to commit)

`included` is decided by the prespecified rules only: a participant is excluded when they have
no eyes-closed data or were removed as a duplicate (EXP-002). The audit (EXP-001) found nobody
else to exclude; the epoch-rejection stage (Phase 4) may still drop *epochs*, never people.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from eegconf.io import get_loader

ROOT = Path(__file__).resolve().parents[1]


def main():
    cfgs = yaml.safe_load(open(ROOT / "configs/datasets.yaml"))
    frames = []
    for cohort, cfg in cfgs.items():
        if not cfg.get("use"):
            continue                                         # ADSZ: dropped (D-017)
        loader = get_loader(cohort)
        p = loader.load_participants(ROOT / cfg["raw_path"], cfg)
        p.insert(0, "cohort", cohort)
        p["global_id"] = cohort + "-" + p["participant_id"].astype(str)
        # Recording time per participant comes from the audit table written by scripts/01_audit.py.
        audit = pd.read_csv(ROOT / "data/metadata" / f"audit_{cohort}.csv", dtype={"participant_id": str})
        audit["participant_id"] = audit["participant_id"].str.zfill(2) if cohort == "APAVA" else audit["participant_id"]
        p = p.merge(audit[["participant_id", "n_segments", "duration_s"]], on="participant_id", how="left")
        p = p.rename(columns={"duration_s": "total_ec_seconds"})
        p["included"] = p["total_ec_seconds"].fillna(0) > 0
        p["exclusion_reason"] = np.where(p["included"], "", "no eyes-closed data")
        frames.append(p)

    df = pd.concat(frames, ignore_index=True)
    # Duplicates removed by the loader (ADFSU AD-41..44) are listed explicitly for the flow diagram.
    for pid in cfgs["ADFSU"].get("exclude_participants", []):
        df.loc[len(df)] = {"cohort": "ADFSU", "participant_id": pid, "global_id": f"ADFSU-{pid}", "diagnosis": "AD",
                           "included": False, "exclusion_reason": "duplicate of AD-40 (EXP-002)"}

    out = ROOT / "data/metadata/participants_all.csv"
    df.to_csv(out, index=False)

    inc = df[df["included"]]
    summary = inc.groupby(["cohort", "diagnosis"]).agg(
        n=("global_id", "count"),
        ec_seconds_min=("total_ec_seconds", "min"),
        ec_seconds_median=("total_ec_seconds", "median"),
        ec_seconds_max=("total_ec_seconds", "max"),
        age_mean=("age", "mean"), age_sd=("age", "std"),
        n_female=("sex", lambda s: int((s == "F").sum()) if s.notna().any() else np.nan),
    ).round(1).reset_index()
    summary.to_csv(ROOT / "results/tables/T01_cohort_summary.csv", index=False)
    print(summary.to_string(index=False))
    print(f"\nincluded: {len(inc)} participants ({(inc.diagnosis == 'AD').sum()} AD, {(inc.diagnosis == 'HC').sum()} HC); "
          f"excluded: {len(df) - len(inc)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

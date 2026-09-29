"""ADSZ vs ADFSU overlap check (WORKPLAN Phase 3, EXP-002).

    python scripts/02_overlap_check.py

Outputs
- data/metadata/overlap_adsz_adfsu.csv        one row per ADSZ file with its ADFSU match (participant-level, local)
- data/metadata/overlap_within_adfsu.csv      duplicated recordings inside ADFSU (local)
- results/tables/T02_overlap_summary.csv       counts only (safe to commit)
"""
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from eegconf import overlap
from eegconf.io.fsu import read_adfsu, read_adsz

ROOT = Path(__file__).resolve().parents[1]


def main():
    adfsu = list(read_adfsu(ROOT / "data/raw/ADFSU"))
    adsz = list(read_adsz(ROOT / "data/raw/ADSZ"))
    print(f"ADFSU recordings: {len(adfsu)}  ({Counter((r['diagnosis'], r['condition']) for r in adfsu)})")
    print(f"ADSZ files: {len(adsz)}  ({Counter((r['diagnosis'], r['condition']) for r in adsz)})")

    ex = overlap.exact_matches(adsz, adfsu)
    nr = overlap.near_matches(adsz, adfsu)
    rows = []
    for ra, (je, se, oe), (jn, sn, on) in zip(adsz, ex, nr):
        j, off = (je, oe) if se >= overlap.MIN_CHANNEL_SHARE else ((jn, on) if sn >= overlap.MIN_CHANNEL_SHARE else (None, None))
        rb = adfsu[j] if j is not None else {}
        rows.append({
            "adsz_file": ra["recording"], "adsz_participant": ra["participant_id"], "adsz_segment": ra.get("segment"),
            "adsz_diagnosis": ra["diagnosis"], "adsz_condition": ra["condition"],
            "adsz_samples": ra["data"].shape[1], "match_offset_samples": off,
            "exact_share": round(se, 3), "near_share": round(sn, 3),
            "adfsu_recording": rb.get("recording"), "adfsu_participant": rb.get("participant_id"),
            "adfsu_diagnosis": rb.get("diagnosis"), "adfsu_condition": rb.get("condition"),
        })
    df = pd.DataFrame(rows)
    matched = df["adfsu_recording"].notna()
    df["label_agrees"] = (df["adsz_diagnosis"] == df["adfsu_diagnosis"]) & matched
    df["condition_agrees"] = (df["adsz_condition"] == df["adfsu_condition"]) & matched

    # Channel mapping for the first matched file (ADSZ columns have no names)
    if matched.any():
        i = int(np.flatnonzero(matched)[0])
        j = next(k for k, r in enumerate(adfsu) if r["recording"] == df.loc[i, "adfsu_recording"])
        cmap = overlap.channel_map(adsz[i], adfsu[j], int(df.loc[i, "match_offset_samples"]))
        print("\nADSZ column -> ADFSU channel (first matched file):")
        print("  " + ", ".join(f"{a}={b} (r={r:.4f})" for a, b, r in cmap))

    # Duplicates inside ADFSU (same signal under two IDs)
    hashes = [{overlap.channel_hash(c) for c in r["data"]} for r in adfsu]
    dup_rows = []
    for i in range(len(adfsu)):
        for j in range(i + 1, len(adfsu)):
            shared = len(hashes[i] & hashes[j])
            if shared >= overlap.MIN_CHANNEL_SHARE * len(adfsu[i]["data"]):
                dup_rows.append((adfsu[i]["recording"], adfsu[j]["recording"], shared))
    dups = pd.DataFrame(dup_rows, columns=["recording_a", "recording_b", "shared_channels"])

    meta = ROOT / "data/metadata"
    meta.mkdir(parents=True, exist_ok=True)
    df.to_csv(meta / "overlap_adsz_adfsu.csv", index=False)
    dups.to_csv(meta / "overlap_within_adfsu.csv", index=False)

    per_person = df[matched].groupby("adsz_participant")["adfsu_participant"].nunique()
    summary = {
        "adsz_files": len(df),
        "adsz_files_matched_in_adfsu": int(matched.sum()),
        "adsz_files_matched_exactly": int((df["exact_share"] >= overlap.MIN_CHANNEL_SHARE).sum()),
        "adsz_participants": df["adsz_participant"].nunique(),
        "adsz_participants_all_files_matched": int(df.groupby("adsz_participant")["adfsu_recording"].apply(lambda s: s.notna().all()).sum()),
        "adfsu_participants_hit": df.loc[matched, "adfsu_participant"].nunique(),
        "adsz_codes_mapping_to_more_than_one_adfsu_person": int((per_person > 1).sum()),
        "label_disagreements": int((matched & ~df["label_agrees"]).sum()),
        "condition_disagreements": int((matched & ~df["condition_agrees"]).sum()),
        "adfsu_within_duplicate_pairs": len(dups),
    }
    out = ROOT / "results/tables/T02_overlap_summary.csv"
    pd.DataFrame([summary]).T.rename(columns={0: "value"}).to_csv(out)
    print("\n" + "\n".join(f"{k}: {v}" for k, v in summary.items()))


if __name__ == "__main__":
    main()

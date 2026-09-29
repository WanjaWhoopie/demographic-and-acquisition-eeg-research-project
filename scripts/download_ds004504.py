"""Download the parts of OpenNeuro ds004504 this project uses (WORKPLAN T2.1.2).

Reads the public OpenNeuro S3 bucket over HTTPS, so no account, API key or AWS CLI is needed.
It keeps only the top-level BIDS files and the raw recordings of AD (Group A) and
healthy-control (Group C) participants, skipping FTD participants and derivatives/.
That is about 2.2 GB instead of about 5.8 GB.

    python scripts/download_ds004504.py              # download
    python scripts/download_ds004504.py --dry-run    # list files and total size only

Re-running skips files already present with the right size. A manifest with a sha256
per file is written to data/raw/ds004504/MANIFEST.tsv.
"""
import argparse
import csv
import hashlib
import io
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BUCKET = "https://s3.amazonaws.com/openneuro.org"
DATASET = "ds004504"
GROUPS = {"A", "C"}


def list_keys(prefix):
    keys, token = [], None
    while True:
        url = f"{BUCKET}?list-type=2&prefix={prefix}&max-keys=1000"
        if token:
            url += "&continuation-token=" + urllib.parse.quote(token)
        xml = urllib.request.urlopen(url).read().decode()
        keys += [(k, int(s)) for k, s in re.findall(r"<Key>(.*?)</Key>.*?<Size>(\d+)</Size>", xml)]
        m = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", xml)
        if not m:
            return keys
        token = m.group(1)


def wanted_subjects():
    tsv = urllib.request.urlopen(f"{BUCKET}/{DATASET}/participants.tsv").read().decode()
    rows = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    return {r["participant_id"] for r in rows if r["Group"] in GROUPS}


def keep(key, subjects):
    parts = key.split("/")[1:]
    if not parts or parts[0] == "derivatives":
        return False
    if parts[0].startswith("sub-"):
        return parts[0] in subjects
    return len(parts) == 1  # top-level files: participants.tsv, dataset_description.json, ...


def fetch(url, out, attempts=6):
    """Download to a .part file and rename, retrying with backoff on dropped connections."""
    part = out.with_name(out.name + ".part")
    for attempt in range(1, attempts + 1):
        try:
            urllib.request.urlretrieve(url, part)
            part.replace(out)
            return
        except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
            wait = 5 * 2 ** (attempt - 1)
            print(f"  attempt {attempt} failed ({err}); retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"giving up on {url}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=f"data/raw/{DATASET}")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    subjects = wanted_subjects()
    files = [(k, s) for k, s in list_keys(f"{DATASET}/") if keep(k, subjects)]
    print(f"{len(subjects)} participants, {len(files)} files, {sum(s for _, s in files) / 1e9:.2f} GB")
    if args.dry_run:
        return

    target = Path(args.target)
    manifest = []
    for i, (key, size) in enumerate(files, 1):
        out = target / key.split("/", 1)[1]
        if not (out.exists() and out.stat().st_size == size):
            out.parent.mkdir(parents=True, exist_ok=True)
            print(f"[{i}/{len(files)}] {key}")
            fetch(f"{BUCKET}/{urllib.parse.quote(key)}", out)
        assert out.stat().st_size == size, f"size mismatch: {out}"
        manifest.append((out.relative_to(target).as_posix(), size, sha256(out)))

    with open(target / "MANIFEST.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["file", "bytes", "sha256"])
        w.writerows(manifest)
    print("done; manifest written")


if __name__ == "__main__":
    main()

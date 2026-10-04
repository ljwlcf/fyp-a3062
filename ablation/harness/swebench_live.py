"""Prepare a SWE-bench-Live split (arXiv:2505.23419) for the localization pipeline.

Downloads one split at a pinned dataset revision, keeps only instances created after a cutoff
(issues the backbone cannot have seen in training) whose gold patch touches at least one .py
file (the graph is built with Python's ast), and writes, under data/swebench_live/:
  <name>.json      instance records (instance_id, repo, base_commit, problem_statement,
                   golden_patch, created_at, difficulty, ...), for config `dataset_file:`
  <name>.ids.txt   one instance id per line, for config `instances_file:`
  <name>.meta.json dataset, revision, split, filters and counts
Data stays out of git (data/ is ignored); the meta file and the config record the revision so
the set can be rebuilt exactly.

Usage:
  python ablation/harness/swebench_live.py --split verified --revision <sha> \\
      --created-after 2024-09-19 [--name live_verified_after_2024-09-19]
"""
import argparse
import io
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET = "SWE-bench-Live/SWE-bench-Live"
SPLIT_FILES = {"verified": ["data/verified-00000-of-00001.parquet"],
               "lite": ["data/lite-00000-of-00001.parquet"],
               "test": ["data/test-00000-of-00001.parquet"],
               "full": ["data/full-00000-of-00002.parquet", "data/full-00001-of-00002.parquet"]}
KEEP = ["instance_id", "repo", "base_commit", "problem_statement", "patch", "created_at",
        "difficulty", "pull_number", "issue_numbers", "FAIL_TO_PASS", "PASS_TO_PASS"]


def read_split(split, revision):
    import pyarrow.parquet as pq
    rows = []
    for path in SPLIT_FILES[split]:
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{revision}/{path}"
        with urllib.request.urlopen(url, timeout=120) as resp:
            table = pq.read_table(io.BytesIO(resp.read()))
        rows.extend(table.to_pylist())
    return rows


def patch_files(patch):
    return sorted(set(re.findall(r"^diff --git a/(\S+) b/", patch or "", re.M)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", choices=sorted(SPLIT_FILES), default="verified")
    ap.add_argument("--revision", required=True, help="dataset commit sha (pin it)")
    ap.add_argument("--created-after", required=True,
                    help="keep instances created after 00:00 of this date (YYYY-MM-DD), e.g. the "
                         "backbone's training cutoff or release date")
    ap.add_argument("--name", help="output base name (default live_<split>_after_<date>)")
    args = ap.parse_args()

    cutoff = datetime.fromisoformat(args.created_after)
    rows = read_split(args.split, args.revision)
    counts = Counter(total=len(rows))
    kept, seen = [], set()
    for r in rows:
        if r["instance_id"] in seen:          # the split itself lists conan-io__conan-18153 twice
            counts["dropped_duplicate"] += 1
            continue
        seen.add(r["instance_id"])
        c = r["created_at"]   # pyarrow may give a datetime or a string
        created = c.replace(tzinfo=None) if isinstance(c, datetime) else \
            datetime.fromisoformat(str(c).replace("Z", ""))
        r["created_at"] = created.isoformat()
        if created <= cutoff:
            counts["dropped_created_before_cutoff"] += 1
            continue
        files = patch_files(r["patch"])
        if not any(f.endswith(".py") for f in files):
            counts["dropped_no_python_in_gold_patch"] += 1
            continue
        rec = {k: r.get(k) for k in KEEP}
        rec["golden_patch"] = rec.pop("patch")   # the field name the pipeline tooling uses
        rec["gold_files"] = files
        kept.append(rec)
    counts["kept"] = len(kept)

    name = args.name or f"live_{args.split}_after_{args.created_after}"
    out_dir = os.path.join(ROOT, "data", "swebench_live")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{name}.json"), "w") as f:
        json.dump(kept, f)
    with open(os.path.join(out_dir, f"{name}.ids.txt"), "w") as f:
        f.writelines(r["instance_id"] + "\n" for r in kept)
    meta = {"dataset": DATASET, "revision": args.revision, "split": args.split,
            "created_after": args.created_after, "filters": ["duplicate instance_id dropped",
                                                             "created_at > created_after",
                                                             "gold patch touches a .py file"],
            "counts": dict(counts),
            "repos": dict(Counter(r["repo"] for r in kept).most_common()),
            "created_range": [min((r["created_at"] for r in kept), default=None),
                              max((r["created_at"] for r in kept), default=None)],
            "built": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with open(os.path.join(out_dir, f"{name}.meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    sys.exit(main())

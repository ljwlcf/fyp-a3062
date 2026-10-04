"""Pre-build the FULL dependency graphs a localization config needs, before any GPU job.

The pipeline builds a missing graph itself (repo_ops.set_current_issue: clone, then
build_graph(repo_dir, global_import=True)), but inside a GPU job that leaves the GPU idle
for minutes per instance (a sympy graph takes ~7 min). This does the same build on CPU:
one clone per repository, checked out at each instance's base commit, the same builder
call, pickled to the config's graph_index_dir as <instance_id>.pkl. Unlike RQ1's caches,
nothing is stripped: the pipeline needs each node's code.

Usage:
    python ablation/harness/build_full_graphs.py ablation/configs/<config>.yaml
"""
import json
import os
import pickle
import subprocess
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_localization import ROOT, FORK, instance_ids  # noqa: E402
from swe_graph import checkout, repo_dir  # noqa: E402

sys.path.insert(0, os.path.join(FORK, "localization"))
from dependency_graph.build_graph import build_graph  # noqa: E402

from instances import load_records  # noqa: E402  (default: the fork's SWE-bench Verified records)


def main(cfg_path):
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    out_dir = os.path.join(ROOT, cfg["paths"]["graph_index_dir"])
    repos_root = os.path.join(ROOT, "data", "repos")
    os.makedirs(out_dir, exist_ok=True)
    meta = load_records(cfg)

    ids = instance_ids(cfg)
    failures = {}
    for i, iid in enumerate(ids, 1):
        dest = os.path.join(out_dir, f"{iid}.pkl")
        if os.path.exists(dest):
            print(f"[{i}/{len(ids)}] {iid}: cached", flush=True)
            continue
        inst = meta[iid]
        path = repo_dir(repos_root, inst["repo"])
        try:
            if not os.path.exists(os.path.join(path, ".git")):
                subprocess.run(["git", "clone", "-q", f"https://github.com/{inst['repo']}.git", path],
                               check=True)
            try:
                checkout(path, inst["base_commit"])
            except subprocess.CalledProcessError:
                # Base commit not reachable from the cloned branches (e.g. only on a PR ref, or
                # history rewritten): GitHub serves a commit by sha, so fetch it and retry.
                subprocess.run(["git", "-C", path, "fetch", "-q", "origin", inst["base_commit"]],
                               check=True)
                checkout(path, inst["base_commit"])
        except subprocess.CalledProcessError as e:
            # One unbuildable instance must not abort the rest; it is recorded and skipped.
            failures[iid] = f"{inst['repo']} @ {inst['base_commit']}: {e}"
            print(f"[{i}/{len(ids)}] {iid}: FAILED (repo/commit unavailable), skipped", flush=True)
            continue
        t0 = time.time()
        G = build_graph(path, global_import=True)   # exactly repo_ops' call
        with open(dest, "wb") as f:
            pickle.dump(G, f)
        print(f"[{i}/{len(ids)}] {iid}: {G.number_of_nodes()} nodes, "
              f"{G.number_of_edges()} edges, {time.time() - t0:.0f} s", flush=True)
    if failures:
        path = os.path.join(out_dir, "build_failures.json")
        old_f = json.load(open(path)) if os.path.exists(path) else {}
        old_f.update(failures)
        with open(path, "w") as f:
            json.dump(old_f, f, indent=2)
        print(f"{len(failures)} instance(s) could not be built; listed in {path}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

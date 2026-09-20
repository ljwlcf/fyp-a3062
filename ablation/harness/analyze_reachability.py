"""Summarise the RQ1 raw records into the numbers that go in notes/results.md.

Reads every raw.*.jsonl under a run's results directory and writes summary.json
alongside a markdown table on stdout. Analysis is kept separate from the run so the
raw records stay the record of truth.

Usage: python ablation/harness/analyze_reachability.py --run ablation/results/rq1_reachability_v1
"""

import argparse
import glob
import json
import os.path as osp
from collections import Counter, defaultdict


def pct(n, d):
    return f"{100.0 * n / d:5.1f}%" if d else "    -"


def load(run_dir):
    recs = []
    for path in sorted(glob.glob(osp.join(run_dir, "raw.*.jsonl"))):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
    return recs


def cdf_row(values, budgets, total):
    """Share of instances whose value is <= each budget (None counts as unreached)."""
    return [sum(1 for v in values if v is not None and v <= b) for b in budgets]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()

    recs = load(args.run)
    errors = [r for r in recs if "error" in r]
    ok = [r for r in recs if "error" not in r]
    n = len(ok)
    budgets = [0, 1, 2, 3, 4, 5, 6]

    print(f"# RQ1 reachability — {osp.basename(args.run)}")
    print(f"\n{n} instances measured, {len(errors)} failed.")
    if errors:
        for e in errors:
            print(f"  - {e['instance_id']}: {e['error']}")

    by_repo = Counter(r["repo"] for r in ok)
    print("\nBy repository: " + ", ".join(f"{k} {v}" for k, v in sorted(by_repo.items())))

    # ---- ceiling A: is the gold location in the graph at all? -------------
    print("\n## Ceiling A — gold location present in the graph\n")
    a = {
        "all gold files are Python": sum(
            1 for r in ok if r["gold_summary"]["n_non_python_files"] == 0),
        "all gold files are graph nodes": sum(
            1 for r in ok if r["gold_summary"]["n_files_missing_from_graph"] == 0),
        "no gold file hidden by the test-name filter": sum(
            1 for r in ok if r["gold_summary"]["n_files_hidden_by_test_filter"] == 0),
        "every changed line sits inside a class/function node": sum(
            1 for r in ok if all(g["lines_outside_any_entity"] == 0
                                 for g in r["gold_files"].values())),
        "at least one gold entity node found": sum(
            1 for r in ok if r["gold_summary"]["n_entity_nodes"] > 0),
    }
    print("| check | instances | share |")
    print("|---|---:|---:|")
    for k, v in a.items():
        print(f"| {k} | {v}/{n} | {pct(v, n)} |")

    # ---- entry set --------------------------------------------------------
    entry_sizes = sorted(r["entry_set"]["n_nodes"] for r in ok)
    named_file = sum(1 for r in ok if r["entry_set"]["gold_file_named_directly"])
    named_ent = sum(1 for r in ok if r["entry_set"]["gold_entity_named_directly"])
    med = entry_sizes[n // 2] if n else 0
    print(f"\n## Entry set (issue-named entities)\n")
    print(f"Size: median {med}, min {entry_sizes[0] if n else 0}, "
          f"max {entry_sizes[-1] if n else 0}.")
    print(f"Gold FILE named directly in the issue: {named_file}/{n} ({pct(named_file, n)}).")
    print(f"Gold ENTITY named directly in the issue: {named_ent}/{n} ({pct(named_ent, n)}).")

    # ---- the control: how much of the repository is within k hops anyway --
    policies = [p for p in ("all", "no_dir", "dep_only") if ok and p in ok[0]["reach"]]
    print("\n## Control — share of the repository already within k hops of the entry set\n")
    print("Mean over instances. Read every reachability number below against this row: a "
          "graph\nthat puts most of the repository inside three hops makes reaching the gold "
          "file easy\nfor reasons that have nothing to do with localization.\n")
    print("| policy | target | " + " | ".join(f"k={b}" for b in budgets) + " |")
    print("|---|---|" + "---:|" * len(budgets))
    control = {}
    for p in policies:
        for t in ("files", "entities"):
            means = []
            for b in budgets:
                vals = [r["reach"][p]["coverage"][t]["within_k"].get(str(b),
                        r["reach"][p]["coverage"][t]["within_k"].get(b, 0))
                        / max(r["reach"][p]["coverage"][t]["pool"], 1) for r in ok]
                means.append(sum(vals) / len(vals) if vals else 0.0)
            control[(p, t)] = means
            print(f"| {p} | {t} | " + " | ".join(f"{m*100:5.1f}%" for m in means) + " |")

    # ---- ceiling B/C: reachability ---------------------------------------
    for target, label in (("files", "gold FILE"), ("entities", "gold ENTITY")):
        print(f"\n## Reachability of the {label} within k hops of an issue-named entity\n")
        print("| policy | " + " | ".join(f"k={b}" for b in budgets) + " | unreachable |")
        print("|---|" + "---:|" * (len(budgets) + 1))
        for p in policies:
            vals_any = [r["reach"][p][target]["min_hops"] for r in ok]
            counts = cdf_row(vals_any, budgets, n)
            unreached = sum(1 for v in vals_any if v is None)
            print(f"| {p} (nearest) | " +
                  " | ".join(pct(c, n) for c in counts) + f" | {unreached} |")
        # all-targets variant matters only where a patch spans several locations
        for p in policies:
            vals_all = [r["reach"][p][target]["max_hops"]
                        if r["reach"][p][target]["all_reached"] else None for r in ok]
            counts = cdf_row(vals_all, budgets, n)
            unreached = sum(1 for v in vals_all if v is None)
            print(f"| {p} (all targets) | " +
                  " | ".join(pct(c, n) for c in counts) + f" | {unreached} |")
        for p in policies:
            print(f"| _{p} control_ | " +
                  " | ".join(f"_{m*100:.1f}%_" for m in control[(p, target)]) + " | |")

    # ---- enrichment over the control -------------------------------------
    print("\n## Enrichment — gold reachability divided by the control\n")
    print("How much more likely the gold node is to be inside k hops than an arbitrary node\n"
          "of the same kind. 1.0 means the traversal carries no information at that budget.\n")
    print("| policy | target | " + " | ".join(f"k={b}" for b in budgets) + " |")
    print("|---|---|" + "---:|" * len(budgets))
    enrichment = {}
    for p in policies:
        for t in ("files", "entities"):
            counts = cdf_row([r["reach"][p][t]["min_hops"] for r in ok], budgets, n)
            row = []
            for c, m in zip(counts, control[(p, t)]):
                row.append((c / n) / m if m > 0 else None)
            enrichment[f"{p}|{t}"] = row
            print(f"| {p} | {t} | " +
                  " | ".join("  -  " if v is None else f"{v:5.1f}x" for v in row) + " |")

    # ---- multi-file -------------------------------------------------------
    multi = [r for r in ok if r["gold_summary"]["n_files"] > 1]
    print(f"\n## Multi-file instances ({len(multi)}/{n})\n")
    if multi:
        for p in policies:
            allr = sum(1 for r in multi if r["reach"][p]["files"]["all_reached"])
            print(f"- {p}: every gold file reachable within 6 hops in "
                  f"{allr}/{len(multi)} ({pct(allr, len(multi))})")

    # ---- graph shape ------------------------------------------------------
    print("\n## Graph shape (means over instances)\n")
    agg = defaultdict(float)
    etypes = Counter()
    for r in ok:
        g = r["graph"]
        agg["nodes"] += g["nodes"]
        agg["edges"] += g["edges"]
        agg["hidden_by_test_filter"] += g["nodes_hidden_by_test_filter"]
        agg["orphan_file_nodes"] += g["orphan_file_nodes"]
        for k, v in g["edge_types"].items():
            etypes[k] += v
    print("| repo | nodes | edges | hidden by test filter | orphan file nodes |")
    print("|---|---:|---:|---:|---:|")
    for repo in sorted(by_repo):
        rs = [r for r in ok if r["repo"] == repo]
        m = len(rs)
        print(f"| {repo} | {sum(r['graph']['nodes'] for r in rs) // m:,} | "
              f"{sum(r['graph']['edges'] for r in rs) // m:,} | "
              f"{sum(r['graph']['nodes_hidden_by_test_filter'] for r in rs) // m:,} | "
              f"{sum(r['graph']['orphan_file_nodes'] for r in rs) / m:.1f} |")
    tot = sum(etypes.values())
    print("\nEdge mix: " + ", ".join(f"{k} {pct(v, tot).strip()}" for k, v in etypes.most_common()))

    summary = {
        "run": osp.basename(args.run),
        "n_instances": n,
        "n_errors": len(errors),
        "by_repo": dict(by_repo),
        "ceiling_a": {k: [v, n] for k, v in a.items()},
        "entry_set": {"median": med, "min": entry_sizes[0] if n else 0,
                      "max": entry_sizes[-1] if n else 0,
                      "gold_file_named_directly": named_file,
                      "gold_entity_named_directly": named_ent},
        "reach": {
            t: {p: {
                "nearest_cdf": dict(zip(
                    budgets, cdf_row([r["reach"][p][t]["min_hops"] for r in ok], budgets, n))),
                "all_targets_cdf": dict(zip(
                    budgets, cdf_row([r["reach"][p][t]["max_hops"]
                                      if r["reach"][p][t]["all_reached"] else None
                                      for r in ok], budgets, n))),
            } for p in policies} for t in ("files", "entities")
        },
        "edge_mix": dict(etypes),
        "coverage_control": {f"{p}|{t}": control[(p, t)] for (p, t) in control},
        "enrichment": enrichment,
    }
    out = osp.join(args.run, "summary.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()

"""Two structural properties of SWE-Debate's graph that bound what any traversal can do.

1. How much of it is name matching rather than resolved dependency.
2. How much production code the test-name filter hides from the traversal.

build_graph() never resolves a call to a single target. It matches the called name against
the caller's visible scope and, with fuzzy_search on, keeps EVERY node sharing that short
name; if the name is not visible at all and global_import is on (which is what
batch_build_graph.py uses), it falls back to `global_name_dict` and wires the caller to
every node in the whole repository with that name. Either way one call site can produce
many `invokes` edges, and at most one of them is the real callee.

This script reads the cached graphs and measures that ambiguity: group the `invokes` edges
by (source node, callee short name), and any group larger than one is a name match that
was never resolved. The split between the local-fuzzy and the global branch is not
recoverable from the finished graph — both are counted together here.

`is_test_file` splits a path on '/', '_' and ' ' and drops it if ANY word starts with
"test". That is meant to remove the repository's own test suite, but it also removes
shipped packages whose names merely begin with "test" — django/test/ (django.test.Client,
TestCase, the whole testing framework users import) and sphinx/testing/. Those files are
in the graph and can never be visited, because every get_neighbors call in the pipeline
passes ignore_test_file=True.

Usage: python ablation/harness/graph_quality.py --graphs data/graphs [--limit N]
"""

import argparse
import glob
import json
import os.path as osp
import pickle
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, osp.dirname(osp.abspath(__file__)))
from swe_graph import is_test_file  # noqa: E402


def short_name(nid: str) -> str:
    return nid.split(":")[-1].split(".")[-1]


def measure(G) -> dict:
    groups = defaultdict(list)          # (source, callee short name) -> [targets]
    n_invokes = 0
    for u, v, data in G.edges(data=True):
        if data["type"] != "invokes":
            continue
        n_invokes += 1
        groups[(u, short_name(v))].append(v)

    ambiguous = {k: v for k, v in groups.items() if len(v) > 1}
    edges_in_ambiguous = sum(len(v) for v in ambiguous.values())
    sizes = sorted(len(v) for v in ambiguous.values())

    # ambiguity of the repository's own name space, independent of any edge
    name_counts = Counter(short_name(n) for n in G.nodes() if ":" in n)
    ambiguous_names = sum(1 for c in name_counts.values() if c > 1)

    # what the test-name filter hides. A file under a TOP-LEVEL tests/ directory is the
    # repository's own suite and is meant to be hidden; anything else is production code
    # the traversal has been made blind to.
    files = [n for n, d in G.nodes(data=True) if d.get("type") == "file"]
    hidden = [f for f in files if is_test_file(f)]
    hidden_production = sorted(
        f for f in hidden if f.split("/")[0] not in ("tests", "test", "testing"))

    return {
        "nodes": G.number_of_nodes(),
        "invokes_edges": n_invokes,
        "invoke_groups": len(groups),
        "unresolved_groups": len(ambiguous),
        "edges_in_unresolved_groups": edges_in_ambiguous,
        "share_of_invokes_unresolved": (
            round(edges_in_ambiguous / n_invokes, 4) if n_invokes else None),
        "largest_group": sizes[-1] if sizes else 0,
        "median_group": statistics.median(sizes) if sizes else 0,
        "entity_names": len(name_counts),
        "ambiguous_entity_names": ambiguous_names,
        "share_of_names_ambiguous": (
            round(ambiguous_names / len(name_counts), 4) if name_counts else None),
        "file_nodes": len(files),
        "files_hidden_by_test_filter": len(hidden),
        "production_files_hidden_by_test_filter": len(hidden_production),
        "production_files_hidden_examples": hidden_production[:15],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphs", default="data/graphs")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default="ablation/results/rq1_reachability_v1/graph_quality.json")
    args = ap.parse_args()

    paths = sorted(glob.glob(osp.join(args.graphs, "*.pkl")))
    if args.limit:
        paths = paths[:args.limit]

    rows = []
    for p in paths:
        with open(p, "rb") as f:
            G = pickle.load(f)
        row = measure(G)
        row["instance_id"] = osp.basename(p)[:-4]
        row["repo"] = row["instance_id"].rsplit("-", 1)[0]
        rows.append(row)
        print(f"{row['instance_id']:32s} invokes={row['invokes_edges']:7,} "
              f"unresolved={row['share_of_invokes_unresolved']:.1%} "
              f"largest_group={row['largest_group']:4d} "
              f"ambiguous_names={row['share_of_names_ambiguous']:.1%} "
              f"prod_files_hidden={row['production_files_hidden_by_test_filter']}")

    print(f"\n{len(rows)} graphs")
    for repo in sorted({r["repo"] for r in rows}):
        rs = [r for r in rows if r["repo"] == repo]
        print(f"  {repo:24s} n={len(rs):3d} "
              f"mean share of invokes edges left unresolved = "
              f"{statistics.mean(r['share_of_invokes_unresolved'] for r in rs):.1%}; "
              f"mean share of entity names that are ambiguous = "
              f"{statistics.mean(r['share_of_names_ambiguous'] for r in rs):.1%}; "
              f"mean production files hidden by the test filter = "
              f"{statistics.mean(r['production_files_hidden_by_test_filter'] for r in rs):.1f}"
              f" of {statistics.mean(r['file_nodes'] for r in rs):.0f}")

    with open(args.out, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()

"""RQ1: the dependency graph's structural reachability ceiling.

For every instance, build SWE-Debate's dependency graph at the base commit, locate the
gold patch in it, and ask how far the gold location sits from the entities the issue
text names. No LLM and no GPU: this bounds what any traversal policy over this graph
could achieve, which is the ceiling every later localization number sits under.

Three edge policies are measured side by side:
  all       every node and edge type, exactly what _dfs_traversal walks
  no_dir    directory nodes removed (they are containment hubs, not dependencies)
  dep_only  imports / invokes / inherits only, no containment at all

Usage:
    python ablation/harness/reachability.py --config ablation/configs/<cfg>.yaml
    python ablation/harness/reachability.py --config <cfg> --repo django/django
"""

import argparse
import hashlib
import json
import os
import os.path as osp
import subprocess
import sys
import time
from collections import Counter, deque
from typing import Dict, List, Optional, Set

import yaml

sys.path.insert(0, osp.dirname(osp.abspath(__file__)))

import swe_graph as sg

POLICIES = {
    # faithful to _dfs_traversal: it filters neighbours by edge type but not by node
    # type, so directory nodes are traversable and the containment tree is a hub
    "all": {"drop_directories": False, "edge_types": None, "drop_ambiguous_invokes": False},
    "no_dir": {"drop_directories": True, "edge_types": None,
               "drop_ambiguous_invokes": False},
    "dep_only": {"drop_directories": True,
                 "edge_types": {"imports", "invokes", "inherits"},
                 "drop_ambiguous_invokes": False},
    # invokes edges are ~80% unresolved name matches (see graph_quality.py), so these two
    # views ask what the graph connects through structure it actually got right
    "no_invokes": {"drop_directories": True,
                   "edge_types": {"contains", "imports", "inherits"},
                   "drop_ambiguous_invokes": False},
    "resolved_only": {"drop_directories": True, "edge_types": None,
                      "drop_ambiguous_invokes": True},
}


def build_adjacency(G, drop_directories: bool, edge_types: Optional[Set[str]],
                    drop_ambiguous_invokes: bool = False):
    """Undirected adjacency over traversable nodes.

    Test files are dropped because RepoDependencySearcher.get_neighbors is called with
    ignore_test_file=True everywhere in the pipeline; the traversal cannot see them.

    drop_ambiguous_invokes keeps only those invokes edges whose (source, callee short
    name) group has exactly one target. build_graph never resolves a call to one callee:
    it keeps every node sharing the name, so a group larger than one is a name match, and
    at most one member of it is the real dependency. Dropping those leaves the edges the
    builder did resolve.
    """
    allowed = set()
    for nid, data in G.nodes(data=True):
        if sg.is_test_file(nid):
            continue
        if drop_directories and data.get("type") == sg.NODE_TYPE_DIRECTORY:
            continue
        allowed.add(nid)

    ambiguous = set()
    if drop_ambiguous_invokes:
        groups: Dict[tuple, list] = {}
        for u, v, data in G.edges(data=True):
            if data["type"] != "invokes":
                continue
            groups.setdefault((u, v.split(":")[-1].split(".")[-1]), []).append(v)
        for (u, name), targets in groups.items():
            if len(targets) > 1:
                ambiguous.update((u, t) for t in targets)

    adj: Dict[str, Set[str]] = {n: set() for n in allowed}
    for u, v, data in G.edges(data=True):
        if u not in adj or v not in adj:
            continue
        if edge_types is not None and data["type"] not in edge_types:
            continue
        if data["type"] == "invokes" and (u, v) in ambiguous:
            continue
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs_distances(adj, sources: Set[str], max_hops: int) -> Dict[str, int]:
    """Multi-source BFS over the whole view, out to max_hops.

    Every node's distance is kept, not just the gold ones: the share of the repository
    that falls inside k hops is the control the gold numbers have to be read against. In
    a graph dense enough to put most of the repository three hops from anything, "the
    gold file is reachable in three hops" says nothing about the graph.
    """
    dist: Dict[str, int] = {}
    frontier = deque()
    for s in sources:
        if s in adj:
            dist[s] = 0
            frontier.append((s, 0))

    while frontier:
        node, d = frontier.popleft()
        if d >= max_hops:
            continue
        for nb in adj[node]:
            if nb not in dist:
                dist[nb] = d + 1
                frontier.append((nb, d + 1))
    return dist


def summarise_targets(distances: Dict[str, int], targets: Set[str]) -> dict:
    if not targets:
        return {"n_targets": 0, "n_reached": 0, "min_hops": None, "max_hops": None,
                "all_reached": None}
    reached = [distances[t] for t in targets if t in distances]
    return {
        "n_targets": len(targets),
        "n_reached": len(reached),
        "min_hops": min(reached) if reached else None,
        "max_hops": max(reached) if reached else None,
        "all_reached": len(reached) == len(targets),
    }


def measure_instance(instance: dict, cfg: dict) -> dict:
    t0 = time.time()
    rec = {"instance_id": instance["instance_id"], "repo": instance["repo"],
           "base_commit": instance["base_commit"],
           "difficulty": instance.get("difficulty")}

    G, cached = sg.build_or_load_graph(
        instance,
        repos_root=cfg["paths"]["repos_root"],
        cache_dir=cfg["paths"]["graph_cache"],
        global_import=cfg["graph"]["global_import"],
        fuzzy_search=cfg["graph"]["fuzzy_search"],
    )
    rec["graph_from_cache"] = cached
    rec["graph_build_seconds"] = round(time.time() - t0, 1)

    type_counts = Counter(d.get("type") for _, d in G.nodes(data=True))
    edge_counts = Counter(d["type"] for _, _, d in G.edges(data=True))
    n_test_nodes = sum(1 for n in G.nodes() if sg.is_test_file(n))
    rec["graph"] = {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "node_types": dict(type_counts),
        "edge_types": dict(edge_counts),
        "nodes_hidden_by_test_filter": n_test_nodes,
        "orphan_file_nodes": len(sg.orphan_file_nodes(G)),
    }

    # --- gold locations -------------------------------------------------
    patch_files = sg.parse_patch(instance["patch"])
    gold = sg.gold_nodes(G, patch_files)
    rec["gold_files"] = gold

    gold_file_nodes = {p for p, g in gold.items()
                       if g["file_node_in_graph"] and not g["excluded_by_test_filter"]}
    gold_entity_nodes = set()
    for p, g in gold.items():
        if not g["excluded_by_test_filter"]:
            gold_entity_nodes.update(g["entity_nodes"])

    rec["gold_summary"] = {
        "n_files": len(gold),
        "n_python_files": sum(1 for g in gold.values() if g["is_python"]),
        "n_non_python_files": sum(1 for g in gold.values() if not g["is_python"]),
        "n_new_files": sum(1 for g in gold.values() if g["new_file"]),
        "n_files_missing_from_graph": sum(
            1 for g in gold.values() if g["is_python"] and not g["file_node_in_graph"]),
        "n_files_hidden_by_test_filter": sum(
            1 for g in gold.values() if g["excluded_by_test_filter"]),
        "all_python_files_present": all(
            g["file_node_in_graph"] and not g["excluded_by_test_filter"]
            for g in gold.values() if g["is_python"]),
        "n_entity_nodes": len(gold_entity_nodes),
    }

    # --- entry set ------------------------------------------------------
    index = sg.name_index(G)
    entry_cfg = cfg["entry_set"]
    entry, matched = sg.issue_entry_nodes(
        G, instance["problem_statement"], index,
        min_name_len=entry_cfg["min_name_len"],
        max_nodes_per_name=entry_cfg.get("max_nodes_per_name"),
        use_stopwords=entry_cfg.get("use_stopwords", True),
    )
    rec["entry_set"] = {
        "method": entry_cfg["method"],
        "n_nodes": len(entry),
        "n_names_matched": len(matched),
        "gold_file_named_directly": sorted(gold_file_nodes & entry),
        "gold_entity_named_directly": sorted(gold_entity_nodes & entry),
    }

    # --- reachability ---------------------------------------------------
    max_hops = cfg["reach"]["max_hops"]
    rec["reach"] = {}
    ntype = {n: d.get("type") for n, d in G.nodes(data=True)}
    for name in cfg["reach"]["policies"]:
        pol = POLICIES[name]
        adj = build_adjacency(G, pol["drop_directories"], pol["edge_types"],
                              pol["drop_ambiguous_invokes"])
        dist = bfs_distances(adj, entry, max_hops)

        # control: how much of the repository is inside k hops anyway
        all_files = [n for n in adj if ntype.get(n) == sg.NODE_TYPE_FILE]
        all_ents = [n for n in adj if ntype.get(n) in sg.ENTITY_NODE_TYPES]
        cover = {}
        for label, pool in (("files", all_files), ("entities", all_ents)):
            hist = Counter(dist[n] for n in pool if n in dist)
            cum, running = {}, 0
            for k in range(max_hops + 1):
                running += hist.get(k, 0)
                cum[k] = running
            cover[label] = {"pool": len(pool), "within_k": cum}

        rec["reach"][name] = {
            "traversable_nodes": len(adj),
            "entry_nodes_in_view": len(entry & set(adj)),
            "files": summarise_targets(dist, gold_file_nodes),
            "entities": summarise_targets(dist, gold_entity_nodes),
            "coverage": cover,
            "file_hops": {t: dist[t] for t in sorted(gold_file_nodes) if t in dist},
        }

    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--repo", help="restrict to one repo, e.g. django/django")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--shard", help="split one repo across parallel workers, e.g. 1/2")
    ap.add_argument("--repos-root", help="override paths.repos_root, so a second worker "
                                         "can use its own git worktree of the same clone")
    args = ap.parse_args()

    with open(args.config) as f:
        raw_cfg = f.read()
    cfg = yaml.safe_load(raw_cfg)
    cfg_hash = hashlib.sha256(raw_cfg.encode()).hexdigest()[:12]

    root = sg.REPO_ROOT
    for key, val in cfg["paths"].items():
        if not osp.isabs(val):
            cfg["paths"][key] = osp.join(root, val)

    if args.repos_root:
        cfg["paths"]["repos_root"] = (args.repos_root if osp.isabs(args.repos_root)
                                      else osp.join(root, args.repos_root))

    instances = sg.load_instances(cfg["paths"]["dataset"], cfg["paths"]["instance_ids"])
    if args.repo:
        instances = [i for i in instances if i["repo"] == args.repo]
    shard_tag = ""
    if args.shard:
        idx, total = (int(x) for x in args.shard.split("/"))
        instances = [inst for j, inst in enumerate(instances) if j % total == idx - 1]
        shard_tag = f".shard{idx}of{total}"
    if args.limit:
        instances = instances[:args.limit]

    out_dir = cfg["paths"]["results"]
    os.makedirs(out_dir, exist_ok=True)
    suffix = (args.repo.replace("/", "__") if args.repo else "all") + shard_tag
    raw_path = osp.join(out_dir, f"raw.{suffix}.jsonl")

    # skip anything any shard of this run has already recorded, not just this file
    done = set()
    import glob as _glob
    for path in _glob.glob(osp.join(out_dir, "raw.*.jsonl")):
        with open(path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "error" not in rec:
                    done.add(rec["instance_id"])

    manifest = {
        "run": cfg["name"], "config": osp.relpath(osp.abspath(args.config), root),
        "config_sha256_12": cfg_hash,
        "graph_version": sg.GRAPH_VERSION,
        "code_commit": subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                                      capture_output=True, text=True).stdout.strip(),
        "swe_debate_commit": subprocess.run(
            ["git", "-C", osp.join(root, "swe-debate"), "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip(),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_instances": len(instances),
        "repo_filter": args.repo,
        "shard": args.shard,
    }
    with open(osp.join(out_dir, f"manifest.{suffix}.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    with open(raw_path, "a") as out:
        for i, inst in enumerate(instances, 1):
            if inst["instance_id"] in done:
                print(f"[{i}/{len(instances)}] {inst['instance_id']} already done")
                continue
            try:
                rec = measure_instance(inst, cfg)
            except Exception as e:  # keep going; a failure is itself a datum
                rec = {"instance_id": inst["instance_id"], "repo": inst["repo"],
                       "error": f"{type(e).__name__}: {e}"}
                print(f"[{i}/{len(instances)}] {inst['instance_id']} FAILED: {e}")
            out.write(json.dumps(rec) + "\n")
            out.flush()
            if "error" not in rec:
                r = rec["reach"].get("no_dir", {}).get("files", {})
                print(f"[{i}/{len(instances)}] {inst['instance_id']} "
                      f"{rec['seconds']}s entry={rec['entry_set']['n_nodes']} "
                      f"gold_files={rec['gold_summary']['n_files']} "
                      f"no_dir_reached={r.get('n_reached')}/{r.get('n_targets')} "
                      f"min_hops={r.get('min_hops')}")

    print(f"\nwrote {raw_path}")


if __name__ == "__main__":
    main()

# rq1_reachability_v2

Structural reachability ceiling of SWE-Debate's dependency graph, all 75
SWE-Bench-Verified-S instances. No LLM, no GPU. See `notes/results.md` 2026-09-20.

| file | what it is |
|---|---|
| `raw.<repo>[.shardNofM].jsonl` | one JSON record per instance — the record of truth |
| `manifest.<suffix>.json` | config hash, graph version, A3062 and fork commit SHAs |
| `summary.json` | everything `analyze_reachability.py` computes |
| `graph_quality.json` | per-instance edge-resolution and test-filter measurements |

sympy is split across five shard files because the run was parallelised across git
worktrees and the partition changed mid-run (2-way, then 3-way) after the graph builder was
made faster. The union is exactly 75 unique instances with no conflicting records;
`analyze_reachability.py` de-duplicates by `instance_id`.

Reproduce:

```bash
python ablation/harness/reachability.py --config ablation/configs/rq1_reachability_v2.yaml
python ablation/harness/analyze_reachability.py --run ablation/results/rq1_reachability_v2
python ablation/harness/graph_quality.py
```

The first command clones django, sympy and sphinx into `data/repos/` and builds a graph per
base commit into `data/graphs/` (~350 MB, ~10 CPU-hours; both directories are gitignored).
`--repo` and `--shard i/n` split the work, `--repos-root` points a worker at its own worktree.

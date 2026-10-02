"""Where instance data comes from, shared by the runner, the graph builder and the scorer.

Default (no `dataset_file` in the config): the moatless SWE-bench Verified records bundled with
the fork, i.e. exactly what the released workflow.py uses (get_moatless_instance).
With `dataset_file: <path>` (relative to the repo root): a prepared JSON list of instance records,
e.g. a SWE-bench-Live split written by ablation/harness/swebench_live.py, with at least
instance_id, repo, base_commit, problem_statement and golden_patch.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOATLESS = os.path.join(ROOT, "swe-debate", "moatless", "benchmark",
                        "swebench_verified_all_evaluations.json")


def dataset_file(cfg):
    path = (cfg or {}).get("dataset_file")
    return os.path.join(ROOT, path) if path else None


def load_records(cfg=None):
    """{instance_id: record} from the configured source (see module docstring)."""
    path = dataset_file(cfg) or MOATLESS
    with open(path) as f:
        return {r["instance_id"]: r for r in json.load(f)}


def get_instance(iid, cfg=None):
    """One instance record. Default source: the fork's own get_moatless_instance, unchanged."""
    if dataset_file(cfg) is None:
        from moatless.benchmark.utils import get_moatless_instance  # fork on sys.path
        return get_moatless_instance(instance_id=iid)
    records = load_records(cfg)
    if iid not in records:
        raise ValueError(f"{iid} not in {cfg['dataset_file']}")
    return records[iid]

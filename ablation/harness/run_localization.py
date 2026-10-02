"""Run SWE-Debate's localization stage on a list of instances and record every LLM call.

The call is the one workflow.py makes, unchanged:
    EntityLocalizationPipeline().run_pipeline(instance, "context", max_initial_entities=5)
Nothing inside the pipeline is modified. This script only adds what the pipeline lacks:
per-call token accounting (wrapped around the pipeline's own OpenAI client), a manifest, and
raw JSON output. Scoring is a separate step.

Usage (from the repo root, with the vLLM server already up):
    python ablation/harness/run_localization.py ablation/configs/smoke_localization_v1.yaml
"""
import argparse
import inspect
import json
import os
import platform
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FORK = os.path.join(ROOT, "swe-debate")
PIPELINE_FILE = "entity_localization_pipeline.py"


def git_sha(path):
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None


def _gpu_names():
    """GPU model(s) this job sees, for the manifest (comparisons must share one GPU model)."""
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                              capture_output=True, text=True, check=True).stdout.split("\n")[:-1]
    except Exception:
        return None


def served_model(base_url):
    """What the endpoint says it is serving, so the manifest records the real checkpoint."""
    try:
        from openai import OpenAI
        return [m.id for m in OpenAI(base_url=base_url, api_key="EMPTY").models.list().data]
    except Exception as e:
        return f"unreachable: {e!r}"


class CallLog:
    """Wraps client.chat.completions.create; one record per call, thread-safe (the five
    voting and debating agents run in a ThreadPoolExecutor)."""

    def __init__(self, client):
        self.records = []
        self._lock = threading.Lock()
        self._create = client.chat.completions.create
        client.chat.completions.create = self.create

    @staticmethod
    def _stage():
        # The pipeline method that made the call, e.g. _vote_on_chains. _call_llm_simple is
        # a pass-through helper, so skip it and report its caller.
        for f in inspect.stack()[2:]:
            if f.filename.endswith(PIPELINE_FILE) and f.function != "_call_llm_simple":
                return f.function
        return "unknown"

    def create(self, *args, **kwargs):
        rec = {"stage": self._stage(), "thread": threading.current_thread().name,
               "started": time.time(), "temperature": kwargs.get("temperature"),
               "max_tokens": kwargs.get("max_tokens"),
               "n_messages": len(kwargs.get("messages") or [])}
        try:
            resp = self._create(*args, **kwargs)
        except Exception as e:
            rec.update(seconds=time.time() - rec["started"], error=repr(e))
            with self._lock:
                self.records.append(rec)
            raise
        usage = getattr(resp, "usage", None)
        rec.update(seconds=time.time() - rec["started"],
                   prompt_tokens=getattr(usage, "prompt_tokens", None),
                   completion_tokens=getattr(usage, "completion_tokens", None),
                   finish_reason=resp.choices[0].finish_reason if resp.choices else None,
                   # kept so parse failures (the pipeline drops agents whose JSON fails a
                   # strict json.loads) can be inspected; ~100 KB per instance
                   response=resp.choices[0].message.content if resp.choices else None)
        with self._lock:
            self.records.append(rec)
        return resp

    def summary(self):
        by_stage = {}
        for r in self.records:
            s = by_stage.setdefault(r["stage"], {"calls": 0, "errors": 0, "prompt_tokens": 0,
                                                 "completion_tokens": 0, "truncated": 0})
            s["calls"] += 1
            s["errors"] += "error" in r
            s["prompt_tokens"] += r.get("prompt_tokens") or 0
            s["completion_tokens"] += r.get("completion_tokens") or 0
            s["truncated"] += r.get("finish_reason") == "length"
        total = {k: sum(s[k] for s in by_stage.values())
                 for k in ("calls", "errors", "prompt_tokens", "completion_tokens", "truncated")}
        return {"total": total, "by_stage": by_stage}


def _init_worker():
    """Make the fork importable in this process. The pipeline keeps the current issue in
    module-level globals (repo_ops.CURRENT_ISSUE_ID, DP_GRAPH, ...), so instances run in
    parallel must be separate processes, never threads."""
    for p in (FORK, os.path.join(FORK, "localization")):
        if p not in sys.path:
            sys.path.insert(0, p)


def run_one(iid, keep_fields, pipe):
    """Run the pipeline on one instance; return the raw record. Runs in a worker process."""
    _init_worker()
    from moatless.benchmark.utils import get_moatless_instance
    from entity_localization_pipeline import EntityLocalizationPipeline
    import entity_localization_pipeline as elp
    getattr(elp, "A3062_PARSE_STATS", {}).clear()  # per instance, also when workers == 1

    full = get_moatless_instance(instance_id=iid)
    instance = {k: full[k] for k in keep_fields}
    pipeline = EntityLocalizationPipeline(max_depth=pipe["max_depth"])
    calls = CallLog(pipeline.client)
    order = apply_chain_order(pipeline, iid, pipe.get("chain_order") or {"mode": "fixed"})
    t0 = time.time()
    rec = {"instance_id": iid, "pid": os.getpid()}
    try:
        rec["output"] = pipeline.run_pipeline(instance, pipe["context"],
                                              max_initial_entities=pipe["max_initial_entities"])
        rec["status"] = "ok"
    except Exception as e:
        rec["status"] = "error"
        rec["error"] = repr(e)
        rec["traceback"] = traceback.format_exc()
    rec["seconds"] = round(time.time() - t0, 1)
    rec["chain_order"] = order
    import entity_localization_pipeline as elp  # which lenient-parse step succeeded, per reply
    rec["json_parse"] = dict(getattr(elp, "A3062_PARSE_STATS", {}))
    order_dir = os.path.join(os.environ["ENTITY_PIPELINE_CACHE_DIR"], iid)
    os.makedirs(order_dir, exist_ok=True)
    with open(os.path.join(order_dir, "chain_order.json"), "w") as f:
        json.dump(order, f)
    rec["tokens"] = calls.summary()
    rec["calls"] = calls.records
    import resource  # peak RSS of this worker process; ru_maxrss is KiB on Linux
    rec["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)
    return rec


def apply_chain_order(pipeline, iid, spec):
    """Control the order in which the kept chains (stage 4) are shown to the voters.

    The released code shows them in stage 4's order (the longest first when more than 6 chains
    were built), and stage 5 numbers them chain_1, chain_2, ... in that order, so the order is
    also the label. mode "shuffle" permutes stage 4's output with a seed derived from
    (seed, instance_id): the same seed gives the same permutation of positions in every arm.
    Only display order and labels change; no chain is added, dropped or altered. Returns the
    record of what was done; `permutation[k-1]` is the stage-4 position of the chain shown as
    chain_k. The pipeline itself is untouched (method wrapped on this instance only)."""
    info = {"mode": spec.get("mode", "fixed"), "seed": spec.get("seed")}
    if info["mode"] == "fixed":
        return info
    if info["mode"] != "shuffle" or info["seed"] is None:
        raise ValueError(f"chain_order must be fixed, or shuffle with a seed: {spec}")
    import random
    select = pipeline._select_diverse_chains

    def select_then_shuffle(all_chains, *args, **kwargs):
        kept = select(all_chains, *args, **kwargs)
        perm = list(range(len(kept)))
        random.Random(f"{info['seed']}:{iid}").shuffle(perm)
        info["permutation"] = [p + 1 for p in perm]
        return [kept[p] for p in perm]

    pipeline._select_diverse_chains = select_then_shuffle
    return info


def instance_ids(cfg):
    """`instances: [ids]`, or `instances_file:` (one id per line) with optional
    `instances_slice: "start:stop"`."""
    if "instances" in cfg:
        return list(cfg["instances"])
    with open(os.path.join(ROOT, cfg["instances_file"])) as f:
        ids = [line.strip() for line in f if line.strip()]
    if cfg.get("instances_slice"):
        a, b = (int(x) if x else None for x in str(cfg["instances_slice"]).split(":"))
        ids = ids[a:b]
    return ids


# Config parts that change results; a resumed run must match the original on all of them.
# Not included: llm.base_url (per-job port), run.workers (concurrency only).
def result_relevant(cfg):
    return {"name": cfg.get("name"), "version": cfg.get("version"),
            "instances": cfg.get("instances"), "instances_file": cfg.get("instances_file"),
            "instances_slice": cfg.get("instances_slice"),
            "model": cfg["llm"]["model"], "timeout_seconds": cfg["llm"].get("timeout_seconds"),
            "pipeline": cfg["pipeline"], "instance_fields": cfg.get("instance_fields"),
            "graph_index_dir": cfg["paths"]["graph_index_dir"]}


def prepare_resume(run_dir, cfg):
    """Continue a run in place: return (manifest, ids already recorded). Every instance with a
    line in raw.jsonl is skipped whatever its status (a crash such as debate_collapsed is an
    outcome, not a gap); instances in progress when the job died have no line and run again.
    Refuses if the config differs from the original run in anything that changes results.
    A torn last line (job killed mid-write) is dropped, keeping raw.jsonl.bak."""
    with open(os.path.join(run_dir, "manifest.json")) as f:
        manifest = json.load(f)
    before, now = result_relevant(manifest["config_body"]), result_relevant(cfg)
    diff = sorted(k for k in now if json.dumps(before.get(k), sort_keys=True, default=str)
                  != json.dumps(now.get(k), sort_keys=True, default=str))
    if diff:
        raise SystemExit(f"--resume refused: config differs from {run_dir} in {diff}")
    raw_path, done, good, torn = os.path.join(run_dir, "raw.jsonl"), set(), [], 0
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["instance_id"])
                    good.append(line if line.endswith("\n") else line + "\n")
                except (ValueError, KeyError):
                    torn += 1
        if torn:
            os.replace(raw_path, raw_path + ".bak")
            with open(raw_path, "w") as f:
                f.writelines(good)
    manifest.setdefault("resumes", []).append({"dropped_torn_lines": torn})
    return manifest, done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--base-url", help="override llm.base_url, e.g. a per-job port on a shared node")
    ap.add_argument("--shuffle-seed", type=int, default=None,
                    help="show the kept chains in a seeded random order (overrides pipeline.chain_order)")
    ap.add_argument("--lenient-json", action="store_true",
                    help="opt-in lenient JSON parsing in the fork (overrides pipeline.lenient_json)")
    ap.add_argument("--resume", metavar="RUN_DIR",
                    help="continue this run in place: skip instances already in its raw.jsonl")
    ap.add_argument("--workers", type=int, default=None,
                    help="instances run in parallel (separate processes); default run.workers or 1")
    args = ap.parse_args()

    cfg_path = os.path.abspath(args.config)
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    workers = args.workers or cfg.get("run", {}).get("workers", 1)
    ids = instance_ids(cfg)

    llm, pipe = cfg["llm"], cfg["pipeline"]
    if args.lenient_json:
        pipe["lenient_json"] = True
    if args.shuffle_seed is not None:
        pipe["chain_order"] = {"mode": "shuffle", "seed": args.shuffle_seed}
    if args.base_url:
        llm["base_url"] = args.base_url

    if args.resume:
        out = os.path.abspath(args.resume)
        old_manifest, done = prepare_resume(out, cfg)
        run_id = old_manifest["run_id"]
    else:
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        out = os.path.join(ROOT, cfg["paths"]["results"], run_id)
        old_manifest, done = None, set()
    work = os.path.join(out, "work")
    os.makedirs(work, exist_ok=True)
    # The fork reads all of these at import or construction time, so set them first.
    # Worker processes inherit the environment and the working directory.
    os.environ["LLM_BASE_URL"] = llm["base_url"]
    os.environ["LLM_MODEL"] = llm["model"]
    os.environ["LLM_TIMEOUT"] = str(llm["timeout_seconds"])
    os.environ["GRAPH_INDEX_DIR"] = os.path.join(ROOT, cfg["paths"]["graph_index_dir"])
    os.environ["ENTITY_PIPELINE_CACHE_DIR"] = os.path.join(out, "stage_cache")
    os.environ["CHAIN_EMBED_MODEL"] = pipe["chain_embed_model"]
    # Fork's opt-in lenient JSON parsing (default off = released behaviour); workers inherit it.
    os.environ["A3062_LENIENT_JSON"] = "1" if pipe.get("lenient_json") else "0"
    # set_current_issue() makes playground/<uuid> relative to the working directory.
    os.chdir(work)

    manifest = {
        "run_id": run_id, "config": os.path.relpath(cfg_path, ROOT), "config_body": cfg,
        "instances": ids, "workers": workers,
        "lenient_json": os.environ["A3062_LENIENT_JSON"] == "1",
        "started": datetime.now().isoformat(), "host": platform.node(),
        "python": sys.version, "repo_sha": git_sha(ROOT), "fork_sha": git_sha(FORK),
        "served_models": served_model(llm["base_url"]),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "slurm_gpus": os.environ.get("SLURM_JOB_GPUS") or os.environ.get("SLURM_GPUS_ON_NODE"),
        "gpu_names": _gpu_names(),
        "serving": {k.lower(): os.environ.get(k) for k in
                    ("MODEL", "SERVED_NAME", "MAX_LEN", "ROPE_YARN", "GPU_UTIL", "PARALLEL", "SEED")},
        "base_url": llm["base_url"], "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    }
    if old_manifest is not None:
        # keep the original run's manifest; record this continuation in its `resumes` list
        old_manifest["resumes"][-1].update(
            {k: manifest[k] for k in ("started", "host", "repo_sha", "fork_sha", "served_models",
                                      "slurm_job_id", "workers", "base_url", "gpu_names",
                                      "serving", "lenient_json")},
            skipped=sorted(done), remaining=[i for i in ids if i not in done])
        manifest = old_manifest
        ids = [i for i in ids if i not in done]
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"run {run_id} -> {out}" + (f" (resumed: {len(done)} done, {len(ids)} to run)"
                                       if old_manifest is not None else ""))
    print(f"endpoint serves: {manifest['served_models']}")
    print(f"{len(ids)} instances, {workers} at a time", flush=True)

    raw_path = os.path.join(out, "raw.jsonl")
    keep = cfg["instance_fields"]["keep"]

    empty_tokens = {"total": {"calls": 0, "errors": 0, "truncated": 0, "prompt_tokens": 0,
                              "completion_tokens": 0}, "by_stage": {}}

    def record(rec, done):
        rec.setdefault("seconds", None)
        rec.setdefault("tokens", empty_tokens)
        rec.setdefault("calls", [])
        with open(raw_path, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        t = rec["tokens"]["total"]
        print(f"[{done}/{len(ids)}] {rec['instance_id']}: {rec['status']} in {rec['seconds']} s, "
              f"{t['calls']} calls ({t['errors']} failed, {t['truncated']} hit max_tokens), "
              f"{t['prompt_tokens']} prompt + {t['completion_tokens']} completion tokens"
              + (f", peak RAM {rec['peak_rss_gb']} GB" if rec.get("peak_rss_gb") else ""),
              flush=True)
        if rec["status"] == "error":
            print(rec["traceback"], flush=True)

    if workers <= 1:
        for i, iid in enumerate(ids, 1):
            record(run_one(iid, keep, pipe), i)
    else:
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor, as_completed
        from concurrent.futures.process import BrokenProcessPool

        # spawn, not fork (torch and threads make fork unsafe). max_tasks_per_child=1: a
        # fresh process per instance, so nothing (embedding model, graph) accumulates.
        # If a worker is killed (job 180136: the job hit its 24 GB RAM limit), the pool
        # breaks and every pending future fails; rerun those in a new pool, at most twice
        # per instance, instead of recording them as errors.
        pending, attempts, done = list(ids), {iid: 0 for iid in ids}, 0
        while pending:
            for iid in pending:
                attempts[iid] += 1
            broken = []
            with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn"),
                                     initializer=_init_worker, max_tasks_per_child=1) as ex:
                futs = {ex.submit(run_one, iid, keep, pipe): iid for iid in pending}
                for fut in as_completed(futs):
                    iid = futs[fut]
                    try:
                        rec = fut.result()
                    except BrokenProcessPool:
                        broken.append(iid)
                        continue
                    except Exception as e:
                        rec = {"instance_id": iid, "status": "error", "error": repr(e),
                               "traceback": traceback.format_exc()}
                    done += 1
                    record(rec, done)
            pending = [iid for iid in broken if attempts[iid] < 3]
            for iid in broken:
                if attempts[iid] >= 3:
                    done += 1
                    record({"instance_id": iid, "status": "error",
                            "error": "worker process died 3 times (likely out of memory)",
                            "traceback": ""}, done)
            if pending:
                print(f"worker pool broke (a worker was killed); retrying {len(pending)} "
                      f"instances in a new pool", flush=True)

    manifest["finished"] = datetime.now().isoformat()
    if manifest.get("resumes"):
        manifest["resumes"][-1]["finished"] = manifest["finished"]
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)


if __name__ == "__main__":
    main()

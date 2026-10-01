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
                   finish_reason=resp.choices[0].finish_reason if resp.choices else None)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--base-url", help="override llm.base_url, e.g. a per-job port on a shared node")
    args = ap.parse_args()

    cfg_path = os.path.abspath(args.config)
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(ROOT, cfg["paths"]["results"], run_id)
    work = os.path.join(out, "work")
    os.makedirs(work, exist_ok=True)

    llm, pipe = cfg["llm"], cfg["pipeline"]
    if args.base_url:
        llm["base_url"] = args.base_url
    # The fork reads all of these at import or construction time, so set them first.
    os.environ["LLM_BASE_URL"] = llm["base_url"]
    os.environ["LLM_MODEL"] = llm["model"]
    os.environ["LLM_TIMEOUT"] = str(llm["timeout_seconds"])
    os.environ["GRAPH_INDEX_DIR"] = os.path.join(ROOT, cfg["paths"]["graph_index_dir"])
    os.environ["ENTITY_PIPELINE_CACHE_DIR"] = os.path.join(out, "stage_cache")
    os.environ["CHAIN_EMBED_MODEL"] = pipe["chain_embed_model"]

    sys.path[:0] = [os.path.join(FORK, "localization"), FORK]
    # set_current_issue() makes playground/<uuid> relative to the working directory.
    os.chdir(work)

    from moatless.benchmark.utils import get_moatless_instance
    from entity_localization_pipeline import EntityLocalizationPipeline

    manifest = {
        "run_id": run_id, "config": os.path.relpath(cfg_path, ROOT), "config_body": cfg,
        "started": datetime.now().isoformat(), "host": platform.node(),
        "python": sys.version, "repo_sha": git_sha(ROOT), "fork_sha": git_sha(FORK),
        "served_models": served_model(llm["base_url"]),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "base_url": llm["base_url"], "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    }
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"run {run_id} -> {out}")
    print(f"endpoint serves: {manifest['served_models']}")

    raw_path = os.path.join(out, "raw.jsonl")
    for iid in cfg["instances"]:
        full = get_moatless_instance(instance_id=iid)
        instance = {k: full[k] for k in cfg["instance_fields"]["keep"]}

        pipeline = EntityLocalizationPipeline(max_depth=pipe["max_depth"])
        calls = CallLog(pipeline.client)
        t0 = time.time()
        rec = {"instance_id": iid}
        try:
            rec["output"] = pipeline.run_pipeline(instance, pipe["context"],
                                                  max_initial_entities=pipe["max_initial_entities"])
            rec["status"] = "ok"
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = repr(e)
            rec["traceback"] = traceback.format_exc()
        rec["seconds"] = round(time.time() - t0, 1)
        rec["tokens"] = calls.summary()
        rec["calls"] = calls.records

        with open(raw_path, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        t = rec["tokens"]["total"]
        print(f"{iid}: {rec['status']} in {rec['seconds']} s, {t['calls']} calls "
              f"({t['errors']} failed, {t['truncated']} hit max_tokens), "
              f"{t['prompt_tokens']} prompt + {t['completion_tokens']} completion tokens")
        if rec["status"] == "error":
            print(rec["traceback"])

    manifest["finished"] = datetime.now().isoformat()
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)


if __name__ == "__main__":
    main()

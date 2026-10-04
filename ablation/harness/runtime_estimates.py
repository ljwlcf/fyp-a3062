"""Wall-clock minutes per instance, per GPU model, from past run manifests.

Used by ablation/eee/pick_gpu.sh (GPU rule 3, decisions.md 2026-10-02): a fallback GPU pair
for a small model is chosen only if its estimated start plus expected run time is clearly
sooner than 2x pro6000's. Reads every ablation/results/*/<run>/manifest.json with a finished
time; the GPU model comes from the host name (gpu-a6000-1 -> a6000). Prints one line per
(gpu model, served model): runs, instances, minutes per instance (median over runs), workers.

Usage:  python ablation/harness/runtime_estimates.py [served-model-substring]
"""
import glob
import json
import os
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def gpu_model(host):
    m = re.match(r"gpu-([a-z0-9]+?)(?:-\d+)?(?:\.|$)", host or "")
    return {"5090": "rtx5090"}.get(m.group(1), m.group(1)) if m else None


def main(filter_model=""):
    per = defaultdict(list)
    for path in glob.glob(os.path.join(ROOT, "ablation", "results", "*", "*", "manifest.json")):
        try:
            with open(path) as f:
                m = json.load(f)
        except ValueError:  # a run that crashed while writing its manifest
            continue
        if not m.get("finished") or not m.get("started"):
            continue
        gpu = gpu_model(m.get("host"))
        model = ((m.get("serving") or {}).get("served_name")
                 or (m.get("config_body") or {}).get("llm", {}).get("model"))
        if not gpu or filter_model not in (model or ""):
            continue
        n = len(m.get("instances") or (m.get("config_body") or {}).get("instances") or [])
        if not n:
            continue
        minutes = (datetime.fromisoformat(m["finished"]) -
                   datetime.fromisoformat(m["started"])).total_seconds() / 60
        # parser setting and GPU count change the run time a lot (a collapsed debate is fast)
        lenient = "lenient" if m.get("lenient_json") else "released"
        names = m.get("gpu_names") or ["?"]
        ngpu = len(names)
        # pro6000 nodes mix the 300 W Max-Q Workstation and the 600 W Server Edition: same outputs,
        # different speed, so time estimates are kept apart by edition
        edition = ("max-q" if any("Max-Q" in x for x in names) else
                   "server" if any("Server" in x for x in names) else "-")
        per[(gpu, model, lenient, ngpu, edition)].append((minutes / n, n, m.get("workers")))
    for (gpu, model, lenient, ngpu, edition), runs in sorted(per.items()):
        print(f"{gpu}\t{model}\t{lenient} x{ngpu}gpu {edition}\t{len(runs)} runs\t{sum(r[1] for r in runs)} instances\t"
              f"{statistics.median(r[0] for r in runs):.2f} min/instance\t"
              f"workers {sorted({r[2] for r in runs})}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")

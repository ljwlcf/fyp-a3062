"""Paired comparison of arms run on IDENTICAL chains (run_localization --reuse-chains).

For each original seed: the first original run, any noise-floor reruns of the original arm on the
same chains, and the arm runs that reused that seed's chains. Reports per seed, and pooled:
Acc@1, stage 6-7 tokens, discordant pairs against the first original run (exact McNemar), and the
difference against the MEAN of all original-arm runs on those chains (paired bootstrap over
instances; the fairer reference once reruns exist, since the first run is itself one noisy draw).

Usage: python ablation/harness/paired_arms.py [--out FILE]
Run folders are found from each run's manifest (`reuse_chains_from`), so nothing is hard-coded.
"""
import argparse
import glob
import json
import os
import random
from math import comb

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ORIG = "ablation/results/baseline_72b_lenient_v1"
ARMS = {"rerun (noise floor)": "ablation/results/baseline_72b_rerun_lenient_v1",
        "adaptive single-agent": "ablation/results/baseline_72b_adaptive_lenient_v1",
        "adaptive round1_only": "ablation/results/baseline_72b_adaptive_r1_lenient_v1",
        "self-consistency": "ablation/results/baseline_72b_sc_lenient_v1"}


def scores(run):
    path = os.path.join(ROOT, run, "scores.jsonl")
    if not os.path.exists(path):
        return None
    return {r["instance_id"]: r for r in map(json.loads, open(path))}


def ref_of(run):
    m = json.load(open(os.path.join(ROOT, run, "manifest.json")))
    return (m.get("config_body") or {}).get("pipeline", {}).get("reuse_chains_from")


def mcnemar(b, c):
    n = b + c
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n) if n else 1.0


def boot(diffs_by_inst, n_boot=4000, seed=0):
    ids = sorted(diffs_by_inst)
    rng = random.Random(seed)
    out = []
    for _ in range(n_boot):
        smp = [diffs_by_inst[ids[rng.randrange(len(ids))]] for _ in ids]
        out.append(sum(sum(g) for g in smp) / sum(len(g) for g in smp))
    out.sort()
    return [round(out[int(0.025 * n_boot)], 4), round(out[int(0.975 * n_boot)], 4)], round(out[int(0.05 * n_boot)], 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    runs = {}   # reference seed run -> {arm: [run dirs]}
    for arm, base in ARMS.items():
        for d in sorted(glob.glob(os.path.join(ROOT, base, "*/manifest.json"))):
            run = os.path.relpath(os.path.dirname(d), ROOT)
            ref = ref_of(run)
            if ref and scores(run) and scores(ref):
                if len(scores(run)) == len(scores(ref)) == 75:
                    runs.setdefault(ref, {}).setdefault(arm, []).append(run)
    report = {"seeds": {}, "pooled": {}}
    pooled = {}
    for ref in sorted(runs):
        o = scores(ref)
        reruns = [scores(r) for r in runs[ref].get("rerun (noise floor)", [])]
        orig_mean = {i: sum(x[i]["acc1_file"] for x in [o] + reruns) / (1 + len(reruns)) for i in o}
        seed = {"original": {"acc1": round(sum(o[i]["acc1_file"] for i in o) / len(o), 4),
                             "stage67": round(sum(o[i]["stage67_tokens"] for i in o) / len(o))},
                "original_runs_in_mean": 1 + len(reruns)}
        for arm, dirs in runs[ref].items():
            for run in dirs:
                x = scores(run)
                same = all(x[i]["n_chains_kept"] == o[i]["n_chains_kept"] for i in o)
                b = sum(1 for i in o if x[i]["acc1_file"] and not o[i]["acc1_file"])
                c = sum(1 for i in o if o[i]["acc1_file"] and not x[i]["acc1_file"])
                row = {"run": run, "same_chains": same,
                       "acc1": round(sum(x[i]["acc1_file"] for i in o) / len(o), 4),
                       "stage67": round(sum(x[i]["stage67_tokens"] for i in o) / len(o)),
                       "vs_first_original": f"{b}:{c}"}
                seed.setdefault(arm, []).append(row)
                p = pooled.setdefault(arm, {"b": 0, "c": 0, "n": 0, "acc": 0, "tok": 0, "otok": 0,
                                            "omean": 0, "diff": {}})
                p["b"] += b; p["c"] += c; p["n"] += len(o)
                p["acc"] += sum(x[i]["acc1_file"] for i in o)
                p["tok"] += sum(x[i]["stage67_tokens"] for i in o)
                p["otok"] += sum(o[i]["stage67_tokens"] for i in o)
                if arm != "rerun (noise floor)":
                    p["omean"] += sum(orig_mean.values())
                    for i in o:
                        p["diff"].setdefault(i, []).append(int(x[i]["acc1_file"]) - orig_mean[i])
        report["seeds"][ref] = seed
    for arm, p in pooled.items():
        r = {"instance_runs": p["n"], "acc1": round(p["acc"] / p["n"], 4),
             "stage67": round(p["tok"] / p["n"]), "original_stage67": round(p["otok"] / p["n"]),
             "token_change": round(p["tok"] / p["otok"] - 1, 3),
             "vs_first_original": f"{p['b']}:{p['c']}", "mcnemar_p": round(mcnemar(p["b"], p["c"]), 3),
             "discordance": round((p["b"] + p["c"]) / p["n"], 3)}
        if p["diff"]:
            d = sum(sum(g) for g in p["diff"].values()) / sum(len(g) for g in p["diff"].values())
            ci, lo = boot(p["diff"])
            r.update(original_mean_acc1=round(p["omean"] / p["n"], 4), diff_vs_original_mean=round(d, 4),
                     ci95=ci, one_sided_lower95=lo)
        report["pooled"][arm] = r
    if args.out:
        json.dump(report, open(os.path.join(ROOT, args.out), "w"), indent=2)
    for arm, r in report["pooled"].items():
        print(f"{arm:23} n={r['instance_runs']:3}  acc {r['acc1']:.3f}  tokens {r['stage67']} ({r['token_change']:+.0%})"
              f"  vs first original {r['vs_first_original']} (p={r['mcnemar_p']}, disc {r['discordance']:.1%})"
              + (f"  vs original mean {r['original_mean_acc1']:.3f}: {r['diff_vs_original_mean']:+.4f} {r['ci95']} lower {r['one_sided_lower95']}"
                 if "diff_vs_original_mean" in r else ""))


if __name__ == "__main__":
    main()

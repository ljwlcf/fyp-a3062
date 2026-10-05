"""Offline replay of adaptive debate (CLAUDE.md plan item 2) on runs of the ORIGINAL arm.

Adaptive debate keeps the vote (stage 6) and then either
  skip  — the signal says the vote is clear: the single-agent plan step (decisions.md 2026-10-02:
          one round-1 analysis, round 2 skipped, the released discriminator), or
  full  — the released debate (5 round-1 analyses, round 2, discriminator).
An original-arm run records everything both branches need on the same winning chain, so the
trigger can be evaluated without new GPU runs:
  full branch answer  = the run's own final-plan file (acc1_file), cost = its stage 6-7 tokens;
  skip branch answer  = ONE round-1 agent's top file. The five round-1 agents get identical
          prompts at T=0.7 (deviations.md), so each is an exchangeable sample of the skip branch;
          its accuracy is the EXPECTED value over the five (an agent whose reply did not parse or
          did not resolve to a file counts as wrong);
          cost = vote + one round-1 call (the run's mean) + the run's discriminator call. The
          discriminator here read five analyses, so this overstates the skip cost (conservative).
Approximation to check against the self-consistency runs, which run the real skip step: the
discriminator may change the file of a lone round-1 analysis (see `--sc`: pass-through rate).

Signals (skip when signal >= threshold; an instance without the signal is never skipped):
  lp_conf               mean over votes of p(top chain) at the chain-number token (vote logprobs)
  vote_agreement        winning votes / valid votes (the released vote)
  vote_mean_confidence  the agents' self-reported confidence (released field)

Thresholds chosen on the same rows are optimistic; with several runs, `held_out` picks the
threshold on the other runs (largest saving whose accuracy is >= the original's there) and
evaluates it on the held-out run.

Usage:
    python ablation/harness/replay_trigger.py RUN_DIR [RUN_DIR ...] [--sc SC_RUN_DIR ...]
        [--out ablation/results/<name>/trigger_replay.json]
Run score_localization.py on each run first (reads scores.jsonl and raw.jsonl).
"""
import argparse
import json
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SIGNALS = ("lp_conf", "vote_agreement", "vote_mean_confidence")


def _tok(by_stage, stage):
    v = by_stage.get(stage) or {}
    return v.get("prompt_tokens", 0) + v.get("completion_tokens", 0), v.get("calls", 0)


def load_rows(run_dir):
    raw = {}
    with open(os.path.join(run_dir, "raw.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            raw[r["instance_id"]] = r
    rows = []
    with open(os.path.join(run_dir, "scores.jsonl")) as f:
        for line in f:
            s = json.loads(line)
            if s.get("arm", "original") != "original":
                sys.exit(f"{run_dir}: arm {s.get('arm')}; replay needs original-arm runs")
            if s.get("winning_chain_id") is None:
                continue        # failed before the vote: neither branch exists
            by = (raw[s["instance_id"]].get("tokens") or {}).get("by_stage", {})
            vote, _ = _tok(by, "vote_worker")
            r1, r1_calls = _tok(by, "analyze_worker")
            r2, _ = _tok(by, "analyze_worker_round2")
            disc, _ = _tok(by, "_conduct_final_discrimination")
            gold = set(s["gold_files"])
            n_agents = max(r1_calls, 1)
            rows.append({
                "run": os.path.relpath(run_dir, ROOT), "instance_id": s["instance_id"],
                "status": s["status"],
                "full_correct": bool(s.get("acc1_file")),
                "skip_correct": sum(f in gold for f in s.get("round1_files") or []) / n_agents,
                "cost_full": vote + r1 + r2 + disc,
                "cost_skip": vote + (r1 / r1_calls if r1_calls else 0) + disc,
                "selected_has_gold_file": s.get("selected_has_gold_file"),
                "debate_effect": s.get("debate_effect"),
                **{k: s.get(k) for k in SIGNALS}})
    return rows


def evaluate(rows, signal, tau):
    """Accuracy (expected) and stage 6-7 tokens of adaptive debate at one threshold."""
    acc = cost = 0.0
    skipped = 0
    for r in rows:
        v = r[signal]
        if v is not None and v >= tau:
            skipped += 1
            acc += r["skip_correct"]
            cost += r["cost_skip"]
        else:
            acc += r["full_correct"]
            cost += r["cost_full"]
    n = len(rows)
    return {"threshold": tau, "skip_rate": round(skipped / n, 3), "acc1": round(acc / n, 4),
            "mean_stage67_tokens": round(cost / n)}


def thresholds(rows, signal):
    vals = sorted({r[signal] for r in rows if r[signal] is not None})
    return vals + [float("inf")]       # inf = never skip = the original arm


def curve(rows, signal):
    return [evaluate(rows, signal, t) for t in thresholds(rows, signal)]


def best_no_loss(rows, signal):
    """Lowest-cost threshold whose accuracy is >= the original's on these rows."""
    pts = curve(rows, signal)
    base = pts[-1]
    ok = [p for p in pts if p["acc1"] >= base["acc1"] - 1e-9]
    return min(ok, key=lambda p: (p["mean_stage67_tokens"], -p["acc1"]))


def bootstrap_diff(rows, signal, tau, n_boot=2000, seed=0):
    """Paired bootstrap over instances (all runs of an instance resampled together): adaptive
    minus original Acc@1 at threshold tau. Returns the mean and the 95% interval."""
    by_inst = {}
    for r in rows:
        v = r[signal]
        a = r["skip_correct"] if v is not None and v >= tau else r["full_correct"]
        by_inst.setdefault(r["instance_id"], []).append(a - r["full_correct"])
    groups = list(by_inst.values())
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        sample = [groups[rng.randrange(len(groups))] for _ in groups]
        tot = sum(sum(g) for g in sample)
        n = sum(len(g) for g in sample)
        diffs.append(tot / n)
    diffs.sort()
    point = sum(sum(g) for g in groups) / sum(len(g) for g in groups)
    return {"mean_diff": round(point, 4), "ci95": [round(diffs[int(0.025 * n_boot)], 4),
                                                  round(diffs[int(0.975 * n_boot)], 4)]}


def held_out(rows, signal):
    runs = sorted({r["run"] for r in rows})
    if len(runs) < 2:
        return None
    out = []
    for run in runs:
        train = [r for r in rows if r["run"] != run and r[signal] is not None]
        test = [r for r in rows if r["run"] == run]
        if not train or not any(r[signal] is not None for r in test):
            continue
        tau = best_no_loss(train, signal)["threshold"]
        res = evaluate(test, signal, tau)
        res.update(run=run, original_acc1=evaluate(test, signal, float("inf"))["acc1"],
                   original_tokens=evaluate(test, signal, float("inf"))["mean_stage67_tokens"])
        out.append(res)
    return out


def sc_check(sc_dirs, ids):
    """Self-consistency runs (the real skip step on N votes): Acc@1 and stage 6-7 tokens on the
    replayed instances, and how often the discriminator kept the lone round-1 file."""
    rows = []
    for d in sc_dirs:
        with open(os.path.join(d, "scores.jsonl")) as f:
            rows += [s for s in map(json.loads, f) if s["instance_id"] in ids]
    if not rows:
        return None
    passed = [s for s in rows if s.get("round1_files") and s.get("plan_files")]
    return {"runs": [os.path.relpath(d, ROOT) for d in sc_dirs], "n": len(rows),
            "acc1": round(sum(bool(s.get("acc1_file")) for s in rows) / len(rows), 4),
            "mean_stage67_tokens": round(sum(s.get("stage67_tokens") or 0 for s in rows) / len(rows)),
            "plan_keeps_round1_file": round(sum(s["plan_files"][0] == s["round1_files"][0]
                                                for s in passed) / max(1, len(passed)), 3)}


def summarize(rows, sc_dirs):
    n = len(rows)
    orig = {"acc1": round(sum(r["full_correct"] for r in rows) / n, 4),
            "mean_stage67_tokens": round(sum(r["cost_full"] for r in rows) / n)}
    always = {"acc1": round(sum(r["skip_correct"] for r in rows) / n, 4),
              "mean_stage67_tokens": round(sum(r["cost_skip"] for r in rows) / n)}
    oracle = {"acc1": round(sum(max(r["full_correct"], r["skip_correct"]) for r in rows) / n, 4)}
    out = {"runs": sorted({r["run"] for r in rows}), "n_rows": n,
           "n_instances": len({r["instance_id"] for r in rows}),
           "n_rows_not_ok": sum(r["status"] != "ok" for r in rows),
           "original": orig, "always_skip": always, "oracle_per_instance": oracle,
           "signals": {}}
    for sig in SIGNALS:
        have = [r for r in rows if r[sig] is not None]
        if not have:
            continue
        best = best_no_loss(rows, sig)
        out["signals"][sig] = {
            "n_rows_with_signal": len(have),
            "best_no_loss_in_sample": best,
            "token_saving_in_sample": round(1 - best["mean_stage67_tokens"] / orig["mean_stage67_tokens"], 3),
            "bootstrap_at_best": bootstrap_diff(rows, sig, best["threshold"]),
            "held_out": held_out(rows, sig),
            "curve": curve(rows, sig)}
    if sc_dirs:
        out["self_consistency"] = sc_check(sc_dirs, {r["instance_id"] for r in rows})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs", nargs="+", help="original-arm run directories (scored)")
    ap.add_argument("--sc", nargs="*", default=[], help="self-consistency run directories (scored)")
    ap.add_argument("--out", help="write the full result (with curves) here")
    args = ap.parse_args()
    rows = [r for d in args.runs for r in load_rows(d)]
    res = summarize(rows, args.sc)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump({"rows": rows, **res}, f, indent=2, default=str)
    brief = json.loads(json.dumps(res, default=str))
    for s in brief["signals"].values():
        s.pop("curve")
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()

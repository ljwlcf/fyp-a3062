"""Is vote agreement a confidence signal, or partly a position effect? (decisions.md 2026-10-02)

Reads scored runs (score_localization.py output) of the same instances under FIXED chain order
(stage 4's order, longest first when >6 chains) and SHUFFLED order (runner --shuffle-seed), and
reports, per arm:

  shown_first   P(winner was the chain shown first)  vs chance (mean 1/n_kept)
  longest       P(winner is the longest kept chain)  -- content, independent of display order
  agreement     mean vote agreement (winning votes / valid votes)
  agree|first   mean agreement when the winner was shown first vs when it was not
  selection     P(selected chain contains a gold file), and Acc@1 (File)

Reading it: if shuffling leaves `longest` and `agreement` unchanged and `shown_first` falls to
chance, the vote follows content and agreement can be used as a skip signal. If `shown_first`
stays above chance under shuffle, or agreement is higher when the first-shown chain wins, the
vote has a position bias and agreement is inflated by it.

Usage:
    python ablation/harness/analyze_order.py ablation/results/order_check_v1/<run> [...]
Prints a table and writes order_analysis.json next to the first run's parent directory.
"""
import json
import os
import sys
from collections import defaultdict


def load(run_dir):
    with open(os.path.join(run_dir, "scores.jsonl")) as f:
        rows = [json.loads(line) for line in f]
    return [r for r in rows if r["status"] == "ok" and "error" not in r]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def arm_stats(rows):
    first = [r for r in rows if r.get("winner_shown_position") == 1]
    other = [r for r in rows if r.get("winner_shown_position") not in (1, None)]
    return {
        "n_instance_runs": len(rows),
        "shown_first": mean([r.get("winner_shown_position") == 1 for r in rows]),
        "chance_shown_first": mean([1 / r["n_chains_kept"] for r in rows if r.get("n_chains_kept")]),
        "longest": mean([r.get("winner_is_longest") for r in rows]),
        "stage4_first": mean([r.get("winner_stage4_position") == 1 for r in rows]),
        "agreement": mean([r.get("vote_agreement") for r in rows]),
        "agreement_when_first_won": mean([r.get("vote_agreement") for r in first]),
        "agreement_when_other_won": mean([r.get("vote_agreement") for r in other]),
        "unanimous": mean([r.get("vote_agreement") == 1 for r in rows]),
        "selection": mean([r.get("selected_has_gold_file") for r in rows]),
        "acc1_file": mean([r.get("acc1_file") for r in rows]),
    }


def main(run_dirs):
    arms = defaultdict(list)
    runs = defaultdict(list)
    for d in run_dirs:
        rows = load(d)
        mode = (rows[0].get("chain_order") if rows else None) or "fixed"
        arms[mode].extend(rows)
        runs[mode].append(os.path.basename(d.rstrip("/")))
    out = {mode: {"runs": runs[mode], **arm_stats(rows)} for mode, rows in arms.items()}

    keys = ["n_instance_runs", "shown_first", "chance_shown_first", "longest", "stage4_first",
            "agreement", "agreement_when_first_won", "agreement_when_other_won", "unanimous",
            "selection", "acc1_file"]
    modes = sorted(out)
    print(f"{'':28s}" + "".join(f"{m:>12s}" for m in modes))
    for k in keys:
        print(f"{k:28s}" + "".join(f"{str(out[m].get(k)):>12s}" for m in modes))

    # per instance: does the same CONTENT win regardless of order?
    by_iid = defaultdict(lambda: defaultdict(list))
    for mode, rows in arms.items():
        for r in rows:
            by_iid[r["instance_id"]][mode].append(
                (tuple(r.get("winner_chain") or []), r.get("winner_shown_position"),
                 r.get("vote_agreement")))
    print("\nper instance: winner shown position / agreement, per run")
    for iid in sorted(by_iid):
        cells = []
        for m in modes:
            cells.append(m + ": " + " ".join(f"{p}/{a:.1f}" if a is not None else f"{p}/-"
                                             for _, p, a in by_iid[iid][m]))
        print(f"  {iid:26s} " + " | ".join(cells))
    out["per_instance"] = {iid: {m: [{"shown": p, "agreement": a, "winner": list(w)}
                                     for w, p, a in v] for m, v in d.items()}
                           for iid, d in by_iid.items()}

    dest = os.path.join(os.path.dirname(run_dirs[0].rstrip("/")), "order_analysis.json")
    with open(dest, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])

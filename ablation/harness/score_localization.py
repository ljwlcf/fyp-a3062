"""Score localization runs produced by run_localization.py, stage by stage.

For each instance, reads raw.jsonl (status, tokens, calls) and the pipeline's own stage
cache, and asks where the gold location was found or lost:

  built     stage 3: is the gold file / entity in ANY chain built?   (the graph's job)
  kept      stage 4: is it in a chain kept for the vote?             (diversity filter)
  selected  stage 6: is it in the winning chain?                     (the vote's job)
  acc1_file final plan: is the first file the plan edits a gold file?

plus vote agreement, whether the winner was chain_1 (always the longest, always shown
first), agents dropped from the debate, and tokens split into graph walk / vote / debate.

Gold files come from the moatless record's golden_patch. Gold entities (innermost
class/function spanning each changed line) come from the RQ1 raw records, which map the
same gold patch onto the same builder's graph; instances outside RQ1 get file-level only.

Usage:
    python ablation/harness/score_localization.py ablation/results/<config>/<run_id> [...]
Writes scores.jsonl and summary.json into each run directory and prints a summary.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOATLESS = os.path.join(ROOT, "swe-debate", "moatless", "benchmark",
                        "swebench_verified_all_evaluations.json")
RQ1_RAW = os.path.join(ROOT, "ablation", "results", "rq1_reachability_v2", "raw.*.jsonl")

STAGE_GROUP = {  # pipeline method that made the call -> cost bucket
    "_extract_initial_entities": "graph_walk",
    "_extract_entities_from_code_snippets": "graph_walk",
    "_select_next_node_with_llm": "graph_walk",
    "_prefilter_neighbors_with_llm": "graph_walk",
    "vote_worker": "vote",
    "analyze_worker": "debate",
    "analyze_worker_round2": "debate",
    "_conduct_final_discrimination": "debate",
}
ENTITY_NUM = re.compile(r"Entity\s+(\d+)\s*:?\s*")
PY_PATH = re.compile(r"([\w./-]+\.py)")


def resolve_location(text, chain):
    """Map an agent's free-text location onto a winning-chain node id, or None.
    Agents write it three ways: a full node id ('a/b.py:C.f'), 'Entity N: ...' where N is
    the entity's 1-based position in the chain as numbered in their prompt, or a bare
    qualified name ('C.f')."""
    text = str(text or "").strip()
    m = PY_PATH.search(text)
    if m:
        path = m.group(1)
        rest = text[m.end():].lstrip(":").strip()
        full = f"{path}:{rest}" if rest else path
        for n in chain:
            if n == full:
                return n
        same_file = [n for n in chain if node_file(n) == path]
        return same_file[0] if same_file else path      # file is right even if entity unknown
    m = ENTITY_NUM.match(text)
    if m and 1 <= int(m.group(1)) <= len(chain):
        return chain[int(m.group(1)) - 1]
    name = ENTITY_NUM.sub("", text)
    for n in chain:
        q = n.split(":", 1)[1] if ":" in n else ""
        if name and (q == name or q.endswith("." + name)):
            return n
    return None


def round_answers(analyses, key, chain):
    """Each valid agent's top location (first 'high'-priority one, else the first), as a
    file. Returns (files, n_unresolved)."""
    files, unresolved = [], 0
    for a in analyses:
        locs = (a.get("analysis") or {}).get(key) or []
        if not locs:
            continue
        top = next((l for l in locs if str(l.get("priority", "")).lower() == "high"), locs[0])
        node = resolve_location(top.get("entity_id"), chain)
        if node is None:
            unresolved += 1
        else:
            files.append(node_file(node))
    return files, unresolved


def majority(files):
    if not files:
        return None, None
    (top, n), = Counter(files).most_common(1)
    return top, n / len(files)


def load_gold():
    files = {}
    with open(MOATLESS) as f:
        for rec in json.load(f):
            files[rec["instance_id"]] = sorted(set(
                re.findall(r"^diff --git a/(\S+) b/", rec["golden_patch"], re.M)))
    entities = {}
    for path in glob.glob(RQ1_RAW):
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                entities[r["instance_id"]] = sorted(
                    {e for g in r["gold_files"].values() for e in g.get("entity_nodes", [])})
    return files, entities


def node_file(nid):
    return nid.split(":", 1)[0]


def hits(chain_nodes, gold_files, gold_entities):
    return {"file": any(node_file(n) in gold_files for n in chain_nodes),
            "entity": any(n in gold_entities for n in chain_nodes) if gold_entities else None}


def latest_cache(run_dir, iid):
    paths = sorted(glob.glob(os.path.join(run_dir, "stage_cache", iid, "*_pipeline_cache.json")))
    if not paths:
        return None
    with open(paths[-1]) as f:
        return json.load(f)


def data(cache, stage):
    return (cache.get(stage) or {}).get("data") or {}


def score_instance(rec, cache, gold_files, gold_entities):
    s = {"instance_id": rec["instance_id"], "status": rec["status"], "seconds": rec.get("seconds"),
         "gold_files": gold_files, "n_gold_entities": len(gold_entities)}

    tok = {"graph_walk": 0, "vote": 0, "debate": 0, "other": 0}
    for stage, v in rec.get("tokens", {}).get("by_stage", {}).items():
        tok[STAGE_GROUP.get(stage, "other")] += v["prompt_tokens"] + v["completion_tokens"]
    s["tokens"] = tok
    s["tokens_total"] = sum(tok.values())
    s["llm_calls"] = rec.get("tokens", {}).get("total", {}).get("calls")
    s["llm_errors"] = rec.get("tokens", {}).get("total", {}).get("errors")
    s["truncated"] = rec.get("tokens", {}).get("total", {}).get("truncated")
    if rec["status"] != "ok" or cache is None:
        s["error"] = rec.get("error") or "no stage cache"
        return s

    built = [c["chain"] for c in data(cache, "stage_3_localization_chains").get("all_chains", [])
             if c.get("chain")]
    kept = [c["chain"] for c in data(cache, "stage_4_diverse_chains").get("selected_chains", [])
            if c.get("chain")]
    s["n_chains_built"], s["n_chains_kept"] = len(built), len(kept)
    # One chain attempt per stage-2 start entity; an attempt is empty mostly because the LLM
    # proposed an entity id that is not in the graph (a hallucinated file or function).
    attempts = [c for g in data(cache, "stage_3_localization_chains").get(
        "grouped_localization_chains", []) for c in g.get("localization_chains", [])]
    s["n_chain_attempts"] = len(attempts)
    s["n_start_entities_not_in_graph"] = sum(
        1 for c in attempts if c.get("error") == "Entity not found in graph")
    s["n_chain_attempts_empty"] = sum(1 for c in attempts if not c.get("chain"))
    for name, chains in (("built", built), ("kept", kept)):
        h = [hits(c, gold_files, gold_entities) for c in chains]
        s[f"{name}_has_gold_file"] = any(x["file"] for x in h)
        s[f"{name}_n_chains_with_gold_file"] = sum(x["file"] for x in h)
        s[f"{name}_has_gold_entity"] = any(x["entity"] for x in h) if gold_entities else None

    v6 = data(cache, "stage_6_voting_result")
    vote = v6.get("voting_result") or {}
    winner = (v6.get("winning_chain") or {}).get("original_chain_info", {}).get("chain", [])
    s["winning_chain_id"] = v6.get("winning_chain_id")
    s["winner_is_chain_1"] = v6.get("winning_chain_id") == "chain_1"
    h = hits(winner, gold_files, gold_entities)
    s["selected_has_gold_file"], s["selected_has_gold_entity"] = h["file"], h["entity"]
    s["votes_for_winner"] = vote.get("winning_votes")
    s["valid_votes"] = vote.get("total_valid_votes")
    s["invalid_votes"] = len(vote.get("invalid_votes") or [])
    s["vote_agreement"] = (vote["winning_votes"] / vote["total_valid_votes"]
                           if vote.get("total_valid_votes") else None)
    s["vote_mean_confidence"] = vote.get("average_confidence")
    s["vote_distribution"] = vote.get("vote_distribution")

    r1 = data(cache, "stage_7_round1_analysis").get("first_round_analyses") or []
    r2 = data(cache, "stage_7_round2_analysis").get("second_round_analyses") or []
    s["debate_round1_valid"] = sum(1 for a in r1 if a.get("analysis"))
    s["debate_round2_valid"] = sum(1 for a in r2 if a.get("analysis"))
    # The debate's answer before and after: round-1 majority file (five independent
    # proposals, before any exchange) vs round-2 majority vs the final plan's first file.
    f1, u1 = round_answers(r1, "modification_locations", winner)
    f2, u2 = round_answers(r2, "refined_modification_locations", winner)
    s["round1_files"], s["round2_files"] = f1, f2
    s["unresolved_locations"] = u1 + u2
    s["round1_answer"], s["round1_agreement"] = majority(f1)
    s["round2_answer"], s["round2_agreement"] = majority(f2)

    plan = (data(cache, "stage_8_edit_agent_prompt").get("modification_plan") or {}).get(
        "final_plan") or {}
    # The plan writes each step's location in no fixed format ("File: a/b.py, Function: f",
    # "a/b.py:C.f", or just a name), so take any .py path, else resolve against the chain.
    plan_files = []
    for step in plan.get("modifications") or []:
        ctx = str(step.get("context", ""))
        found = PY_PATH.findall(ctx)
        if not found:
            node = resolve_location(ctx.replace("Function:", "").strip(), winner)
            found = [node_file(node)] if node else []
        for f in found:
            if f not in plan_files:
                plan_files.append(f)
    s["plan_files"] = plan_files
    s["acc1_file"] = bool(plan_files) and plan_files[0] in gold_files
    s["plan_has_gold_file"] = any(f in gold_files for f in plan_files)
    before, after = s["round1_answer"], plan_files[0] if plan_files else None
    if before and after:
        b, a = before in gold_files, after in gold_files
        s["debate_effect"] = ("unchanged_right" if before == after and b else
                              "unchanged_wrong" if before == after else
                              "fixed" if a and not b else
                              "broke" if b and not a else "changed_wrong")
    elif before and not after:
        # every agent answered but the final discriminator produced no plan (usually its
        # JSON failed to parse): the answer is lost after the debate, not by it
        s["debate_effect"] = "plan_failed_after_right" if before in gold_files else "plan_failed_after_wrong"
    else:
        s["debate_effect"] = None
    return s


def rate(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return {"n": len(vals), "rate": round(sum(map(bool, vals)) / len(vals), 3) if vals else None}


def summarize(rows):
    ok = [r for r in rows if r["status"] == "ok" and "error" not in r]
    summ = {"n_instances": len(rows), "n_ok": len(ok),
            "errors": Counter(r.get("error", "")[:80] for r in rows if r not in ok)}
    for k in ("built_has_gold_file", "kept_has_gold_file", "selected_has_gold_file",
              "acc1_file", "plan_has_gold_file", "built_has_gold_entity",
              "kept_has_gold_entity", "selected_has_gold_entity", "winner_is_chain_1"):
        summ[k] = rate(ok, k)
    # recall lost at the diversity filter, and selection precision given kept
    kept_gold = [r for r in ok if r.get("kept_has_gold_file")]
    summ["selection_given_kept_file"] = rate(kept_gold, "selected_has_gold_file")
    built_gold = [r for r in ok if r.get("built_has_gold_file")]
    summ["kept_given_built_file"] = rate(built_gold, "kept_has_gold_file")
    n = len(ok) or 1
    summ["mean_tokens"] = {k: round(sum(r["tokens"][k] for r in ok) / n)
                           for k in ("graph_walk", "vote", "debate", "other")}
    summ["mean_tokens_total"] = round(sum(r["tokens_total"] for r in ok) / n)
    summ["mean_seconds"] = round(sum(r["seconds"] for r in ok) / n, 1)
    summ["mean_vote_agreement"] = round(sum(r["vote_agreement"] or 0 for r in ok) / n, 3)
    summ["instances_with_dropped_debate_agent"] = sum(
        1 for r in ok if r["debate_round1_valid"] < 5 or r["debate_round2_valid"] < 5)
    summ["instances_with_invalid_votes"] = sum(1 for r in ok if r["invalid_votes"])
    summ["debate_effect"] = Counter(r.get("debate_effect") for r in ok)
    for k in ("round1_agreement", "round2_agreement"):
        vals = [r[k] for r in ok if r.get(k) is not None]
        summ[f"mean_{k}"] = round(sum(vals) / len(vals), 3) if vals else None
    summ["unresolved_locations"] = sum(r.get("unresolved_locations", 0) for r in ok)
    att = sum(r.get("n_chain_attempts", 0) for r in ok)
    summ["start_entities_not_in_graph"] = {
        "n": sum(r.get("n_start_entities_not_in_graph", 0) for r in ok), "of_attempts": att}
    return summ


def main(run_dirs):
    gold_files, gold_entities = load_gold()
    for run_dir in run_dirs:
        rows = []
        with open(os.path.join(run_dir, "raw.jsonl")) as f:
            for line in f:
                rec = json.loads(line)
                iid = rec["instance_id"]
                rows.append(score_instance(rec, latest_cache(run_dir, iid),
                                           gold_files.get(iid, []), gold_entities.get(iid, [])))
        with open(os.path.join(run_dir, "scores.jsonl"), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        summ = summarize(rows)
        with open(os.path.join(run_dir, "summary.json"), "w") as f:
            json.dump(summ, f, indent=2)
        print(f"== {os.path.relpath(run_dir, ROOT)}")
        print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])

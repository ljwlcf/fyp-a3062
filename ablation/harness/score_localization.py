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
import math
import os
import re
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # for instances.py
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
ENTITY_NUM = re.compile(r"[Ee]ntity[\s_#-]*(\d+)\s*:?\s*")  # "Entity 3: ...", "entity_3", "Entity #3"
PY_PATH = re.compile(r"([\w./-]+\.py)")


def resolve_location(text, chain):
    """Map an agent's free-text location onto a winning-chain node id, or None.
    Agents write it four ways: a full node id ('a/b.py:C.f'), 'Entity N: ...' or 'entity_N'
    where N is the entity's 1-based position in the chain as numbered in their prompt, or a
    bare qualified name ('C.f')."""
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


def _load_lenient_parser():
    """The fork's lenient JSON parser (_a3062_loads), loaded from its source so a saved reply can
    be replayed exactly as a --lenient-json run would parse it. None if the fork lacks it."""
    path = os.path.join(ROOT, "swe-debate", "localization", "entity_localization_pipeline.py")
    src = open(path).read()
    start = src.find("from collections import Counter as _A3062Counter")
    end_marker = 'raise ValueError("unparseable JSON in reply")'
    if start == -1 or end_marker not in src:
        return None
    ns = {"json": json, "os": os}
    exec(src[start:src.index(end_marker) + len(end_marker)], ns)
    return ns


LENIENT = _load_lenient_parser()


def _strip_fence(text):  # what every parse site in the pipeline does before json.loads
    text = (text or "").strip()
    text = text[7:] if text.startswith("```json") else text
    return text[:-3] if text.endswith("```") else text


def truncation(rec):
    """Calls cut off at max_tokens (finish_reason == "length"), by stage, and what parsing makes
    of each cut-off reply: `released_ok` = the released strict parse still succeeds (the cut
    fell after the JSON); otherwise the lenient parser is replayed on the saved text:
    `first_value` (a complete object survived before the cut), `repaired` (json_repair closed the
    truncated JSON: a PARTIAL answer), `failed`. Needs saved replies (runs from 2026-10-02 on)."""
    by_stage, fate = Counter(), Counter()
    for c in rec.get("calls", []):
        if c.get("finish_reason") != "length":
            continue
        by_stage[c["stage"]] += 1
        text = c.get("response")
        if text is None:
            fate["no_saved_reply"] += 1
            continue
        t = _strip_fence(text)
        try:
            json.loads(t)
            fate["released_ok"] += 1
            continue
        except Exception:
            pass
        if LENIENT is None:
            fate["released_dropped"] += 1
            continue
        stats = LENIENT["A3062_PARSE_STATS"]
        before = dict(stats)
        old = os.environ.get("A3062_LENIENT_JSON")
        os.environ["A3062_LENIENT_JSON"] = "1"
        try:
            LENIENT["_a3062_loads"](t)
        except ImportError:  # json_repair not installed here: say so, do not count as failed
            fate["repair_unavailable"] += 1
            continue
        except Exception:
            pass
        finally:
            if old is None:
                os.environ.pop("A3062_LENIENT_JSON", None)
            else:
                os.environ["A3062_LENIENT_JSON"] = old
        step = next((k for k in stats if stats[k] != before.get(k, 0)), "failed")
        fate[step] += 1
    return dict(by_stage), dict(fate)


def vote_logprob_signal(rec, n_chains):
    """Order-independent confidence candidates from the votes' logprobs (runner --vote-logprobs):
    each vote's top logprobs at its chain-number token give P(chain_1..chain_n) (renormalised over
    the chain ids present); averaged over voters. Returns {} when the run has no logprobs."""
    dists, p_voted = [], []
    for c in rec.get("calls", []):
        v = c.get("vote_logprobs")
        if c.get("stage") != "vote_worker" or not v or "top" not in v:
            continue
        probs = {}
        for tok, lp in v["top"]:
            t = str(tok).strip()
            if t.isdigit() and 1 <= int(t) <= max(n_chains, 1):
                probs[int(t)] = probs.get(int(t), 0.0) + math.exp(lp)
        mass = sum(probs.values())
        if mass <= 0:
            continue
        dists.append({k: p / mass for k, p in probs.items()})
        if str(v.get("voted", "")).isdigit():
            p_voted.append(dists[-1].get(int(v["voted"]), 0.0))
    if not dists:
        return {}
    mean = {k: sum(d.get(k, 0.0) for d in dists) / len(dists) for k in range(1, n_chains + 1)}
    ranked = sorted(mean.values(), reverse=True) + [0.0]
    entropy = -sum(p * math.log(p) for p in mean.values() if p > 0)
    top = max(mean, key=mean.get)
    return {"lp_votes": len(dists), "lp_top_chain": f"chain_{top}", "lp_conf": round(ranked[0], 4),
            "lp_margin": round(ranked[0] - ranked[1], 4), "lp_entropy": round(entropy, 4),
            "lp_mean_p_voted": round(sum(p_voted) / len(p_voted), 4) if p_voted else None}


def load_gold(cfg=None):
    """Gold files from the run's own instance source (config `dataset_file`, default the fork's
    SWE-bench Verified records); gold entities only where RQ1 mapped them (the 75-instance set)."""
    from instances import load_records
    files = {iid: sorted(set(re.findall(r"^diff --git a/(\S+) b/", rec["golden_patch"], re.M)))
             for iid, rec in load_records(cfg).items()}
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
    s["truncated_by_stage"], s["truncated_fate"] = truncation(rec)
    arm = rec.get("arm") or {"name": "original"}
    s["arm"], s["n_votes_planned"] = arm.get("name"), arm.get("n_votes")
    s["debate_skipped"] = arm.get("skipped")   # adaptive arm: the trigger skipped the debate
    s["stage67_tokens"] = tok["vote"] + tok["debate"]   # what equal-token matching compares
    s["calls_by_stage"] = {k: v["calls"] for k, v in rec.get("tokens", {}).get("by_stage", {}).items()}
    s["truncated"] = rec.get("tokens", {}).get("total", {}).get("truncated")
    # Stages 1-4 taken from a reference run (run_localization --reuse-chains): the graph walk
    # was not re-run, so its tokens here are ~0; its cost is the reference run's.
    s["chains_reused_from"] = (rec.get("reused_chains") or {}).get("from")
    if rec["status"] != "ok" or cache is None:
        s["error"] = rec.get("error") or "no stage cache"
        # Upstream defect: when EVERY round-1 answer fails to parse, round 2 builds
        # ThreadPoolExecutor(max_workers=min(0, 1)) and the instance crashes. It is the extreme
        # case of agents dropped by JSON parsing: the debate collapsed completely.
        s["failure_kind"] = ("debate_collapsed" if "max_workers must be greater than 0" in s["error"]
                             else "other")
        if cache is None or not data(cache, "stage_6_voting_result"):
            return s
        # The crash comes after the vote, so stages 1-6 (graph walk, chains, vote) still count.

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
    # Position vs content: where the winner was SHOWN, where stage 4 had put it, and whether it
    # is the longest kept chain (stage 4 puts the longest first only when >6 chains were built).
    order = rec.get("chain_order") or {"mode": "fixed"}
    s["chain_order"] = order.get("mode")
    s["chain_order_seed"] = order.get("seed")
    m = re.match(r"chain_(\d+)$", str(v6.get("winning_chain_id")))
    shown = int(m.group(1)) if m else None
    perm = order.get("permutation")
    s["winner_shown_position"] = shown
    s["winner_stage4_position"] = (perm[shown - 1] if perm and shown and shown <= len(perm)
                                   else shown)
    s["winner_is_longest"] = bool(winner) and bool(kept) and len(winner) == max(map(len, kept))
    s["winner_chain"] = winner
    h = hits(winner, gold_files, gold_entities)
    s["selected_has_gold_file"], s["selected_has_gold_entity"] = h["file"], h["entity"]
    s["votes_for_winner"] = vote.get("winning_votes")
    s["valid_votes"] = vote.get("total_valid_votes")
    s["invalid_votes"] = len(vote.get("invalid_votes") or [])
    s["vote_agreement"] = (vote["winning_votes"] / vote["total_valid_votes"]
                           if vote.get("total_valid_votes") else None)
    s["vote_mean_confidence"] = vote.get("average_confidence")
    s["vote_distribution"] = vote.get("vote_distribution")
    lp = vote_logprob_signal(rec, len(kept))
    s.update(lp)
    if lp:
        s["lp_top_is_winner"] = lp["lp_top_chain"] == v6.get("winning_chain_id")

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
    voted = [r for r in rows if r.get("winning_chain_id") is not None]  # reached stage 6
    summ = {"n_instances": len(rows), "n_ok": len(ok),
            "n_debate_collapsed": sum(r.get("failure_kind") == "debate_collapsed" for r in rows),
            "errors": Counter(r.get("error", "")[:80] for r in rows if r not in ok)}
    for k in ("built_has_gold_file", "kept_has_gold_file", "selected_has_gold_file",
              "acc1_file", "plan_has_gold_file", "built_has_gold_entity",
              "kept_has_gold_entity", "selected_has_gold_entity", "winner_is_chain_1",
              "winner_is_longest"):
        summ[k] = rate(ok, k)
    # Stages 1-6 over every instance that reached the vote, including later crashes.
    summ["n_reached_vote"] = len(voted)
    for k in ("built_has_gold_file", "kept_has_gold_file", "selected_has_gold_file",
              "winner_is_chain_1", "winner_is_longest"):
        summ[f"{k}_incl_crashed"] = rate(voted, k)
    summ["split_vote_rate_incl_crashed"] = rate(
        [dict(r, split=(r.get("vote_agreement") or 0) < 0.8) for r in voted], "split")
    summ["start_entities_not_in_graph_incl_crashed"] = {
        "n": sum(r.get("n_start_entities_not_in_graph", 0) for r in voted),
        "of_attempts": sum(r.get("n_chain_attempts", 0) for r in voted)}
    # recall lost at the diversity filter, and selection precision given kept
    kept_gold = [r for r in ok if r.get("kept_has_gold_file")]
    summ["selection_given_kept_file"] = rate(kept_gold, "selected_has_gold_file")
    built_gold = [r for r in ok if r.get("built_has_gold_file")]
    summ["kept_given_built_file"] = rate(built_gold, "kept_has_gold_file")
    n = len(ok) or 1
    summ["mean_tokens"] = {k: round(sum(r["tokens"][k] for r in ok) / n)
                           for k in ("graph_walk", "vote", "debate", "other")}
    summ["mean_tokens_total"] = round(sum(r["tokens_total"] for r in ok) / n)
    summ["arms"] = dict(Counter(r.get("arm") for r in rows))
    summ["mean_stage67_tokens"] = round(sum(r.get("stage67_tokens", 0) for r in ok) / n)
    summ["mean_seconds"] = round(sum(r["seconds"] for r in ok) / n, 1)
    summ["mean_vote_agreement"] = round(sum(r["vote_agreement"] or 0 for r in ok) / n, 3)
    # what "winner shown first" would be if position did not matter
    summ["chance_winner_shown_first"] = round(sum(1 / r["n_chains_kept"] for r in ok
                                                  if r.get("n_chains_kept")) / n, 3)
    summ["instances_with_dropped_debate_agent"] = sum(
        1 for r in ok if r["debate_round1_valid"] < 5 or r["debate_round2_valid"] < 5)
    summ["instances_with_invalid_votes"] = sum(1 for r in ok if r["invalid_votes"])
    summ["debate_effect"] = Counter(r.get("debate_effect") for r in ok)
    for k in ("round1_agreement", "round2_agreement"):
        vals = [r[k] for r in ok if r.get(k) is not None]
        summ[f"mean_{k}"] = round(sum(vals) / len(vals), 3) if vals else None
    summ["unresolved_locations"] = sum(r.get("unresolved_locations", 0) for r in ok)
    lp_rows = [r for r in rows if r.get("lp_votes")]
    if lp_rows:
        summ["vote_logprobs"] = {
            "instances": len(lp_rows),
            "mean_lp_conf": round(sum(r["lp_conf"] for r in lp_rows) / len(lp_rows), 3),
            "mean_lp_margin": round(sum(r["lp_margin"] for r in lp_rows) / len(lp_rows), 3),
            "lp_top_is_winner": rate(lp_rows, "lp_top_is_winner"),
            "lp_conf_when_selection_right": round(
                sum(r["lp_conf"] for r in lp_rows if r.get("selected_has_gold_file"))
                / max(1, sum(1 for r in lp_rows if r.get("selected_has_gold_file"))), 3),
            "lp_conf_when_selection_wrong": round(
                sum(r["lp_conf"] for r in lp_rows if not r.get("selected_has_gold_file"))
                / max(1, sum(1 for r in lp_rows if not r.get("selected_has_gold_file"))), 3)}
    # Truncation at max_tokens, over ALL instances (crashed ones included): by stage, with the
    # stage's call count, and what parsing makes of the cut-off replies.
    trunc, calls, fate = Counter(), Counter(), Counter()
    for r in rows:
        trunc.update(r.get("truncated_by_stage") or {})
        calls.update(r.get("calls_by_stage") or {})
        fate.update(r.get("truncated_fate") or {})
    summ["truncated_by_stage"] = {k: f"{trunc[k]}/{calls[k]}" for k in sorted(trunc)}
    summ["truncated_total"] = f"{sum(trunc.values())}/{sum(calls.values())}"
    summ["truncated_fate"] = dict(fate)
    att = sum(r.get("n_chain_attempts", 0) for r in ok)
    summ["start_entities_not_in_graph"] = {
        "n": sum(r.get("n_start_entities_not_in_graph", 0) for r in ok), "of_attempts": att}
    return summ


def main(run_dirs):
    gold_cache = {}
    for run_dir in run_dirs:
        with open(os.path.join(run_dir, "manifest.json")) as f:
            source = (json.load(f).get("config_body") or {}).get("dataset_file")
        if source not in gold_cache:
            gold_cache[source] = load_gold({"dataset_file": source} if source else None)
        gold_files, gold_entities = gold_cache[source]
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

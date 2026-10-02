# Results — FYP A3062

Readable summary of experiment results, newest first. Raw JSON stays in `ablation/results/`.
This file is what chat, the supervisor and the report draw on, so write each entry so it makes
sense without opening the code.

Every entry names its config. A result that can't be traced to a config is not a result.

Format:

## YYYY-MM-DD — <short name> (Phase N, RQx)
Config: `ablation/configs/<file>` · Raw: `ablation/results/<file>`
Setup: backbone + checkpoint, subset, number of instances, seeds
Numbers: Acc@1 (File), chain recall@K, selection precision, tokens/instance by stage
Takeaway: one or two sentences on what this means for H1–H4 or the plan
Caveats: single seed, partial run, logged deviation, etc.

---

## 2026-10-02 — Backbone trial, interim: Qwen2.5-Coder-32B with the released parser (Phase 1, backbone choice)
Config: `ablation/configs/backbone_trial_32b_v1.yaml` · Raw + scores:
`ablation/results/backbone_trial_32b_v1/20261002-065000/` (EEE job 180342; 1 pro6000 highmem,
6 workers, 64k context via YaRN, released JSON parser). Interim: the lenient-parser pass and
both 72B passes are still running; the full comparison will replace this entry.
Provenance note: the fork was updated on disk during this run (opt-in lenient parser added);
with the option off that code path is identical, but the manifest's fork_sha is the start state.

**Numbers** (10 instances):
- Debate collapsed (all five round-1 answers unparseable, upstream crash) on 8/10; 2 completed.
- Up to the vote: gold file in built chains 10/10, kept 9/10, selected chain 7/10.
- Votes lost to unparseable JSON: up to 3 of 5 per instance; surviving votes were unanimous on
  all 10 instances, so the split-vote rate (0/10) is over surviving votes only.
- Hallucinated start entities 74/200 (37%; 7B: 22-27%).
- 0 context-overflow errors at 64k; 95 calls hit max_tokens, mostly `_prefilter_neighbors_with_llm`
  (limit 1000), whose truncated replies also fail to parse.
- 1,308 s per instance (6 sharing one GPU); 388k tokens per instance (graph walk 304k).

**Same model, lenient parser** (`20261002-073451`, job 180367, 1 pro6000, `--lenient-json`):
10/10 completed, 0 collapses; gold file built 10/10, kept 10/10, selected 8/10; Acc@1 (File) 7/10;
debate effect 7 unchanged-right, 2 unchanged-wrong, 1 lost after the debate (empty final plan),
0 changed; split votes 1/10, mean vote agreement 0.94; agents dropped on 1 instance; hallucinated
start entities 67/200 (34%); 670k tokens per instance (graph walk 555k, vote 49k, debate 66k),
3,090 s per instance with 6 workers on one GPU. Parse steps over 2,227 replies: strict 297,
prose-wrapped (first object) 1,754, repaired 140, later object 3, failed 33; 210 calls hit
max_tokens (mostly neighbour pre-filtering, limit 1000).

**Takeaway so far.** With the released parser a 32B backbone has effectively no debate: it wraps
JSON in prose, so votes and analyses are dropped. With lenient parsing it completes every
instance, but Acc@1 is no better than the 7B's (7/10) and the debate still changes no answer.
Lenient parsing also changes the graph walk (more walk steps parse, so the walk goes further:
555k walk tokens vs 304k), so the parser setting is not confined to the debate stage.
These are 1-GPU runs; under the GPU rules the 32B is rerun on 2 pro6000 (`backbone_trial_32b_v2`).

---

## 2026-10-02 — Order check: vote agreement partly reflects display order; released order helps accuracy (Phase 1, precondition)
Config: `ablation/configs/order_check_v1.yaml` · Raw + scores: `ablation/results/order_check_v1/`
(fixed: `20261002-055659` job 180271, `20261002-055750` job 180272, plus the shakeout's
`shakeout10_localization_v1/20261002-044344` job 180200; shuffled: seed 1 `20261002-060609`
job 180273, seed 2 `20261002-060810` job 180274, seed 3 `20261002-061510` job 180275) ·
Analysis: `ablation/results/order_check_v1/order_analysis.json` (`analyze_order.py`).

**Setup.** The 10 shakeout instances, 7B debugging model, all on pro6000 (highmem, 8 workers;
two hardware variants of the chip, see decisions.md). Three runs with the released chain
order, three with the kept chains shuffled before the vote (seeds 1-3, same permutation per
seed for every arm). Pre-registered pass/fail rule in decisions.md 2026-10-02.

**Numbers** (fixed, 30 instance-runs -> shuffled, 29; one shuffled run crashed, see below):
- Winner shown first: 0.77 -> 0.24 (chance 0.17).
- Winner is the longest kept chain: 0.77 -> 0.55.
- Mean vote agreement 0.89 -> 0.87; unanimous votes 0.67 -> 0.55.
- Agreement when the first-shown chain won vs another won: 0.91 / 0.83 -> 0.94 / 0.85.
- Gold file in the selected chain 0.73 -> 0.59; Acc@1 (File) 0.77 -> 0.52.
- One shuffled instance-run crashed when all five round-1 answers failed to parse
  (`debate_collapsed`, sphinx-8056, seed 1; upstream defect, decisions.md).

**Takeaway.** The check does not pass. Under shuffle the first-shown chain wins only a little
more than chance, so most of the fixed-order "position" effect was the longest chain winning on
content; but the longest chain wins less often once it is not shown first, and agreement is
still higher when the first-shown chain wins. Vote agreement therefore carries some position
signal and is not yet a clean confidence measure. Separately, the released longest-first order
is useful: shuffling cost 15-25 points of selection and Acc@1, so the order acts as a prior.

**Caveats.** 7B debugging model; 10 instances; 7 vs 22 instance-runs in the agreement split;
temperature 0.7 noise is large (shakeout runs flipped 2/10 instances). Must be repeated with
the real backbone (decisions.md), where saturation may make votes near-unanimous regardless.

---

## 2026-10-02 — Shakeout, second sample on a pro6000: same totals, different instances (Phase 1, measurement setup)
Config: `ablation/configs/shakeout10_localization_v1.yaml` · Raw + scores:
`ablation/results/shakeout10_localization_v1/20261002-044344/` (EEE job 180200, one pro6000
Blackwell, `-C highmem`, vLLM 0.30.0, `--workers 4`). Compare with the a6000 run below.

**Setup.** Identical to the a6000 shakeout except the GPU and 4 workers instead of 2. This was
the first pro6000 job (Blackwell + RAM test, decisions.md 2026-10-02).

**Numbers** (a6000 -> pro6000, 10 instances each):
- Gold file in built chains 10 -> 10; in kept chains 8 -> 9; in the selected chain 7 -> 9;
  Acc@1 (File) 7 -> 7. Same Acc@1 outcome on 8/10 instances; sympy-18189 went wrong -> right,
  sympy-13647 right -> wrong (lost at stage 4 this time).
- Debate effect: 7 unchanged-right / 3 unchanged-wrong -> 7 / 2, plus 1 new outcome: on
  sphinx-8548 all four surviving agents named a gold file (`importer.py`) but the final
  discriminator returned no plan, so a correct answer was lost after the debate. Across both
  runs the debate changed the file-level answer on 0 of 20 instance-runs.
- Winner was chain_1 in 3/10 -> 9/10. Mean vote agreement 0.86 -> 0.92.
- Agents dropped by JSON parsing: 5 -> 6 instances. Hallucinated start entities 43 -> 54 of 200.
- Tokens/instance 379k -> 351k (graph walk 76-77% in both). Context-overflow calls 5 -> 6.
- Wall clock: 387 s -> 211 s per instance with twice the parallelism; whole job 35 -> 16 min.
- Blackwell works: vLLM 0.30.0 and FlashInfer's JIT kernel ran on sm_120 with no change.
- RAM: a highmem pro6000 job gets 90 GB; 4 workers peaked at 34.8 GB (4.07 GB per worker).

**Takeaway.** Run-to-run variation at temperature 0.7 is as large as any effect seen so far:
the totals look stable (Acc@1 7/10 twice) while individual instances flip, and the chain_1
rate swung from 3/10 to 9/10. Per-instance claims need several seeds, as the design says. Two
findings repeat in both samples: the debate does not change the answer, and answers are lost
around it (stage 4, the vote, JSON parsing, the final plan) rather than by it.

**Caveats.** 7B debugging model; one seed per machine; the two runs also differ in GPU and
vLLM worker count, so they are two samples, not a controlled comparison.

---

## 2026-10-02 — Shakeout: 10 instances, 7B debugging model, a6000 (Phase 1, measurement setup)
Config: `ablation/configs/shakeout10_localization_v1.yaml` · Raw + scores:
`ablation/results/shakeout10_localization_v1/20261002-041812/` (EEE job 180175, one a6000,
vLLM 0.30.0, `--workers 2`). The earlier folder `20261002-040139` is job 180136, which ran
out of RAM after 4 instances (4 workers, 24 GB) and is kept only as a record of that failure.

**Setup.** 10 hand-picked instances (3 sphinx, 4 django, 3 sympy; every difficulty band; two
multi-file gold patches), Qwen2.5-Coder-7B-Instruct bf16, one run, pipeline as released.
Scored with `ablation/harness/score_localization.py`.

**Numbers** (rates over 10 instances):
- Gold file in ANY chain built (graph's job): 10/10.
- Still in a KEPT chain after stage 4's dissimilarity filter: 8/10, so 2 lost before any vote
  (sphinx-8548, sympy-18189).
- In the chain the vote SELECTED: 7/10, i.e. 7 of the 8 where it was still available.
- Acc@1 (File), first file of the final plan: 7/10, identical to selection on every instance.
- Debate effect (round-1 majority file vs final plan file): 7 unchanged-right, 3
  unchanged-wrong, 0 changed. Mean round-1 agreement 0.97; mean vote agreement 0.86.
- The one wrong vote with the gold chain still available (django-11999) was also the one
  split vote (2/5 for the winner); the debate did not change it.
- Winner was chain_1 (always the longest, always shown first) in 3/10.
- Agents dropped by unparseable JSON: at least one in 5/10 instances.
- Start entities not in the graph (hallucinated by stage 2): 43 of 200 attempts (22%).
- Context overflow: 5 calls failed on the 32k-token limit (4 in sympy-13647, 1 in sympy-18189),
  all in `_prefilter_neighbors_with_llm`.
- Tokens per instance: mean 379k (graph walk 290k = 77%, vote 43k = 11%, debate 46k = 12%);
  range 147k-1,092k (sympy-18189). Mean 387 s per instance with 2 in parallel.
- Job RAM peak 24.0 GB of 24 GB with 2 workers (includes reclaimable page cache); 4.07 GB per
  worker process regardless of repository.

**Takeaway.** Pattern only (7B model, n = 10, one seed), but it is the pattern the approved
plan is about: the gold location is lost at stage 4 or the vote, never by the debate; the debate
changed nothing on these instances while costing as much as the vote; and the single split vote
is exactly where adaptive debate would spend its tokens. Most of the cost is the graph walk.

**Caveats.** Debugging model, one seed, temperature 0.7 everywhere; a second sample of the same
10 instances (pro6000, job 180200) is running. Debate effect is file-level; within-file changes
are not yet measured.

---

## 2026-10-01 — Smoke test repeated on the EEE cluster: 3x faster, debate collapsed (Phase 1, setup)
Config: `ablation/configs/smoke_localization_v1.yaml` · Raw:
`ablation/results/smoke_localization_v1/20261001-092851/` (EEE job 179270) · Compare with the
MLDA run `20261001-133650` below. Scores: `scores.jsonl` / `summary.json` in each folder.

**Setup.** Same instance (sphinx-doc__sphinx-8269), same model (Qwen2.5-Coder-7B-Instruct,
bf16), same config, one run each. Differences: RTX A6000 (300 W) vs RTX 3090 (180 W cap), and
vLLM 0.30.0 (FlashInfer sampling) vs 0.9.2, forced by the two machines' drivers.

| | MLDA gpu21 | EEE a6000 |
|---|---|---|
| wall clock | 483.6 s | 158.8 s |
| LLM calls / tokens | 71 / 161,988 | 52 / 130,134 |
| chains built / kept | 12 / 6 | 7 / 6 |
| kept chains containing gold file | 1 | 3 |
| vote | 5/5 for chain_1 (has gold) | 4/5 for chain_3 (no gold) |
| valid debate answers, round 1 / 2 | 4 / 4 | 1 / 0 |
| final plan | `sphinx/builders/linkcheck.py`, correct | `sphinx/linkcheck.py` (does not exist), wrong |

**Takeaway.** The EEE pipeline runs end to end and is ~3x faster per instance. But the same
instance came out right on one machine and wrong on the other. With temperature 0.7 at every
stage and n = 1, that is within what sampling alone can do, so this says nothing about the
machines; it says single runs are meaningless here, which the design already assumes. The real
finding is the debate collapse: 4 of 5 round-1 answers and the only surviving round-2 answer
failed the pipeline's strict `json.loads` ("Invalid control character", i.e. raw newlines or
tabs inside JSON strings, typical when an agent writes code into a field), so the debate ran
on one agent, and the final plan named a file that does not exist (`sphinx/linkcheck.py`).
(Corrected 2026-10-02: first recorded as an empty plan; that was a scorer bug, since fixed.)

**Caveats.** n = 1 per machine, a 7B debugging model. Raw replies were not saved, so the
control-character diagnosis is inferred from the error text; the runner now stores every reply.
Graph pre-build on EEE CPU: sphinx 4 s, django ~50 s, sympy 157-1279 s (sympy-18189: 442k edges).

---

## 2026-10-01 — Smoke test: SWE-Debate localization runs end to end on gpu21 (Phase 1, setup)
Config: `ablation/configs/smoke_localization_v1.yaml` · Raw:
`ablation/results/smoke_localization_v1/20261001-133650/` (`raw.jsonl` = output + every LLM
call; `stage_cache/` = the pipeline's own record of all 8 stages, every vote and debate turn)
Earlier folders in the same directory are the three failed attempts that led to the fixes
(see that directory's README).

**Setup.** One instance, sphinx-doc__sphinx-8269 (gold: `sphinx/builders/linkcheck.py`,
`CheckExternalLinksBuilder.check_thread.check_uri`). Debugging backbone
Qwen/Qwen2.5-Coder-7B-Instruct, bf16, vLLM 0.9.2, one RTX 3090 on MLDA gpu21. Pipeline called
exactly as workflow.py does; graph built by the pipeline itself. Single run, single seed.
Repo `8582411`, fork `2f252f9`.

**Numbers.**
- Completed all 8 stages: 483.6 s wall clock, 71 LLM calls, 0 failed, 0 truncated.
- Tokens: 142,453 prompt + 19,535 completion = 161,988 per instance. By stage:
  graph walk (stages 1-3: entity extraction, neighbour expansion, chain building) 92,371
  (57%), of which chain building alone is 81,656; chain vote 29,148 (18%); debate (two
  analysis rounds + discriminator) 40,469 (25%).
- Chain recall: the gold file is in 6 of the 12 chains built (3 contain the gold function);
  diversity selection keeps 6 chains, of which exactly 1 contains it.
- Vote: unanimous, 5/5 for that chain, mean confidence 90.4. Selection correct.
- Final plan's first edit location: `check_uri` in `sphinx/builders/linkcheck.py`. Acc@1
  (File) correct on this instance.

**Takeaway.** The 30 Sep go/no-go is met: SWE-Debate's localization stage runs end to end
on self-hosted hardware with full token accounting, so the project stays on SWE-Debate (no
switch to LocAgent/CoSIL). The per-stage split is already informative: most tokens go to the
graph walk, not the debate, which matters for any compute-matched comparison.

**Caveats.** n = 1, one seed, a 7B debugging model rather than the real backbone; none of the
numbers above are results. Two behaviours worth counting on every future run: (1) stage 1
named entities that do not exist (e.g. `sphinx/linkcheck.py`; the pipeline drops them with a
warning), and (2) agent 2's round-1 answer was malformed JSON, so it was silently dropped and
only 4 agents debated in round 2. The winning chain was also the first-ranked and longest of
the 6 shown to the voters, so position cannot be ruled out (the ordering control in
CLAUDE.md). `total_chains_generated` reports 20 while `all_chains` holds 12; not yet checked
why.

---

## 2026-09-20 — RQ1: the graph's reachability ceiling is not the bottleneck (Phase 1)
Config: `ablation/configs/rq1_reachability_v2.yaml` · Raw: `ablation/results/rq1_reachability_v2/`
(`raw.*.jsonl`, `summary.json`, `graph_quality.json`, `manifest.*.json`)
Sensitivity arms: `..._v2_strict.yaml`, `..._v2_loose.yaml`

**Setup.** All 75 SWE-Bench-Verified-S instances (django 25, sympy 25, sphinx-doc 25), 0
failures. No LLM and no GPU. SWE-Debate's own `build_graph` (v2.3, `global_import=True`,
`fuzzy_search=True`), imported unmodified from the fork, run at each instance's base commit.
The gold patch is mapped onto graph nodes (file node, plus the innermost class/function node
spanning each changed pre-image line), and hop distance is measured from a deterministic
stand-in for stage-1 entity extraction: every non-test node whose short name appears verbatim
in the issue text (see decisions.md 2026-09-20). Reported under five edge policies, including
one faithful to `_dfs_traversal` and one that keeps only invoke edges the builder actually
resolved.

**The ceiling, such as it is.** Every gold file in all 75 instances is a Python file, is
present as a graph node, and survives the test-name filter. The gold file is reachable from an
issue-named entity within 2 hops in 96% of instances and within 4 hops in 100% (0 unreachable
under the faithful policy; 1 under dependency edges alone). The gold class or function is
reachable within 3 hops in 97%. Nothing about the graph's connectivity stops SWE-Debate from
finding the answer.

**But the number means almost nothing, which is the actual result.** Measured against the
control — how much of the repository sits inside k hops of the same entry set — the traversal
stops carrying information almost immediately:

| hops | gold FILE reached | share of repo reachable | enrichment | candidate files |
|---:|---:|---:|---:|---:|
| 0 | 42.7% |  2.1% | 20.0x |  10 |
| 1 | 86.7% | 19.7% |  4.4x |  67 |
| 2 | 96.0% | 64.7% |  1.5x | 355 |
| 3 | 97.3% | 84.2% |  1.2x | 476 |
| 4 | 100.0% | 89.2% |  1.1x | 507 |

(`no_dir` policy; enrichment is how much likelier the gold file is to be inside k hops than an
arbitrary file. 1.0x means the traversal has told you nothing.) For class/function targets the
collapse is sharper: 91.4x at hop 0, 11.3x at hop 1, 1.9x at hop 2, 1.1x at hop 3, by which
point the reachable set averages 11,032 entities. `_dfs_traversal` runs to depth 5.

**The signal is in the issue text, not the graph.** Splitting instances by entry-set size, the
bottom quartile (1-14 nodes named) reaches the gold file 61% of the time at 1 hop and 89% at
3; the top two quartiles reach 100% at 1 hop. The single hardest instance
(`sphinx-doc__sphinx-9367`, gold file unreachable through dependency edges alone) has an entry
set of one node: its issue text is a code snippet that names nothing the graph can match.

**Robustness.** The pattern is unchanged across three entry-set definitions whose median size
differs three-fold (strict 16, default 35, loose 46) and across all five edge policies,
including `resolved_only`, which drops every ambiguous invoke edge. Enrichment at hop 3 is
1.2x or lower in all fifteen combinations.

Takeaway for H1: graph grounding's contribution cannot be a reachability effect — the gold
location was always reachable. If multiple chains help, they help by *ordering* candidates,
not by making them available, and that is the mechanism the Phase 1 factorial has to isolate.
The recall/selection split matters even more than expected: chain recall is near-ceiling by
construction, so essentially all of the observed accuracy is selection precision.

Caveats: the entry set is a deterministic upper bound on stage 1, not the real LLM output, so
these are ceilings and not predictions of measured accuracy. 20 of 75 instances have at least
one changed line outside any class/function node (module-level code), so entity-level gold
sets are partial for those. Single run, but the measurement is deterministic — reachability
has no seed.

---

## 2026-09-20 — The graph is mostly unresolved name matches (Phase 1, supporting)
Config: same run · Raw: `ablation/results/rq1_reachability_v2/graph_quality.json`

`build_graph` never resolves a call to one callee. It matches the called name against the
caller's visible scope and keeps every node sharing that short name; if the name is not
visible and `global_import` is on (which is what `batch_build_graph.py` uses), it wires the
caller to every node in the repository with that name. Grouping invoke edges by
(source node, callee short name), any group larger than one is a name match that was never
resolved:

| repo | invoke edges | unresolved | largest single group | ambiguous entity names |
|---|---:|---:|---:|---:|
| django/django | 176,612 | 80.0% | 618 | 11.5% |
| sympy/sympy | 296,020 | 74.9% | 438 | 12.1% |
| sphinx-doc/sphinx | 31,515 | 77.0% |  98 | 19.4% |

Invoke edges are 77.5% of all edges. One django call site naming `get` is wired to 618
different methods. The median ambiguous group has 3-4 targets.

Also measured: the `is_test_file` filter hides 67-68% of file nodes, which is mostly the
intended test suite, but it also takes shipped production code with it — the whole of
`django/test/` (12 files: `django.test.Client`, `TestCase`, the runner), `sphinx/testing/`
(6 files), and 2-28 sympy files, mostly `autolev` parser fixtures. None of the 75 gold files
falls there, so it does not bite on this subset, but on a broader dataset those files are
automatic misses. Separately, no file in any of the 75 graphs failed to parse (0 orphan file
nodes), so the AST builder handles these repositories cleanly.

Takeaway: this is the strongest reason yet to be careful with Phase 2's primary candidate.
"Graph-grounded debate" assumes an agent can cite a checkable graph fact; four in five invoke
edges are not facts. Raised in for-chat.md. It also partly explains the reachability collapse
above — though only partly, since the `no_invokes` and `resolved_only` policies show the same
collapse, so containment and imports alone already connect most of the repository.

Caveats: the split between the local-fuzzy branch and the global fallback is not recoverable
from a finished graph, so the two are counted together as "unresolved". No claim is made about
which member of a group is the true callee.



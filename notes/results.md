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



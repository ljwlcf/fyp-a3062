# Decisions

## 2026-09-13 — Direction: compute-matched ablation, not a new system (expanded 2026-09-19)
The published SWE-Debate ablation already exists (chains -10.0, edit plan -6.0,
debate -4.2). The gap is that it isn't compute-matched, isn't factorial, reports
no cost, and is single-run. Rejected: building a new multi-agent GraphRAG system.
That ground is occupied by LocAgent, CoSIL, OrcaLoca, KGCompass, Prometheus.

## 2026-09-13 — Scope: localization only
Excludes MCTS patch generation and end-to-end Pass@1. Both factors of interest
live in the localization stage. Removes the Docker test-harness dependency and
most API cost. Cost: not comparable to published Pass@1 numbers. Needs A/P Chen's
agreement.

## 2026-09-13 — Backbone fixed at DeepSeek-V3-0324 (superseded 2026-09-19)
Varying the model would reintroduce the confound the project exists to remove.

## 2026-09-13 — No GPU allocation (superseded 2026-09-19)
Inference is API-side. Ask NTU for a persistent CPU node instead.

## 2026-09-13 — Caveat on the single-backbone decision, found via literature review
The single-DeepSeek-V3-0324-backbone decision above (agents differ only by system
prompt, matching SWE-Debate's own setup) may itself suppress any debate benefit,
independent of and prior to compute-matching. ColMAD (arXiv:2510.20963)'s
homogeneous-debater ablation found even its incentive-redesigned debate protocol
fails to beat a single agent when both debaters share the same LLM — heterogeneity,
not protocol design alone, was necessary in their setting. This doesn't change the
backbone decision (SWE-Debate itself is same-model, so matching it is still correct
for isolating architecture from model effects), but it's a real threat to validity:
H2 (debate's contribution shrinks under compute matching) may be partly explained by
agent homogeneity rather than by compute-matching alone, and this is a shared
limitation with the source paper, not something A3062 introduces. Log as an explicit
threats-to-validity item in the report rather than letting it surface as a surprise
in the results. See notes/literature.md's ColMAD entry for the full argument.

## 2026-09-19 — Direction expanded to three phases after supervisor feedback
At the plan discussion, A/P Chen read the project as a reproduction of SWE-Debate and
suggested (a) testing on other datasets and (b) modifying the debate mechanism. The ablation
is now Phase 1, not the whole project:
1. Diagnose (Sem 1): reachability ceiling, reproduction, compute-matched 2x2 factorial.
2. Modify (Sem 2, first half): change the debate mechanism, chosen from Phase 1 evidence.
3. Validate (Sem 2, second half): test on a contamination-free dataset.
Working title: "Diagnosing and Improving Multi-Agent Debate for Code Fault Localization".
The earlier "no new architecture" rule is replaced by "one modification, evidence-led".

## 2026-09-19 — Gap statement corrected: SWE-Debate's debate effect is end-to-end, not localization
SWE-Debate's -4.2 debate ablation is Pass@1 on SWE-bench Verified (41.4 -> 37.2). The no-debate
37.2% is BELOW the Nature MI ~45% saturation threshold, so the two papers do not contradict
each other there. The 81.67% figure is file-level localization on SWE-bench Lite, where debate
was never ablated. Correct framing: debate's contribution to localization (~80% accuracy) under
matched compute is untested, and capability saturation predicts it is small. The submitted
plan's "difficult to reconcile" wording overstated this; use the corrected framing from now on
(notes/literature-summary.md, section 2).

## 2026-09-19 — Phase 2 modification candidates (pick ONE after Phase 1)
Primary: graph-grounded debate — agents must cite checkable graph facts and disagreements are
settled against the graph. The graph is the external signal Huang et al. show self-correction
lacks, and it costs nothing. No prior work does this.
Fallback: ColMAD's collaborative protocol (arXiv:2510.20963) WITH heterogeneous backbones. Its
own ablation shows it loses to a single agent when debaters share a model, so it only makes
sense with two model families — which complicates compute matching.
Cost-only option: adaptive stopping on round-one agreement.
Ruled out: switching to consensus-seeking debate alone (ColMAD shows it fails too). An earlier
chat suggestion to do this was wrong.

## 2026-09-19 — Phase 3 dataset: SWE-bench-Live
arXiv:2505.23419. Start from the 300-instance Lite subset and keep only issues created after
the backbone's training cutoff. Python-only, so the AST graph carries over; localization-only
evaluation needs no Docker. Multi-SWE-bench is a stretch goal (needs non-Python parsers).

## 2026-09-19 — Backbone: self-hosted open-weights model (supersedes DeepSeek-V3-0324)
DeepSeek retired the deepseek-chat alias on 24 Jul 2026 and no longer serves V3-0324 on its
own API. Plan: serve an open-weights code model at a pinned checkpoint with vLLM on NTU GPUs.
Reasons: the model cannot disappear mid-project; direct control of sampling and seeds, which
compute matching needs; heterogeneous agents become possible for the Phase 2 fallback. Exact
model depends on GPU memory. Absolute accuracy will not match the paper's; compare deltas
within the study. Optional: check whether a third-party host still serves V3-0324 for one
reproduction arm. Logged in deviations.md.

## 2026-09-19 — GPU access (supersedes "No GPU allocation")
Inference now runs on a self-hosted model, so a GPU is needed (inference only, no training). A/P Chen asked for
the MLDA GPU application first. Fallback: EEE GPU Cluster (Slurm; 48-96GB cards; 2 GPUs
concurrently for undergraduates; batch jobs up to 3 days, interactive 2h/1 GPU; login-node
processes killed on disconnect; AI coding agents must be given the cluster's agent.md digest).

## 2026-09-19 — Design controls added
- Debate round count dropped as a factor: rounds are hardcoded (2 debate rounds + 1
  discriminator). Optional extension only.
- Candidate ordering held fixed (or randomised) across all arms; LLM4FL shows ordering alone
  can move Top-1 by 22 points.
- Paired per-instance analysis (McNemar or paired bootstrap), several seeds per cell; all arms
  share instances. Expand from 75 to the 300-instance Lite set if power is marginal.
- Token count is the primary cost metric (hardware-independent). Report latency only when the
  GPU is exclusive (Slurm allocation), not on a shared workstation.

## 2026-09-19 — Literature correction: Kim et al. counted twice
"Agent Scaling Science" (arXiv:2512.08296) is the preprint of the Nature MI paper — same study.
Cite the Nature MI version only. Its SWE-bench arm is 20 instances per cell, full issue
resolution.

## 2026-09-20 — The instrumented fork stays gitignored; its changes are tracked as patches
`swe-debate/` is a clone of upstream and is gitignored, so nothing done to it was backed up or
visible to chat. Rather than vendoring 19 MB of someone else's repository into this one, the
fork now carries a local branch `a3062-instrumented` on top of upstream `8a7d462`, and every
commit on it is exported to `ablation/patches/swe-debate-instrumentation.patch`, which IS
tracked. `ablation/patches/README.md` gives the three commands that rebuild the fork from
upstream. Run manifests already record the fork's HEAD SHA, so a result can be traced to the
exact code that produced it.
Revisit if: the fork's diff grows past a few hundred lines, at which point a proper GitHub
fork plus a git submodule is cleaner. That needs a fork created under the user's account, so
it is not something to do unilaterally.

## 2026-09-20 — RQ1 entry set: issue-identifier matching, as a deterministic stand-in for stage 1
Measuring the graph's reachability ceiling needs a starting set, and SWE-Debate's real one
comes from an LLM (stage 1 extracts entity names from the issue; stage 2 expands them into
code-snippet neighbours). Running that would need the backbone, which is what the whole point
of an LLM-free ceiling is to avoid.
Decision: the entry set is every non-test graph node whose short name appears verbatim in the
issue text, matched against the same `global_name_dict` the pipeline itself uses. The LLM
cannot name an entity the issue never mentions, so this set is a superset of what stage 1 can
produce, and reachability measured from it is an UPPER bound on the real pipeline's. Reported
as such. The per-instance entry-set size is logged so the generosity is visible.
Rejected: seeding from the gold file (circular), and seeding from every node (trivially
reachable, measures nothing).

## 2026-09-20 — RQ1 reports reachability under three edge policies, not one
`_dfs_traversal` filters neighbours by edge type but not by node type, so directory nodes are
traversable and the containment tree acts as a hub: any two files in one directory are three
hops apart regardless of whether they depend on each other. Reporting a single reachability
number would hide that. Every RQ1 figure is therefore reported three ways: `all` (faithful to
the implementation), `no_dir` (directory nodes removed), and `dep_only` (imports/invokes/
inherits only, no containment at all). The gap between them is itself the result: it says how
much of the graph's apparent connectivity is dependency structure and how much is filesystem
layout.

## Still pending
- Localization-only scope: still needs A/P Chen's explicit confirmation.
- Reproduction decision point: 30 Sep 2026. If one SWE-Debate instance does not run end to end,
  run the same design on LocAgent or CoSIL.

## 2026-09-20 — Raw run outputs are tracked in git; only bulky artifacts are excluded
`.gitignore` blanket-ignored `ablation/results/`, so no result would ever have reached chat or
a backup. The RQ1 run's complete raw output for all 75 instances is about 250 KB of JSON. The
ignore is now narrowed to `ablation/results/**/*.pkl`, `**/trajectories/` and `**/*.log`, so
raw JSONL, manifests and summaries are tracked and a reported number can always be traced back
to the record that produced it. Revisit when the first LLM runs land: agent trajectories are
large and should stay under a `trajectories/` directory so the existing rule covers them.

## 2026-09-22 — GPU access secured on both MLDA and the EEE GPU Cluster (supersedes "GPU access" 2026-09-19)
Jingwei now has access to both the MLDA workstations and the EEE GPU Cluster. GPU access is
no longer a blocker for the 30 Sep go/no-go. Next: run `nvidia-smi` on each to record the card
model, memory and compute capability (vLLM needs 7.0+), then pick the backbone size to fit.
The EEE cluster's rules in CLAUDE.md (load its agent.md digest; vLLM server and harness inside
one `sbatch` job) apply whenever work runs there.

## 2026-09-22 — Proposed direction: improve the debate, not ablate it (PENDING A/P Chen's go-ahead)
Jingwei's call, following A/P Chen's comment that the ablation is already done in the SWE-Debate
paper. The project is no longer framed as an ablation study. Proposed plan, to be discussed with
A/P Chen before any engineering changes direction:
1. Understand how SWE-Debate debates: reproduce the localization stage and analyse the debate
   transcripts (do agents change their minds, is the final answer just the first vote, where do
   debates fail).
2. Modify the debate — one or two modifications done well, chosen from step 1. Targets the
   paper's own admitted weakness (five agents = one model with different prompts). Candidates:
   heterogeneous models, collaborative (ColMAD-style) instead of competitive debate,
   evidence-backed claims.
3. Test on other datasets — answers the paper's stated external threat (single Python-only
   dataset): SWE-bench-Live (post-cutoff issues) plus ONE extra language from Multi-SWE-bench
   (e.g. Java; needs a non-Python graph builder).
4. Localization is the core metric (Acc@1 File + tokens). A small end-to-end check (full
   pipeline incl. MCTS patching, ~50-75 Python instances, original vs improved debate) is a
   firm part of the plan, not optional, to show better localization also fixes more bugs.
Guard against overreach: not all languages, not three modifications.
Until A/P Chen confirms: do not start new ablation-only work (compute-matched 2x2 factorial);
the reproduction and one-instance end-to-end run (30 Sep) are needed under either plan.
Supersedes, once confirmed: the three-phase diagnose/modify/validate framing (2026-09-19) and
the scope decision "Localization only" (2026-09-13).

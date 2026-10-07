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

## 2026-09-22 — Refinement to the proposed direction (still PENDING A/P Chen)
- Lead modification: ADAPTIVE debate. Use the existing chain vote (5 agents + confidence) and,
  where available, token-level uncertainty (logprobs from self-hosted vLLM) as a trigger: clear
  vote -> accept, skip debate; split or low-confidence vote -> full debate, with the hard cases
  optionally debated by heterogeneous-model agents. Motivation: A2 (debate stops helping once a
  single agent is strong; SWE-Debate localizes ~80%), B2 (round-1 uncertainty predicts whether
  multi-agent helps). Goal: same-or-better accuracy than the original debate at fewer tokens,
  and better than an equal-token single agent.
- Keep ONE equal-token single-agent baseline as a comparison arm (not a 2x2 factorial), to
  answer "is the gain just more tokens?".
- The RQ1 graph finding (reachability near-total, invoke edges mostly unresolved) is reused in
  step 1 as supporting analysis of why debate evidence must be checkable.

## 2026-10-01 — vLLM inside an EEE cluster job is within the rules
The EEE terms forbid "serving a personal chatbot or inference endpoint from compute nodes".
Jingwei's reading: the rule targets personal use, and a vLLM server on localhost inside the
same `sbatch` job as the harness, used only by that job for FYP research, is allowed. So the
plan in CLAUDE.md (server and harness start and stop inside one job) stands on both MLDA and
the EEE cluster. Keep the server bound to localhost and never leave it running after the
harness finishes. Revisit if the cluster admins say otherwise.

## 2026-10-01 — MLDA gpu21 hardware, and what fits on it
Measured by Jingwei with `nvidia-smi` on 2026-10-01: 4x NVIDIA RTX 3090, 24 GB each, Ampere
(compute capability 8.6), driver 565.57.01 (CUDA up to 12.7), power capped at 180 W. vLLM,
bf16 and FlashAttention-2 are all supported. MLDA allows 1-2 GPUs per user, so 24 GB or 48 GB.
What fits: a 7-8B model in bf16 on one GPU; 14B in bf16 on two; 32B only 4-bit quantized
(AWQ/GPTQ) on two. 32B in bf16 does not fit. The 180 W cap makes generation slower than a
stock 3090; it does not change outputs. The workstation is shared, so latency measured here
is not reportable (decisions 2026-09-19, design controls). Which backbone to use for the real
runs is open (for-chat.md).

## 2026-10-01 — Debug runs use a 7B model on one GPU; their numbers are not results
The first end-to-end run only has to prove the pipeline works against a self-hosted endpoint.
It uses Qwen/Qwen2.5-Coder-7B-Instruct in bf16 on one 3090, which needs no decision about the
real backbone and leaves a GPU free. Instance: sphinx-doc__sphinx-8269 (single gold file,
"<15 min fix", one of the smallest graphs). Config: `ablation/configs/smoke_localization_v1.yaml`;
runner: `ablation/harness/run_localization.py`, which calls the pipeline exactly as
workflow.py does and wraps its OpenAI client to log tokens per call and per stage from the
first run onward. Setup steps: `ablation/gpu21/README.md`. vLLM and the pipeline live in
separate conda environments because they pin different torch versions. The server binds to
127.0.0.1:8765, not 8000, since other users on gpu21 may hold 8000.

## 2026-10-01 — Two graph caches: data/graphs (structure only) vs data/graphs_full (pipeline)
RQ1's `data/graphs/*.pkl` are stripped on purpose (`swe_graph.strip_graph`): node source code
is dropped because 75 full graphs are too large to cache, and RQ1 only needs structure. The
localization pipeline shows that code to the agents, so it cannot use those files; the first
smoke run died on `KeyError: 'start_line'` (start/end lines are only filled in for nodes that
carry code). Pipeline runs therefore point `GRAPH_INDEX_DIR` at `data/graphs_full/`, which
starts empty: the pipeline clones the repo at the base commit, builds the full graph with the
same builder and options RQ1 used (`build_graph(global_import=True)`), and caches it. The
full caches live on the GPU machine only and are not copied back.

## 2026-10-01 — Go/no-go met: stay on SWE-Debate
The 30 Sep decision point asked whether one SWE-Debate instance runs end to end; if not, the
design would move to LocAgent or CoSIL. On 2026-10-01 (one day late) sphinx-doc__sphinx-8269
ran through all 8 localization stages on gpu21 with a self-hosted model (results.md). The
project stays on SWE-Debate. Supersedes the "Reproduction decision point" item under Still
pending.

## 2026-10-01 — EEE GPU Cluster: what the account allows, and what it changes
Measured by Jingwei on login-1 (2026-10-01). Account `ug-proj`, default QoS `ug`: at most 2
GPUs per model at once (1 rtx5090), 2 running jobs, 5 queued. Also `override-limits-but-killable`:
up to 8 GPUs on idle cards, requeued when a regular job needs them. Budget 180,000 SU/month,
reset on the 1st (0 used).
Cluster inventory (sinfo, 2026-10-01): pro6000 (Blackwell, 96 GB) 90 GPUs on 14 nodes; a40
18; a6000 10; 6000ada 12; l40 8 (all 48 GB); rtx5090 (Blackwell, 32 GB) 20; gh200 1. At the
time of measurement every pro6000, a40 and l40 was in use, so queue waits are expected.
Billing: pro6000 480 SU/GPU-h, rtx5090 360, l40/6000ada 240, a40/a6000 180, so the monthly
budget is ~187 h on 2 pro6000, ~375 h on 2 l40/6000ada, ~500 h on 2 a40/a6000.
What it changes: 32B in bf16 (~64 GB) fits on ONE pro6000 or two 48 GB cards, so the EEE
cluster removes the "32B only 4-bit" constraint that MLDA imposes (for-chat.md backbone
question updated). Driver 595 supports CUDA 13, so the newest vLLM should work here, unlike
gpu21 (CUDA 12.7); Blackwell cards need CUDA 12.8+ builds. Each machine gets its own
environment. A/P Chen has faculty-project QoS entries on this cluster (`chen_lihui_2026_05_00`,
`_01`); membership would give project limits and budget instead of student ones (for-chat.md).

## 2026-10-01 — EEE runs: environments built in a CPU job; server and pipeline in one GPU job
`ablation/eee/setup_envs.sh` (CPU-only, free) builds both conda environments under
`/projects/fypA3062/envs` and downloads models, because the cluster forbids installs on login
nodes. `ablation/eee/run_localization_job.sh` starts vLLM on 127.0.0.1 with a per-job port
(20000 + job id mod 10000; compute nodes are shared), waits for it, runs the pipeline with
`--base-url`, and kills the server on exit via a trap. vLLM is 0.30.0 on EEE but 0.9.2 on MLDA
(driver limits), so model outputs are only comparable within one machine: every arm of a
comparison runs on the same machine and vLLM version, recorded in the run manifest.


## 2026-10-01 — A/P Chen APPROVED the new direction (confirms the 2026-09-22 proposal)
Her reply: "all three directions look good to me. We can first focus on making sure one of them
works, and then see if it's feasible to get more done if time permits." She asked for a title
and abstract for the school system by 2026-10-02.
Title: **Adaptive Multi-Agent Debate for Code Fault Localization**
The 2026-09-22 proposal and its 2026-09-22 refinement are therefore in force, superseding the
three-phase diagnose/modify/validate framing (2026-09-19) and the compute-matched 2x2 factorial
as the project's centrepiece. One equal-token single-agent baseline is kept as a comparison arm.
Priority order, per her instruction (make ONE work first):
1. Measure the debate in practice (reproduce localization, log agreement before debate, how
   often debate changes the answer and in which direction, tokens per stage).
2. Adaptive debate (skip the debate on clear, confident votes; full debate — with heterogeneous
   agents for the hardest cases — when the vote is split or uncertain).
3. Other datasets: SWE-bench-Live first, then ONE extra language (e.g. Java, Multi-SWE-bench)
   only if time permits. The abstract sent to her says "if feasible" for the second language.
4. End-to-end check on 50-75 Python instances (original vs adaptive debate) to show better
   localization also resolves more issues.
Localization-only scope is implicitly accepted (she raised no objection to the question asked in
the email), with the small end-to-end check as the exception. TODO: update CLAUDE.md to match.

## 2026-10-01 — Agents dropped by the strict JSON parser: measure first, then decide (PENDING)
The debate's parser (`_parse_modification_analysis`, and the vote's equivalent) strips a
```json fence and calls strict `json.loads`; any reply with a raw newline or tab inside a
string is discarded and that agent silently leaves the debate. With the 7B model this dropped
1/5 agents on MLDA and 4/5 in round 1 (all in round 2) on EEE, collapsing the debate. The
released code was tuned on DeepSeek-V3; a smaller backbone plus a strict parser loses agents
for formatting reasons, not reasoning ones.
Options: (a) keep the parser as released and report agent loss as a measured property of the
system (it is part of "how the debate behaves in practice", plan item 1); (b) parse leniently
(`json.loads(strict=False)`, then fall back to extracting the outermost JSON object) as a
declared deviation that changes nothing but formatting tolerance.
Decision for now: no change. The runner now stores every reply, the scorer counts valid
answers per round, and the shakeout and backbone choice will show how often it happens with
the real model. If the chosen backbone still loses agents often, adopt (b) for ALL arms,
including the original-debate baseline, and log it in deviations.md. Revisit after the shakeout.
Update 2026-10-02: the extreme case crashes the instance. When all five round-1 answers fail to
parse, `_conduct_second_round_analysis` builds `ThreadPoolExecutor(max_workers=min(0, 1))` and
raises (order check, sphinx-8056, shuffle seed 1). Not patched; the scorer counts it as
`debate_collapsed`. The same line caps round 2 at one worker, so its "parallel" agents run one
after another (latency only). Both go to deviations.md if (b) is adopted.

## 2026-10-02 — EEE GPU choice: best free GPU by a fixed priority; budget is not a constraint (SUPERSEDED same day by "GPU rules" below)
Jingwei's instruction. For every EEE job, check `sinfo` at submission and use the best GPU that
is free: pro6000 first; then rtx5090 if the model fits in its 32 GB; then 6000ada / l40; then
a6000 / a40. The 180k SU/month budget is not to be treated as a constraint. Implemented as
`ablation/eee/pick_gpu.sh [GB_NEEDED]`, which reads sinfo and skips drained nodes. It also
chooses the GPU COUNT (Jingwei, same day): for each model in priority order, the fewest cards
that cover GB_NEEDED (ceil(GB_NEEDED / card memory)), allowed only if the ug QoS permits that
many (2 per model, 1 rtx5090); the first such model with that many cards free wins, else it
queues on the first qualifying model. It prints `<model>:<count>`, used as
`sbatch --gres=gpu:$(ablation/eee/pick_gpu.sh <GB>) ...`, which overrides the job script's a6000
default. `run_localization_job.sh` then sets vLLM's `--tensor-parallel-size` to the number of
GPUs the job received. E.g. a 32B bf16 model at ~80 GB: one pro6000, or two 48 GB cards if no
pro6000 is free; it never runs on one 48 GB card (would not fit).
Consequence for comparisons: one comparison still runs on one GPU model, one GPU count and one
vLLM version (decisions 2026-10-01; tensor parallelism changes floating-point reduction order,
so 1 vs 2 cards is not numerically identical), so a run's GPU model and count are recorded in
its manifest and all arms of one comparison are submitted with the same `--gres`.
RAM per GPU (measured 2026-10-02): a6000 job 24 GB; regular pro6000 node ~33 GB per GPU
(337,920 MB allocated over 10 GPUs on gpu-pro6000-5); a pro6000 job with `-C highmem` gets
90 GB (job 180200; billed 8 SU/min = 480/h). One localization worker needs ~4.1 GB, so a6000
jobs run 2 workers and highmem pro6000 jobs can run 8+ (4 peaked at 34.8 GB). Always add
`-C highmem` on pro6000 when the job runs parallel workers.
First pro6000 job = Blackwell + RAM test: the 10-instance shakeout with 4 workers on one
pro6000 with `-C highmem`. It checks that vLLM 0.30 + FlashInfer's JIT kernel work on
Blackwell (sm_120), records the RAM a highmem pro6000 job is given and the job's peak with 4
workers (the a6000 job with 4 workers was OOM-killed at 24 GB), and gives a speed comparison on
the same 10 instances as the a6000 run (job 180175, 2 workers).

## 2026-10-02 — Serve at least a 64k context for real runs (PENDING the backbone choice)
In the shakeout, 5 calls failed because the prompt exceeded vLLM's 32,768-token limit, all in
`_prefilter_neighbors_with_llm` on sympy, where a node can have hundreds of name-matched
neighbours. The pipeline catches the error and that branch of the walk is lost. The paper used
DeepSeek-V3 through its API (64k context), so a 32k cap is our deviation, not the method's.
Plan: serve the real backbone with max-model-len >= 65,536 (Qwen2.5 models via YaRN rope
scaling, factor 2 over their native 32k; native for models that have it), log it in
deviations.md, and keep counting context-overflow errors per run (scorer: `llm_errors`).

## 2026-10-02 — Order-shuffle check is a PRECONDITION for the adaptive-debate trigger
Jingwei's proposal. Adaptive debate (CLAUDE.md plan item 2) would skip the debate when the vote
is clear, using vote agreement as the signal. But the kept chains are always shown in stage 4's
order (longest first when >6 chains built; generation order otherwise), and in the two fixed-
order shakeout runs the winner was the chain shown first in 12/20 instance-runs (chance 3.3/20)
and agreement was higher when it was (0.93 vs 0.83). Agreement may therefore partly measure
position, not confidence; under the fixed order, position and "longest" are confounded.
Rule: vote agreement may not be used as the skip trigger until this check shows it tracks
content, not display order.
Mechanism: `pipeline.chain_order` in the config (`fixed` = as released, the default) or the
runner's `--shuffle-seed N`, which permutes stage 4's kept chains before stage 5 numbers them
(display order and chain_N labels change; no chain is added, dropped or altered; the pipeline
is not modified). The permutation comes from (seed, instance_id), so one seed gives the same
permutation of positions in every arm; it is recorded per instance (`chain_order` in
raw.jsonl and `stage_cache/<instance>/chain_order.json`) and per run (the seed in the
manifest's config). The default stays `fixed`, so the baseline matches the released code. The scorer reports, per instance, the winner's shown position, its stage-4 position
and whether it is the longest kept chain; `ablation/harness/analyze_order.py` compares arms.
Note: "pro6000" nodes mix two variants of the same Blackwell chip (RTX PRO 6000 Max-Q
Workstation, 300 W, and Server Edition, 600 W); outputs are comparable, speed is not (manifests
record `gpu_names`).
Check (config `order_check_v1.yaml`, the 10 shakeout instances, 7B model, all on pro6000
highmem, 8 workers): fixed order x2 plus the earlier fixed pro6000 run (job 180200), and
shuffle seeds 1, 2, 3. Pass if, under shuffle, P(winner shown first) falls to about chance while
P(winner is longest), selection accuracy and mean agreement stay put. Fail (position bias) if
shown-first stays well above chance, or agreement is higher when the first-shown chain wins.
If it fails: every arm of every later comparison uses shuffled order with shared seeds, and the
trigger is built on agreement under shuffle (or on agreement across several shuffles). The
check must be repeated with the real backbone before the trigger is fixed.

## 2026-10-02 — Backbone trial before settling the backbone: 32B on 1 pro6000 vs 72B on 2
Proposed in a side chat, confirmed by Jingwei (Qwen2.5-72B for the large arm; 72B weights on a
new HDD folder). Before answering the backbone question in for-chat.md, run the 10 shakeout
instances (released chain order) with:
(a) Qwen/Qwen2.5-Coder-32B-Instruct @ 381fc969f78efac66bc87ff7ddeadb7e73c218a7, bf16, 1 pro6000
    (`backbone_trial_32b_v1.yaml`; ~66 GB weights);
(b) Qwen/Qwen2.5-72B-Instruct @ 495f39366efef23836d0cfae4fbe635880d2be31, bf16, 2 pro6000 with
    tensor parallelism on one node (`backbone_trial_72b_v1.yaml`; ~145 GB weights).
Both Apache/Qwen-licensed and ungated; same family, so the comparison is mostly size (code-
specialised 32B vs general 72B). Rejected: Llama-3.3-70B (gated: Meta licence and token),
Qwen3-32B (thinking mode by default, which breaks the pipeline's JSON parsing).
Both served at 65,536 tokens (native 32,768, YaRN factor 2 via vLLM --hf-overrides; with vLLM
0.30 + transformers 5 the override must set `rope_parameters` incl. rope_theta AND an already-
scaled `max_position_embeddings`, built from the model's config.json by the job script;
validated on a CPU node before use after job 180310 failed on the old `rope_scaling` form): 32k
overflowed on sympy (decisions 2026-10-02), and the paper's API allowed 64k. GPU memory
utilisation 0.95. Serving settings are job env vars, documented in each config's `serving:`
block and recorded in the run manifest.
Compare: agents dropped by JSON parsing, hallucinated start entities, Acc@1 (File), gold file
in the selected chain, split-vote rate (adaptive debate needs some disagreement; capability
saturation predicts a stronger model leaves the debate less to do), seconds and tokens per
instance. Result goes into for-chat.md's backbone question for A/P Chen.
Storage: the 150 GB SSD holds envs (14 GB) + 7B and embedding (18 GB) + the 32B (66 GB); the
72B (145 GB) cannot fit on the SSD at all, so it lives on a new HDD project folder, weights
only (`/projects/fypA3062models`, 250 GB, created 2026-10-02). Cost of that: every server
start reads 145 GB from the HDD tier (estimated 10-20 min of
billed GPU time per job; the job script now waits up to 45 min for the server). Models are
downloaded by `ablation/eee/download_models.sh` (CPU job, pinned commit, PINNED.txt beside the
weights) because run jobs are offline.
Costs: the 72B arm uses the whole 2-pro6000 allowance of the ug QoS and needs both cards on one
node, so it may queue longer and blocks other pro6000 work while it runs (budget is not a
constraint, decisions 2026-10-02). KV-cache headroom is tight in both arms (~20-27 GB after
weights, i.e. roughly 75-85k cached tokens shared by all concurrent requests), so throughput
will be lower than the 7B's; workers 6 (32B) and 8 (72B).

## 2026-10-02 — Order check outcome: FAILED (weakly); the fallback needs rethinking (PENDING)
Result (results.md 2026-10-02, order check): under shuffle the first-shown chain wins 0.24 vs
0.17 chance, but the longest chain wins less (0.77 -> 0.55), selection and Acc@1 fall
(0.73 -> 0.59, 0.77 -> 0.52), and agreement stays higher when the first-shown chain wins
(0.94 vs 0.85). By the pre-registered rule the check fails: vote agreement may NOT be used as
the adaptive-debate skip trigger as things stand.
The recorded fallback ("every later arm uses shuffled order, trigger built on agreement under
shuffle") conflicts with a finding the rule did not anticipate: the released longest-first
order raises accuracy by 15-25 points with this model, so shuffling every arm would make the
original-debate baseline worse than the released code. Not applying the fallback yet. Options
to decide with the real backbone:
(a) keep the released order for every arm (baseline = released code) and treat agreement as
    confounded; validate any trigger by checking it predicts correctness under the released
    order, with order shuffles only as a diagnostic;
(b) measure the trigger on a separate shuffled vote (costs one extra vote, ~11% of tokens) while
    the answer still comes from the released-order vote;
(c) build the trigger on a signal that does not depend on display order (token logprobs of the
    vote, or agreement across several shuffled votes).
Repeat the order check with the chosen backbone first; a near-saturated model may make votes
unanimous regardless of order. Raised in for-chat.md because it shapes the adaptive-debate claim.

## 2026-10-02 — Parser question: lenient parsing implemented as an opt-in; trial runs both ways
Evidence settling the pending parser decision: Qwen2.5-Coder-32B (backbone trial, job 180342)
lost all five round-1 debate answers on its first two instances because it wraps JSON in prose;
the instance then crashed (`debate_collapsed`). With the released parser, a 32B backbone gives
no debate at all, so Acc@1 and debate effects cannot be measured.
Done: option (b) from the 2026-10-01 entry, as a fork option that is OFF by default
(deviations.md 2026-10-02). The backbone trial therefore runs twice per model: the current
runs (released parser) measure agent loss and everything up to the vote; a second run with
`--lenient-json` measures Acc@1, the debate's effect and dropouts that remain. The scorer now
keeps stage 1-6 metrics for instances that crash after the vote. Which setting the main
experiments use is decided after both trial passes (it must be the same in every arm).

## 2026-10-02 — GPU rules (supersede "EEE GPU choice: best free GPU..." and its GPU-count update)
Confirmed by Jingwei. For every EEE run:
1. All arms of one comparison run on the same GPU model and GPU count, decided once per
   comparison (run `ablation/eee/pick_gpu.sh` once and reuse its output for every arm).
2. 32B and 72B models always run on 2 pro6000 on one node (`--gres=gpu:pro6000:2 -C highmem`),
   no fallback; they wait in the queue.
3. Smaller models (7B debugging) also use 2 pro6000, unless `sbatch --test-only` shows a fallback
   pair (2x 6000ada / l40, then 2x a6000 / a40) finishing clearly sooner: estimated start plus
   expected run time from past manifests (`ablation/harness/runtime_estimates.py`); "clearly" =
   at least 30 min and 25% sooner.
4. Tensor parallel for 32B/72B (`PARALLEL=tp`, default); two replicas for 7B
   (`PARALLEL=dp`, vLLM `--data-parallel-size 2`).
Implemented in `pick_gpu.sh` (rewritten) and `run_localization_job.sh` (PARALLEL); the manifest
records PARALLEL. Consequence for the backbone trial: its 32B arm ran on 1 pro6000, so both
32B passes are rerun on 2 pro6000 (tensor parallel) after the 72B, as config
`backbone_trial_32b_v2.yaml`; the 1-GPU runs are kept as a record only.
Budget: still not treated as a constraint.
Is the plan practical? Measurement under way:
(a) History: `sacct -a` only shows our own jobs, and this Slurm has no `Reserved` field. Our 9
    single-card pro6000 jobs since 2026-10-01 waited median 10 min (p90 21, max 21); there is
    no 2-card history yet (the 72B job 180343, submitted 06:47 UTC, is the first; part of its
    wait is our own 1-card job holding one of the two pro6000 the QoS allows).
    First 2x pro6000 data point: job 180343 submitted 06:47:44, started 10:26:41 UTC
    (gpu-pro6000-9) = 3 h 39 min, of which ~2 h 40 min was our own QoS limit (a 1-card job held
    a pro6000 until 09:27) and ~59 min was the genuine wait for two free cards on one node
    (Friday 2 Oct, 17:27-18:26 SGT).
(b) Sampling: `ablation/eee/sample_gpu_wait.sh` runs on the Mac (under caffeinate, PID in
    `ablation/results/gpu_wait_v1/sampler.pid`) every 30 min for 24 h from 2026-10-02 08:35 UTC,
    logging per GPU pair the nodes with >= 2 free cards, free cards, and Slurm's estimated start
    for a 2-card job (`sbatch --test-only`, nothing submitted) to
    `ablation/results/gpu_wait_v1/samples.tsv`. Samples taken while the Mac is off NTUSECURE/VPN
    are logged as skipped and sampling continues. First sample (16:35 SGT): no pro6000 node with
    2 free cards; estimated start of 2x pro6000 in 58 h. Slurm's estimate assumes every running
    job uses its full time limit (up to 3 days here), so it is an upper bound, and it includes
    our own QoS limit. The summary by time of day, and whether the 32B/72B plan is practical,
    will be written here when the 24 h are up.
Summary (2026-10-04): the sampler logged only 10 slots, all Friday 2 Oct 16:35-20:35 SGT; 7 more
were skipped (Mac off the NTU network, 21:23-23:55 and Sat 14:16) and the Mac slept overnight
(caffeinate -i does not prevent lid-close sleep, so those slots left no record at all). In the 10
slots, pro6000 nodes with >= 2 free cards ranged 0-3 and free cards 0-10. The `sbatch --test-only`
estimates (58-66 h for 2x pro6000, flat even when 10 cards were free) are not usable: they were
computed for our own user while our own 72B chain was queued, so they mostly measured our own
backlog. Observed waits for two pro6000 on one node: 180343 59 min (Fri 17:27-18:26 SGT), 180368
31 min (Fri 19:34-20:04), 180726 13 min after its dependencies (Sat 02:35-02:48); chained jobs
180739 and 180740 started 10 s and 7 s after their predecessor ended (the lane is kept).
Verdict: the 32B/72B-on-2-pro6000 rule is practical so far (fresh acquisitions under an hour,
chained passes ~0), and chaining passes back to back is the main lever, which supports the
"chain passes" structure; bundling seeds into one job (SEEDS) is not needed while chained jobs
keep the lane. Evidence is thin (one Friday evening and one Saturday night); re-measure from real
job submit/start times as more jobs run. Final samples: ablation/results/gpu_wait_v1/samples_final.tsv.

## 2026-10-02 — max_tokens caps: keep as released, or raise where truncation is frequent? (PENDING)
Measured (results.md, backbone trial): the 7B never hits a cap (0 / 1,450 calls); the 32B
truncates about a quarter of `_prefilter_neighbors_with_llm` replies (cap 1,000 tokens:
94/372 with the released parser, 209/803 with lenient parsing) and almost nothing elsewhere
(1 node-selection call in each run). Cut-off replies are incomplete JSON: the released parser
drops them, so that branch of the graph walk is lost; with `--lenient-json`, `json_repair`
usually closes them and returns a partial neighbour list (134 of 210 in job 180367), so the walk
silently loses candidates. Why it matters: truncation depends on the backbone's verbosity, so it
biases the 32B-vs-72B comparison towards terser models, and the caps were tuned for the paper's
DeepSeek-V3, so a verbose backbone gets a weaker walk than the released system intended.
Options: (a) keep the released caps and report truncation per stage as a measured property of
the backbone (the scorer now does); (b) raise the pre-filter cap, e.g. 1,000 -> 3,000, plus any
other stage where truncation is frequent with the chosen backbone, as a logged deviation applied
to every arm (deviations.md entry required).
Decide together with the parser setting once the backbone is chosen. Not changed for the trial
runs already queued (72B, 32B v2), so the backbone comparison stays consistent; their truncation
by stage goes into the trial write-up when they finish.
Update 2026-10-02 (Jingwei leans to (b): raise caps only, no prompt edits, size from ~p99):
- Correction: a dropped pre-filter reply does not lose the branch. On a parse failure
  `_prefilter_neighbors_with_llm` falls back to `_fallback_neighbor_prefiltering` (first
  neighbour per distinct file, in list order, no model). So under the released parser truncation
  swaps the model's selection for a heuristic one; with lenient parsing a repaired reply gives a
  partial model selection instead.
- Check done: truncated pre-filter replies are per-neighbour prose before the JSON. The prompt's
  first instruction is "Analyze each neighbor entity ID..."; the 32B enumerates neighbours
  (>= 3 list items before any JSON in 87/94 and 199/209 truncated replies), the JSON starts after
  a median ~3,700 chars and is usually cut mid-list ("selected_neighbors" present in 88/94 and
  176/209). The 7B answers with JSON first in 511/511 replies (p99 436 tokens).
- Sizing: the 32B's untruncated lengths are censored at the cap (p50 ~810, p90 ~950, p99 991-994,
  i.e. the cap itself), so their p99 cannot size a new cap. Estimated full lengths (measured
  prose before the JSON + a p99-sized JSON part, at 4.67 chars/token) over all pre-filter replies:
  p50 ~875, p90 ~1,730, p99 ~1,860-1,880, max ~1,960 tokens (6 and 32 replies were cut before
  any JSON, so only >= 1,000 is known for them). Candidate: pre-filter cap 1,000 -> 2,048
  (estimated p99 rounded up), no other stage (1 truncated node-selection call in 1,773). To be
  validated in the first raised-cap run: if pre-filter truncation stays above ~1%, raise again.
- Still to do before deciding: compare truncation rates in the 72B runs. The 1,000-cap runs stay
  as the as-released record.

## 2026-10-02 — Main experiment: job structure, time limits, and resuming (run-time figures PENDING)
From a side chat, confirmed by Jingwei.
Structure: one Slurm job per arm x seed, each covering all 75 instances, chained with
`--dependency=afterany` so every pass queues once (e.g. 3 arms x 3 seeds = 9 jobs). Each job
starts and stops its own vLLM server (as now). All arms of a comparison on the same GPUs (GPU
rules, decided once per comparison).
Time limits: `--time` = expected run time + 30-50%. Billing is for elapsed time only, but a longer
request can queue longer, and running out of time loses the instances in progress (finished
instances are safe in raw.jsonl).
Resuming: `run_localization.py --resume <run_dir>` (via the job script's extra args) continues a
run in place: every instance already in its raw.jsonl is skipped (a crash such as
debate_collapsed is an outcome, not a gap); instances in progress when the job died run again;
the config must match the original on everything that changes results (model, pipeline incl.
chain order and lenient parsing, instances, graph dir), else it refuses; a torn last line is
dropped (raw.jsonl.bak kept); each continuation is recorded under `resumes` in the run's
manifest. Tested 2026-10-02 on a synthetic run folder.
Run-time estimate (from manifests, `ablation/harness/runtime_estimates.py`, now split by parser
setting and GPU count): Qwen2.5-Coder-32B on ONE pro6000 with lenient parsing, 6 workers: 11.3 min
per instance per worker-batch, i.e. 1.88 h per 10 instances = ~14.1 h per 75-instance pass (the
released-parser run, 5.4 h per 75, is not representative: 8/10 debates collapsed). The 2-pro6000
figure and the 1-card vs 2-card speed-up come from the 32B v2 runs (jobs 180486/180487); the
expected time and `--time` for each pass are filled in here when they finish.
Measured 2026-10-04: a 75-instance 72B pass on 2 pro6000 with 6 workers takes 7.7-8.1 h, so
`--time=12:00:00` gives +50%; chained jobs started within ~10 s of their predecessor.
Practicality note: under the GPU rules every 32B/72B job takes 2 pro6000 and the ug QoS allows 2
per user, so only ONE main-experiment job runs at a time; 9 passes run back to back, each also
waiting in the queue for two cards on one node (first measured genuine wait ~59 min; 24 h
sampling under way). Total wall time ~= 9 x (2-card pass time + queue wait).
Proposal (side chat, 2026-10-02; build next session, decide after the 24 h sampler summary):
bundle passes to cut queue handovers. Every job boundary means re-acquiring two pro6000 on one
node (first measured wait ~59 min). Let `run_localization_job.sh` take a list of seeds
(e.g. `SEEDS="2 3"`) and, holding the GPUs, restart vLLM with each seed in turn, so several
passes share one queue wait; e.g. 9 passes as 3 jobs of 3 passes, ~25-30 h per job (under the
3-day limit). Trade-off: a longer job loses more on failure (mitigated by --resume per pass) and
may itself queue longer. Seeds 2 and 3 (180739, 180740) stay separate jobs for now.
Not done (Jingwei, 2026-10-02): filling tonight's idle pro6000 gap with a 72B 10-instance order
check; 72B order checks wait for 180726's split-vote rate, as planned.

## 2026-10-02 — 72B on the other 65 instances, queued now; conditional on the parser decision
From a side chat, confirmed by Jingwei. Job 180726 (`backbone_trial_72b_rest65_v1.yaml`): Qwen2.5-72B
@495f393 on the 65 SWE-Bench-Verified-S instances not in the shakeout, with exactly the settings
of job 180343 (released JSON parser, released max_tokens caps, 64k via YaRN, 2x pro6000 -C highmem,
tensor parallel, released chain order); only change: 6 workers instead of 8 (RAM peaked at 173 of
180 GB with 8; concurrency only). With 180343 it is one full 75-instance, one-seed 72B run.
Purpose: the split-vote rate and how often the debate changes the answer at scale (does adaptive
debate have room on this backbone; is a 72B order check worth running), the first real-scale
test of time and RAM, and seed 1 of the as-released arm if the released parser is kept.
Queued behind the trial (`--dependency=afterany:180487`) and the 75-map graph build
(`afterok:180724`, CPU job, `baseline_75_v1.yaml`); `--time=14:00:00` (estimate 8-10 h: the
10-instance 72B run took ~60 min with 8 workers, 22 of the 65 are sympy, 6 workers); `--resume`
covers a time-out. CONDITION: `scancel 180726` before it starts if the 72B lenient pass (180368,
scored first) changes the parser decision.
Not yet: more 72B order-check seeds (wait for this run's split-vote rate) and the full 3-arm x
3-seed experiment (wait for the backbone, parser and caps decisions).

## 2026-10-02 — Backbone: Qwen2.5-72B; 32B 2-GPU reruns cancelled; 72B seeds queued (end of session)
Decided by Jingwei (side chat), from the backbone trial (results.md 2026-10-02):
- Backbone = Qwen/Qwen2.5-72B-Instruct @495f39366efef23836d0cfae4fbe635880d2be31, bf16, 64k via
  YaRN, 2x pro6000 -C highmem, tensor parallel. With the released parser it completed 10/10 (no
  debate collapse), selected the gold chain on 10/10, Acc@1 (File) 9/10, truncated 5.6% of
  pre-filter calls; the 32B collapsed 8/10 under the same parser and reached Acc@1 7/10 only with
  lenient parsing.
- The 32B 2-GPU reruns (180486, 180487; `backbone_trial_32b_v2.yaml`) were cancelled before they
  started: the 72B is the clear choice, so they no longer inform any decision and they would block
  the pro6000 lane. The backbone comparison therefore uses the 1-card 32B runs (180342, 180367)
  against the 2-card 72B runs. Caveat: the arms differ in GPU count (1 vs 2 pro6000; tensor
  parallel only for the 72B), which affects speed and, slightly, floating-point results; this is
  an exception to GPU rule 1 for this trial only. The 2-GPU 32B speed-up is therefore unmeasured.
- 72B "as released" arm, config `baseline_72b_released_v1.yaml` (75 instances, settings of 180343):
  seed 1 = jobs 180343 (10 instances, `backbone_trial_72b_v1`) + 180726 (65 instances,
  `backbone_trial_72b_rest65_v1`), both vLLM seed 0; seed 2 = job 180739 (SEED=2); seed 3 = job
  180740 (SEED=3). Chain: 180368 and 180724 -> 180726 -> 180739 -> 180740, each `--time=14:00:00`.
  180726 re-pointed to `afterany:180368,afterok:180724`. `SEED` is a new job-script variable
  (vLLM --seed, recorded under `serving` in the manifest); with concurrent requests vLLM is not
  bit-reproducible, so seeds are independent samples, not replays.
Conditions:
- If the 72B lenient pass (180368) changes the parser decision: cancel the queued 72B jobs
  (180726, 180739, 180740) and resubmit them with `--lenient-json` (and their results dir/config
  name noting it).
- Deferred to next session (5-job submission limit): a 75-instance shuffled-order 72B run
  (`--shuffle-seed 1`, same settings), queued after seed 3 (180740) and cancelled if 180726 shows
  almost no split votes (then a 72B order check would have nothing to measure).

## 2026-10-02 — Vote logprobs recorded as a candidate adaptive-debate trigger (instrumentation)
Why: the order check found vote agreement partly order-driven (decisions.md 2026-10-02), and the
72B votes are near-unanimous, so agreement may carry little signal; the vote's logprobs give a
graded confidence that does not depend on counting agreeing voters.
How: runner `--vote-logprobs K` (or `run.vote_logprobs`; default 0 = off, so the queued 72B runs
are unaffected). Vote calls (only) request `logprobs=True, top_logprobs=K` from vLLM; requesting
logprobs does not change what is sampled. The record keeps just the distribution at the token
holding the chain number in `"voted_chain_id": "chain_N"` (Qwen writes digits as single tokens),
under `vote_logprobs` in the call record; failures are recorded, never raised. vLLM returns
logprobs in its default `--logprobs-mode` (to be confirmed and recorded on the first real run).
Scorer: per instance, the voters' distributions over the kept chains are averaged: `lp_conf`
(probability of the top chain), `lp_margin`, `lp_entropy`, `lp_mean_p_voted`, and whether the
logprob top chain is the vote's winner; the summary compares `lp_conf` when the selection was
right vs wrong. Unit-tested with mocked replies; not yet run against vLLM (needs a GPU run with
`--vote-logprobs 10`).
Verified against vLLM 2026-10-04 (job 183231, order_72b_lenient_v1, first instance
django-11848): 5/5 votes carry the distribution at the chain-number token and the shuffle
permutation is recorded. First observation: the 72B is near-certain, e.g. P(voted chain) ~1.0
(logprob 0.0) with every alternative at ~-17 or below, so logprob confidence may saturate like
vote agreement does; judge on the full 75-instance run (lp_conf when selection right vs wrong).
Side observation for the order analysis: the vote prompt's worked example answers
`"voted_chain_id": "chain_2"` (the format template says `chain_X`). An example answer can prime
voters towards that label; check chain_2's win rate under shuffled order when the 72B order
check runs.

## 2026-10-02 — SWE-bench-Live loader; cutoff = Qwen2.5 release date (cutoff PENDING confirmation)
Built (plan item 3): `ablation/harness/swebench_live.py` downloads one SWE-bench-Live split at a
pinned revision (SWE-bench-Live/SWE-bench-Live @ b51a86422e10cfd403beb4773e5a2947953e36ec, MIT),
keeps instances created after a cutoff whose gold patch touches a .py file, and writes
instance records, an id list and a meta file to data/swebench_live/ (not in git; rebuilt from the
pinned revision). `ablation/harness/instances.py` is now the single instance source for the
runner, graph builder and scorer: with no `dataset_file` in a config it is exactly the released
path (get_moatless_instance / the fork's SWE-bench Verified records), so existing configs and the
queued runs are unaffected (rescoring a run gave an identical summary); with `dataset_file` it
reads the prepared records, and the scorer takes gold files from the run's own source.
Split sizes at that revision: test 1,000, lite 300, verified 500, full 1,888.
Cutoff: Qwen2.5's training-data cutoff is not published; its release date, 2024-09-19, bounds it
from above, so "created after 2024-09-19" is conservative. On `verified` that keeps 388/500
(104 earlier, 8 without Python in the gold patch), 96 repositories, 2024-09-19 .. 2025-04-30;
213/388 gold patches touch >= 2 files (a candidate-density proxy for H4; `difficulty` has files/
hunks/lines). Draft config `live_72b_released_v1.yaml`. Practical issue before running: 96
repositories mean 96 clones and graph builds (tens of GB in the 50 GB home); start with a pilot
slice and decide where repos live. Confirm the cutoff choice (Jingwei / chat) before Live runs.

## 2026-10-02 — Equal-token single-agent arm = self-consistency, budget matched per instance
Decided by Jingwei from four options (one-shot, self-consistency, self-refinement, long CoT).
All arms share stages 1-5 (graph walk, chains, stage 4, code); the arm replaces stages 6-7,
which cost the 72B ~97k tokens per instance (vote 47k + debate 50k).
Design: N independent votes with the RELEASED vote prompt, the released majority rule, then a
single-agent plan with no debate: one round-1 analysis (released prompt), round 2 skipped, the
released discriminator. Only released prompts, so the comparison is "debate interaction vs the
same compute spent on more independent samples". The released vote is already 5-sample
self-consistency (identical prompts), so this is "more of the same, no debate". The skipped round
passes each round-1 answer through with `modification_locations` copied to
`refined_modification_locations`, the field the discriminator reads (format only; logged here).
Budget: per instance, the as-released arm's stage 6-7 tokens on that instance (mean over the
reference runs listed in the config); N = round((budget - plan_cost) / vote_cost) with per-call
costs from the same records, clamped to [5, 30]; instances without a reference get the median N
(labelled). For the 72B this gives N = 9-10. Achieved stage 6-7 tokens are recorded per instance
(`stage67_tokens`) and compared with the budget after the run; matching is approximate because
each run builds its own chains.
Implementation: runner `pipeline.arm` (default original); stages swapped on the pipeline object
only (`apply_arm`), pipeline file unchanged; unit-tested (vote gets N, plan gets 1, released
round 2 not called). Draft config `baseline_72b_selfconsistency_v1.yaml` (fill budget_reference
with the as-released seeds first).
Caveat: with one plan agent, one unparseable reply leaves the discriminator nothing, so this arm
is more fragile under the released parser than the 5-agent original; the parser setting must be
the same in every arm. The same single-agent plan step is the "skip" branch of adaptive debate.

## 2026-10-04 — Main experiment: lenient parsing for every arm; released max_tokens caps
Decided by Jingwei (settles the 2026-10-01/10-02 parser entry and the 2026-10-02 caps entry).
- Parser: the fork's opt-in lenient JSON parsing (`pipeline.lenient_json: true`) in EVERY arm of
  the main experiment. Evidence (results.md 2026-10-04): with the 72B the released parser drops
  agents on ~75% of instances and lost 12/225 answers (~5%) when it rejected the discriminator's
  reply; these are formatting failures that confound what is measured (the debate's contribution
  and the adaptive trigger), and the single-agent arm (one plan agent) would be hit hardest. The
  three released-parser 72B seeds stay as an "as released" reference row. Deviation logged
  (deviations.md 2026-10-02, now adopted for the main experiment).
- Caps: keep the released max_tokens caps. The 72B truncates 4.1% of pre-filter replies and <1%
  elsewhere; truncation is reported per stage as a measured property; no deviation.
Queued (one continuous pro6000 chain, each job keeping the lane; --time 12 h, measured pass
7.7-8.1 h): original arm lenient seed 1 -> 75-instance shuffled-order run (lenient, seed 1, plus
vote logprobs) -> original arm lenient seeds 2, 3. Plus a free CPU job preparing SWE-bench-Live
(dataset at the pinned revision + full graphs for the 40-instance pilot). Next session: the
self-consistency arm x 3 seeds (`baseline_72b_sc_lenient_v1.yaml`; budgets from all
baseline_72b_lenient_v1 runs via a glob resolved at job start), held back by the 5-job limit.

## 2026-10-04 — SWE-bench-Live set: 386 runnable instances (1 duplicate, 1 too large)
The pinned `verified` split lists conan-io__conan-18153 twice (identical records); the loader now
drops exact duplicates (387 unique after the cutoff and Python filters) and the runner's instance
list removes repeats. Azure__azure-sdk-for-python-40487 is excluded via the config's
`instances_exclude`: its code graph needs more than 40 GB of RAM to build (job 183289,
MemoryError under the per-graph cap), so pipeline workers could not load it either. All other 386
full graphs are built on EEE (data/graphs_live, 3.9 GB; clones 13 GB in total in data/repos).
Graph-build robustness added on the way: fetch a base commit by sha when it is not on the cloned
branches (a LLaMA-Factory commit), build each graph in a memory-capped subprocess, record and
skip failures (build_failures.json), write graphs atomically; the build job now has 48 GB.

## 2026-10-04 — Extra pro6000 work runs under the killable QoS (second lane, no cost to the first)
Checked (sacctmgr, sbatch --test-only, live submission): `override-limits-but-killable` has its own
limits (8 GPUs, no running-job cap, its own 5-job submit limit) separate from `ug` (2 per model, 2
running, 5 submitted); confirmed by submitting 2 killable jobs while 4 ug jobs were queued (6
accepted). It runs at priority 0 on idle cards only, and `ug` jobs (including our own) preempt it
(PreemptMode REQUEUE; cluster JobRequeue=1). So it adds capacity without touching the ug pro6000
lane, at the cost of running only when pro6000 cards are idle and possibly being requeued.
Jingwei: use it when it adds work without affecting normal usage; keep pro6000 as the GPU (GPU
rules). Requeue safety: `run_localization_job.sh` detects SLURM_RESTART_COUNT > 0, finds the run
folder whose manifest has this job id and passes `--resume`; killable jobs are submitted with
`--requeue --open-mode=append` so the log survives a requeue.
Also fixed: `pick_gpu.sh` now treats a GPU model as unavailable when our own running/pending jobs
already fill its ug limit (it had picked pro6000 for a 7B while our chain held both pro6000 slots
for ~30 h, because Slurm's estimates are dominated by our own queue).
Submitted under killable (2x pro6000 -C highmem): 183679 72B Live pilot (live_pilot40_lenient_v1,
40 instances, lenient, 8 h). The 7B SWE-bench-Live smoke test (live_pilot40_7b_lenient_v1,
PARALLEL=dp, 2 h; catches Live-specific bugs, not a result) was first queued under killable
(183678) and then moved to the free 5th ug slot on 2x l40 (183697; GPU rule 3 fallback, pro6000
blocked by our own chain; the card does not matter for a code-path smoke test), at Jingwei's
request to use every free ug slot.

## 2026-10-04 — GPU rules updated: pro6000 first, killable pro6000 before any other card
Jingwei ("always use pro6000"). Supersedes rule 3 of "GPU rules" (2026-10-02): small models (7B)
get 2 pro6000 under ug if our ug pro6000 limit is free, otherwise 2 pro6000 under the killable QoS
(override-limits-but-killable; separate limits, idle cards only, requeued by regular jobs, our job
script resumes after a requeue); another card model only on explicit request (ALLOW_FALLBACK=1).
Rules 1, 2 and 4 unchanged (32B/72B main passes: 2 pro6000 under ug, chained, never preempted).
`pick_gpu.sh` rewritten accordingly; it counts only our ug jobs against the ug limit. The 7B Live
smoke test therefore moved from 2x l40 (183697, cancelled) to killable pro6000 (183710), and the
freed 5th ug slot holds the self-consistency arm seed 1 (183711, `baseline_72b_sc_lenient_v1`,
2x pro6000, after 183310 so its budget glob sees all three lenient seeds).
Housekeeping: the cancelled lenient seed-1 run (183230, 1 instance, pre-fix code) was moved on EEE
from `ablation/results/baseline_72b_lenient_v1/20261004-064319` to
`ablation/results/_discarded/baseline_72b_lenient_v1/` (with a README), so the self-consistency
budget glob and any seed pooling cannot pick it up. Discarded runs go under `_discarded/` from now.
Run-time estimates now split pro6000 editions (Max-Q 300 W vs Server 600 W; same outputs, different
speed); all 72B runs so far ran on Server Edition (6.1 min per instance with the released parser,
5.6 lenient, per worker batch).
Usage: 29,961 SU billed 2026-10-01 .. 10-04 (16.6% of the 180,000 SU monthly quota; 62 pro6000
GPU-hours, 1 a6000).

## 2026-10-05 — Order check repeated at 72B: agreement passes, the vote's winner choice has a primacy bias
Outcome against the pre-registered rule (2026-10-02): (i) under shuffle the first-shown chain still
wins more than chance (0.29 vs 0.17; a monotonic gradient over positions 1..6), so display order
does bias WHICH chain wins; (ii) vote agreement is the same under both orders (0.95 / 0.96) and is
not higher when the first-shown chain wins, so agreement is not a position artefact at 72B.
Consequences: (1) agreement may be used as a trigger signal as far as order is concerned, but it
is saturated (~88% unanimous), so on its own it would skip the debate almost always; (2) vote
logprobs (lp_conf) are less saturated and separate right from wrong selections somewhat, so the
adaptive-debate trigger is to be built and evaluated on lp_conf (with agreement as a comparison),
on the lenient seeds once all three are in; (3) the primacy bias is itself a finding about the
released vote and a threat to validity for chain-order-sensitive comparisons: keep the released
order in every arm (baseline = released code) and report the shuffled run alongside. The earlier
"shuffle every arm" fallback is dropped (shuffling also cost a few accuracy points at 7B and 72B).
Killable lane in practice: the 7B Live smoke test ran on idle pro6000 (25 min); the 72B Live pilot
(183679) has been preempted and requeued 3 times and resumed each time (15/40 done so far).


## 2026-10-05 — Always keep both lanes full (ug and killable)
Jingwei: "always utilise both ug and killable lanes". Standing rule, extending 2026-10-04: the
normal ug lane stays full (5 submitted, chained 2x pro6000 main-experiment passes) AND the
killable lane stays full (override-limits-but-killable: its own 5-submit / 8-GPU limits, idle
pro6000 only, preempted jobs requeue and resume through the job script). Whenever a slot frees in
either lane, the next useful requeue-safe job goes there. Main-arm passes stay on ug (they must
not be preempted mid-comparison); the killable lane takes Live, repairs and extra seeds.
First use: the rest of the 72B SWE-bench-Live seed, split into three parts so it fills three
killable slots: `live_72b_lenient_{a,b,c}_v1` (id-file lines 40:155, 155:270, 270:387; 115+115+116,
with the 40-instance pilot = all 386), same backbone, serving and parser as the pilot, plus vote
logprobs (no output change), jobs 184607-184609, 16 h limit each. If chat moves the Live cutoff
later, the later set is a subset of this one (filter by created_at); no rerun needed.

## 2026-10-05 — Adaptive-debate trigger evaluated by offline replay first
Both branches of adaptive debate exist inside every original-arm run on the same winning chain,
so the trigger is evaluated by replay (`ablation/harness/replay_trigger.py`) before any adaptive
arm is run on the GPU: full branch = the run's final plan; skip branch = the single-agent plan step
(2026-10-02), replayed as one round-1 agent's top file (the five round-1 agents have identical
prompts, so expected value over them), cost = vote + one round-1 call + the discriminator
(conservative). Thresholds are chosen on other runs (held out) when several exist; paired bootstrap
over instances. Validity check pending: the self-consistency runs run the real skip step, so the
discriminator's pass-through of a lone round-1 file is measured there (`--sc`). A real adaptive arm
on the GPU follows once the triggered branch is settled (for-chat.md). First outcome: results.md
2026-10-05 (skip-always is no worse; errors are selection failures the plan debate cannot reach).

## 2026-10-06 — Arms can reuse a reference run's chains (stages 1-4): proposed protocol for arm comparisons
Observed: each run re-walks the graph, so arms differ in their chains as well as in the arm
itself (self-consistency seed 1 kept the gold file in 0.867 of instances vs 0.92-0.93 for the
original seeds), which blurs the per-instance paired comparison the design relies on.
Built: `run_localization.py --reuse-chains REF_RUN_DIR` (sets `pipeline.reuse_chains_from`,
recorded in the manifest and in each record as `reused_chains`, compared on resume). Stages 1-4
(start entities, related entities, chains, stage-4 selection) come from the reference run's stage
cache; stage 5 (code lookup, no LLM) runs live, so chain_order still applies. Tested: replaying
stages 1-4 reproduces stage 3 and 4 exactly on all 75 seed-1 instances with no LLM call, and the
shuffle still permutes on top; one instance end to end on MLDA gpu21 (7B, smoke_reuse_chains_v1):
stages 1-5 identical to the reference, 16 calls (vote 5, round 1 5, round 2 5, discriminator 1).
Proposed use (Jingwei to confirm): every non-original arm (self-consistency, adaptive) runs once per
original seed k with `--reuse-chains <original seed k>`, so arm vs original is a comparison on
identical chains, and each arm run costs ~25% of the tokens / GPU time of a full run. Costs are
reported as the reference's stages 1-5 plus the arm's own stages 6-8. Self-consistency seed 1 and
the running seed 2 used independent chains; they stay as the independent-chain record.
Confirmed by Jingwei 2026-10-06 ("switch SC seed 3 to reuse-chains"). SC seed 3 (184575) had
already started (34/75) by then, so it was left to finish as a third own-chains seed, and the
reuse-chains SC seed 3 was queued directly after it: job 186863, `--reuse-chains
baseline_72b_lenient_v1/20261004-215633` (original seed 3), vote logprobs; lenient seed 4 now
waits on it. Every later non-original arm runs with --reuse-chains against the matching original seed.

## 2026-10-06 — Adaptive arm implemented (plan item 2): skip the debate on a unanimous vote
Arm `adaptive` in run_localization.py (`pipeline.arm: {name: adaptive, trigger: {signal:
vote_agreement, threshold: 1.0}}`, config `baseline_72b_adaptive_lenient_v1.yaml`): the released
5-agent vote; if every valid vote picked the same chain, the self-consistency arm's single-agent plan
step (one round-1 analysis, round 2 skipped, released discriminator); otherwise the released debate
unchanged. Each record's `arm` stores the observed agreement and `skipped`; the scorer reports
`debate_skipped`. Threshold 1.0 is the plain reading of "clear vote" (unanimous); it is also what the
replay supports (pooled seeds 1-3: -0.4 points, -39% stage 6-7 tokens). lp_conf is not used as the
trigger: on seed 1 it did not beat agreement and it needs the vote logprobs inside the arm. Runs
use --reuse-chains against the matching original seed (paired, ~1 h each). Unit-tested with a fake
pipeline (unanimous -> plan with 1 agent, round 2 skipped; split -> 5 agents and the released round
2; SC arm unchanged after factoring out the shared round-2 skip). Alternative skip branch kept in
reserve: five round-1 agents without round 2 (replay: same accuracy within one instance, ~70k
tokens instead of ~55k); not built unless the single-agent skip loses accuracy in the real runs.
This is the efficiency form of adaptive debate (option (a) in for-chat.md); the chain-level debate
(option (b)) still waits on chat / A/P Chen.

## 2026-10-07 — Noise-floor control and six paired seeds for the adaptive comparison
The first adaptive run lost 4 of 17 split-vote instances that both arms handled with the identical
released debate: re-running the same stage 6-8 procedure on the same chains changes answers. To read
paired discordance (adaptive vs original 2:4, SC vs original 3:8) against chance, add a noise-floor
control: the ORIGINAL arm re-run with --reuse-chains on its own seed's chains (config
baseline_72b_lenient_v1 + --reuse-chains, new results subfolder by run id; ~1.5 h each); the
original-vs-rerun discordance is the floor any arm comparison must clear. Also extend adaptive to
seeds 4-6 (reuse of lenient seeds 4-6 once they exist), giving six paired seeds (~3-3.5 point
non-inferiority margin at the observed discordance; power numbers in for-chat.md). Queued as ug
slots free; lenient seeds 4-6 stay (they are the references).

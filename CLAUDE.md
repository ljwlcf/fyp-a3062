# FYP A3062 — Adaptive Multi-Agent Debate for Code Fault Localization

## What this project is

Final Year Project at NTU (IEM), supervised by A/P Chen Lihui. Fixed dates: interim report
10 Nov 2026, draft final 25 Mar 2027, final report 9 Apr 2027, demonstration 12-16 Apr 2027,
oral 10-12 May 2027. (Project plan was submitted 14 Sep 2026.)

**Target system.** SWE-Debate (arXiv:2507.23348, ICSE 2026) localizes bugs by walking a static
code dependency graph to build candidate fault chains, then has five copies of one LLM vote on
a chain and debate a modification plan (2 debate rounds + 1 discriminator).

**Plan** (approved by A/P Chen 2026-10-01; supersedes the 2026-09-19 three-phase plan and the
2x2 factorial, see `notes/decisions.md` 2026-09-22 and 2026-10-01). Her instruction: make ONE
direction work first, then add more if time permits. Priority order:
1. **Measure the debate in practice.** Reproduce SWE-Debate's localization; log agreement
   before the debate, how often the debate changes the answer and in which direction, where the
   gold location is lost (chains built -> kept -> selected), and tokens per stage.
2. **Adaptive debate** (the lead modification). Use the vote's agreement and confidence (and
   vLLM logprobs) as a trigger: clear vote -> accept and skip the debate; split or uncertain ->
   full debate, optionally with heterogeneous agents for the hardest cases. Goal: same-or-better
   accuracy than the original debate at fewer tokens, and better than an equal-token single
   agent (the one baseline kept from the old design).
3. **Other datasets.** SWE-bench-Live (arXiv:2505.23419, post-cutoff issues) first; ONE extra
   language (e.g. Java, Multi-SWE-bench) only if feasible.
4. **Small end-to-end check:** original vs adaptive debate through MCTS patching on 50-75
   Python instances, to show better localization also resolves more issues.

**What the code actually does** (verified 2026-10-01, `notes/deviations.md`): the five agents
get identical prompts at temperature 0.7, so the vote and debate round 1 are self-consistency
sampling with one real exchange round on top (the paper says "different system prompts");
stage 4 keeps chains by dissimilarity to the longest one, not relevance, and always shows the
longest chain first.

**The gap, stated precisely.** SWE-Debate's -4.2 debate ablation is end-to-end Pass@1 on
SWE-bench Verified (41.4 -> 37.2), removes the debate's tokens along with the mechanism, and is a
single run. Debate was never ablated at the localization level (~80% accuracy), where the
Nature MI capability-saturation finding predicts it adds little. Do NOT describe this as "two
papers contradicting each other" — see `notes/literature-summary.md` section 2.

**Hypotheses.** The Phase 1 hypotheses H1-H4 (graph x debate factorial) are retired with the
factorial; their text is in git history and `notes/decisions.md` 2026-09-19. New ones for the
measurement and adaptive-debate work are still to be written (`notes/for-chat.md`).

## Scope boundaries — do not drift past these

- **Localization only**, accepted by A/P Chen 2026-10-01. Do not modify the MCTS
  patch-generation stage; its only use is the small end-to-end check (plan item 4).
- **One self-hosted backbone, pinned checkpoint, fixed across all arms of a comparison.**
  DeepSeek-V3-0324 (the paper's model) is no longer served by DeepSeek. Serve an open-weights
  model with vLLM on NTU GPUs. The only planned exception is heterogeneous agents inside
  adaptive debate. Claude is the research assistant here, never the system under test.
- **Main data:** the 75-instance SWE-Bench-Verified-S subset (django 25, sympy 25,
  sphinx-doc 25; `utils/verified75.txt` — counted 2026-09-20, correcting an earlier
  23/26/26). Expand to the 300-instance SWE-bench Lite if statistical power is marginal.
- **Python repositories only**, except ONE extra language if feasible (plan item 3), which
  needs a non-Python graph builder. The graph is built with Python's `ast` module.
- **One modification at a time:** adaptive debate first; nothing else until it works.

## Experimental design

Arms, all on the same instances: original SWE-Debate (as released), adaptive debate, and one
single-agent arm with the same token budget as the original. Debate round count is NOT a
factor (hardcoded in the implementation).

- **Hold candidate-chain ordering fixed or randomised across arms.** Ordering alone moved Top-1
  by 22 points in LLM4FL, and the released code always shows the longest chain first.
- **Paired analysis:** all arms run on the same instances, so compare per instance (McNemar or
  paired bootstrap). Several seeds per arm. Never report a single run.

### Metrics to log on every run

- Acc@1 (File), scored against gold-patch files
- Structural reachability: is the true file reachable in the graph from the entry nodes?
- Chain recall @ K: does the true location appear in ANY candidate chain (the graph's job)
- Selection precision: does the CHOSEN chain contain it, given recall (the debate's job)
- Tokens per instance, split by stage — the primary cost metric
- Wall-clock latency — only meaningful when the GPU is exclusively allocated
- Inter-agent agreement rate per debate round

The recall/selection split is a core contribution. The source paper never separates them.

## Compute

- Inference only, no training. vLLM serves the model; the harness calls it over HTTP.
- GPU: applying for MLDA workstation access first (supervisor's request). Alternative: EEE GPU
  Cluster (Slurm). On first login run `nvidia-smi`: vLLM needs compute capability 7.0+ (Volta
  or newer); bf16 and FlashAttention-2 need Ampere or newer. Older MLDA documentation lists
  GTX 1080 Ti workstations, which are too old.
- **If working on the EEE GPU Cluster:** load its AI-facing digest
  (https://github.com/NTUEEECluster/docs/blob/main/skill.md) at the start of the session and
  follow it. Never run heavy processes on login nodes (16 GB cgroup; exceeding it kills all your
  processes). Login-node processes die on disconnect, including tmux/nohup, so the vLLM server
  and the harness must start and stop inside the same `sbatch` job.

## Repository layout

```
FYP-A3062/
├── CLAUDE.md                     # this file
├── FYP_A3062_Project_Plan.md     # current plan (three phases)
├── notes/
│   ├── decisions.md              # what was decided and why (append, mark superseded)
│   ├── progress.md               # one entry per session, newest first
│   ├── results.md                # readable result summaries, each tied to a config
│   ├── for-chat.md               # open questions for chat (direction, scope, writing)
│   ├── deviations.md             # differences from the published setup (threats to validity)
│   ├── literature.md             # one entry per paper
│   ├── literature-summary.md     # plain-language gist of each paper + big picture
│   └── reading-order.md          # A/B/C/D labels matching papers/ filenames
├── papers/                       # PDFs (gitignored), named "A1 - Title (Venue).pdf" etc.
├── swe-debate/                   # instrumented fork (gitignored for now)
├── ablation/{configs,harness,results}/
└── report/
```

## Working conventions

- Every experiment run gets a versioned config file. A result that can't be traced to a config
  is not a result.
- Token accounting goes in before the first factorial pass, not after.
- Write results as raw JSON first; analyse separately.
- Log any deviation from the published SWE-Debate setup in `notes/deviations.md`.
- Debug on one instance end to end before running batches.

## Hand-off between Claude Code and chat

This repo is the single source of truth. Claude Code does the engineering and the technical
design; the claude.ai Project chat handles direction, scope, supervisor communication and
writing (reports, slides). Chat reads this folder rather than relying on a retold summary.

**At the end of every Claude Code session, before stopping:**
1. `notes/progress.md` — a new Did / Broke / Next entry at the top.
2. `notes/results.md` — an entry for any run that produced numbers.
3. `notes/decisions.md` — any decision made, with the reason; mark superseded ones.
4. `notes/for-chat.md` — any question that isn't about the code (scope, direction, what to
   tell A/P Chen, how to frame something in the report). Don't guess an answer to those here.
5. Commit and push, so chat sees the current state.

**When a session starts after a chat discussion,** read `notes/decisions.md` and the Answered
section of `notes/for-chat.md` for anything new, and follow it.

**Enforced by hooks** (`.claude/settings.json`). The SessionStart hook pulls the repo and loads
the latest progress entry and `for-chat.md` into context. The Stop hook blocks the end of any
session that changed something until progress.md has a new entry, results.md is updated when
`ablation/results/` changed, everything is committed and everything is pushed. If it blocks,
fix what it lists; don't work around it.

Switch between the two by task, not mid-task: finish a chunk of work, update the notes, then
move over.

## Known unknowns

- Whether SWE-Debate reproduces. It RUNS: one instance went end to end on 2026-10-01 (results.md),
  so the LocAgent/CoSIL fallback is off. Whether it reproduces the paper's ~80% is still open. Known defects: empty hardcoded API credentials, inconsistent model name,
  absolute cache path at filesystem root (see progress.md 2026-09-13).
- Which backbone: MLDA gpu21 gives 24-48 GB (2x RTX 3090), so 14B bf16 or 32B 4-bit there;
  the EEE cluster fits 32B bf16 (96 GB pro6000, or 2x 48 GB). Open in for-chat.md. Debug runs
  use a 7B model.
- Whether compute matching uses extended reasoning or best-of-N — depends on the chosen model.
- How to operationalize candidate density for H4. Tran & Kiela found plain distractors their
  weakest lever; SWE-bench-Live's multi-file difficulty gradient is a candidate proxy.
- Same-model agents may suppress debate regardless of compute (ColMAD). Threat to validity,
  logged in decisions.md.

# FYP A3062 — Diagnosing and Improving Multi-Agent Debate for Code Fault Localization

## What this project is

Final Year Project at NTU (IEM), supervised by A/P Chen Lihui. Fixed dates: interim report
10 Nov 2026, draft final 25 Mar 2027, final report 9 Apr 2027, demonstration 12-16 Apr 2027,
oral 10-12 May 2027. (Project plan was submitted 14 Sep 2026.)

**Target system.** SWE-Debate (arXiv:2507.23348, ICSE 2026) localizes bugs by walking a static
code dependency graph to build candidate fault chains, then has five copies of one LLM vote on
a chain and debate a modification plan (2 debate rounds + 1 discriminator).

**Three phases** (decided 2026-09-19 after supervisor feedback — see `notes/decisions.md`):
1. **Diagnose (Sem 1).** Measure the graph's reachability ceiling, reproduce the localization
   baseline, then run a compute-matched 2x2 factorial: which component does the work?
2. **Modify (Sem 2, first half).** Change the debate mechanism, ONE modification chosen from
   Phase 1 evidence. Primary candidate: graph-grounded debate (agents cite checkable graph facts;
   disagreements settled against the graph). Fallback: ColMAD's collaborative protocol with
   heterogeneous backbones. Consensus-seeking debate alone is ruled out.
3. **Validate (Sem 2, second half).** Re-test on SWE-bench-Live (arXiv:2505.23419), keeping only
   issues created after the backbone's training cutoff.

**The gap, stated precisely.** SWE-Debate's -4.2 debate ablation is end-to-end Pass@1 on
SWE-bench Verified (41.4 -> 37.2), removes the debate's tokens along with the mechanism, and is a
single run. Debate was never ablated at the localization level (~80% accuracy), where the
Nature MI capability-saturation finding predicts it adds little. Do NOT describe this as "two
papers contradicting each other" — see `notes/literature-summary.md` section 2.

**Hypotheses (Phase 1).**
- H1: graph grounding survives compute matching (it adds information, not just tokens)
- H2: debate's contribution to localization is small under compute matching
- H3: the two factors interact rather than sum
- H4: any surviving debate benefit concentrates on instances with high candidate density

## Scope boundaries — do not drift past these

- **Localization only.** Do not touch the MCTS patch-generation stage. (Still needs the
  supervisor's explicit confirmation.)
- **One self-hosted backbone, pinned checkpoint, fixed across all arms of a comparison.**
  DeepSeek-V3-0324 (the paper's model) is no longer served by DeepSeek. Serve an open-weights
  model with vLLM on NTU GPUs. The only planned exception is the Phase 2 heterogeneous-agent
  fallback. Claude is the research assistant here, never the system under test.
- **Phase 1 data:** the 75-instance SWE-Bench-Verified-S subset (django 23, sympy 26,
  sphinx-doc 26; `utils/verified75.txt`). Expand to the 300-instance SWE-bench Lite if
  statistical power is marginal.
- **Python repositories only.** The graph is built with Python's `ast` module.
- **One modification in Phase 2**, not two.

## Experimental design (Phase 1)

2x2 factorial: graph grounding (multiple chains vs single chain) x debate (multi-agent vs single
agent). Every multi-agent cell gets a compute-matched single-agent counterpart with the same
token budget (extended reasoning or best-of-N), plus compute-matched majority-vote and
self-consistency arms. Debate round count is NOT a factor (hardcoded in the implementation).

- **Hold candidate-chain ordering fixed or randomised across arms.** Ordering alone moved Top-1
  by 22 points in LLM4FL.
- **Paired analysis:** all arms run on the same instances, so compare per instance (McNemar or
  paired bootstrap). Several seeds per cell. Never report a single run.

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
  (https://github.com/NTUEEECluster/docs/blob/main/agent.md) at the start of the session and
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
│   ├── literature-summary.md     # synthesis across papers, tied to the phases
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

- Whether SWE-Debate runs and reproduces. **Decision point 30 Sep 2026**: if one instance does
  not run end to end, use the same design on LocAgent (arXiv:2503.09089) or CoSIL
  (arXiv:2503.22424). Known defects: empty hardcoded API credentials, inconsistent model name,
  absolute cache path at filesystem root (see progress.md 2026-09-13).
- Which backbone: depends on GPU memory (a 32B code model needs ~64 GB in bf16; 14B ~28 GB).
- Whether compute matching uses extended reasoning or best-of-N — depends on the chosen model.
- How to operationalize candidate density for H4. Tran & Kiela found plain distractors their
  weakest lever; SWE-bench-Live's multi-file difficulty gradient is a candidate proxy.
- Same-model agents may suppress debate regardless of compute (ColMAD). Threat to validity,
  logged in decisions.md.

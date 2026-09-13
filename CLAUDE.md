# FYP A3062 — Compute-Matched Ablation of Graph-Grounded Multi-Agent Fault Localization

## What this project is

Final Year Project at NTU (IEM), supervised by A/P Chen Lihui. Due dates are fixed by the
school: plan 14 Sep 2026, interim report 10 Nov 2026, draft final 25 Mar 2027,
final report 9 Apr 2027, oral 10-12 May 2027.

**The research question.** SWE-Debate (arXiv:2507.23348) reports SOTA on software issue
resolution by combining a static code dependency graph with a five-agent, three-round
competitive debate. Its published ablation removes multi-agent debate for a 4.2 point drop.
That ablation is not compute-matched: removing the debate also removes five agents' worth of
inference tokens. This project re-runs the ablation with the token budget held constant.

**Hypotheses.**
- H1: graph grounding survives compute matching (it adds information, not just tokens)
- H2: debate's measured contribution shrinks substantially under compute matching
- H3: the two factors interact rather than sum
- H4: any surviving debate benefit concentrates on instances with high candidate density

H4 is the risk hedge. If debate's advantage vanishes, H4 turns a null into a positive result
about when coordination is worth its cost.

## Scope boundaries — do not drift past these

- **Localization only.** Do not touch the MCTS patch generation stage. It is a third heavy
  component that neither factor of interest involves, and excluding it removes the Docker
  test-harness dependency and most of the API cost.
- **One model backbone: DeepSeek-V3-0324.** Matching the original paper is what isolates
  architecture from model effects. Never substitute a different LLM for experiment runs.
  (Claude is the research assistant here, not the system under test.)
- **75-instance subset** (SWE-Bench-Verified-S, built on verified-mini, ~5GB not ~130GB).
- **Python repositories only.** Graph construction uses Python's `ast` module.
- **No new architecture.** The contribution is measurement.

## Experimental design

2x2 factorial: graph grounding (multiple chains vs single chain) x debate (multi-agent vs
single agent). Debate rounds nested at 1, 2, 3. Every multi-agent cell has a compute-matched
single-agent counterpart granted the same token budget via extended reasoning or best-of-N.
A compute-matched majority-voting arm is included as the cheap baseline.

Multiple seeds per cell, bootstrap confidence intervals. Never report a single run.

### Metrics to log on every run

- Acc@1 (File) — comparable to published figures
- Chain recall @ K — does the true location appear in ANY candidate chain (graph's job)
- Selection precision — does the CHOSEN chain contain it, given recall (debate's job)
- Total tokens per instance, split by stage
- Wall-clock latency per instance
- Cost per correctly localized instance
- Inter-agent agreement rate per debate round

The recall/selection split is a core contribution. The source paper never separates them.

## Repository layout

```
fyp-a3062/
├── CLAUDE.md              # this file
├── notes/literature.md    # paper notes, one entry per paper
├── swe-debate/            # instrumented fork
├── ablation/
│   ├── configs/           # one versioned config per cell
│   ├── harness/           # runner, token accounting, result parsing
│   └── results/           # raw JSON, one dir per run
└── report/
```

## Working conventions

- Every experiment run gets a versioned config file. No ad-hoc CLI overrides that don't get
  recorded — a result that can't be traced to a config is not a result.
- Token accounting is instrumentation, not an afterthought. It goes in before the first
  factorial pass, not after.
- Write results as raw JSON first, analyse separately. Do not compute summary statistics
  inside the run loop.
- Flag any deviation from the published SWE-Debate setup in `notes/deviations.md`. These
  become threats-to-validity entries in the report.
- Prefer running one instance end to end over batch runs when debugging. API spend is a real
  constraint.

## Known unknowns

- Whether SWE-Debate reproduces its reported localization numbers. Verify before anything
  depends on it. Fallback: same factorial on LocAgent (arXiv:2503.09089) or CoSIL
  (arXiv:2503.22424).
- Whether DeepSeek-V3 responds usefully to reasoning-budget control, which determines whether
  compute matching uses extended reasoning or best-of-N.
- An ambiguous line in the source paper's implementation notes about a testbed setup that was
  not used. Resolve early.

# FYP A3062 — Project Plan (current)

**Student:** Li Jingwei · **Supervisor:** A/P Chen Lihui · **Programme:** Information
Engineering and Media, NTU

> Living document, updated 2026-09-19. The version submitted on 14 Sep 2026 framed the project
> as a compute-matched ablation only. After supervisor feedback it now has three phases:
> diagnose, modify, validate. The earlier draft is in git history.

## 1. Title

**Diagnosing and Improving Multi-Agent Debate for Code Fault Localization**

## 2. Objective

To determine which component of graph-guided multi-agent fault localization does the work —
dependency-graph grounding, multi-agent debate, or their interaction — under matched compute;
to use that diagnosis to design and evaluate one improved debate mechanism; and to validate the
findings on issues the model cannot have seen during training.

## 3. Background

Automated issue resolution asks a system to read a bug report, find the responsible code in a
whole repository, and fix it. Finding the code — fault localization — is the bottleneck. Two
techniques dominate current systems: searching a code dependency graph recovered by static
analysis, and having several LLM agents debate the answer. SWE-Debate (Li et al., ICSE 2026)
combines both and reports 81.67% file-level localization accuracy on SWE-bench Lite.

Controlled studies now question the debate half. When a single agent is given the same token
budget, multi-agent debate usually stops helping (Huang et al., ICLR 2024; Tran & Kiela, 2026).
A large controlled study (Kim et al., Nature Machine Intelligence 2026) finds coordination helps
less as the single-agent baseline rises, with little benefit above about 45%, while costing
58-515% extra tokens. Debate can work, but only with incentives that reward information and
genuinely different agents (ColMAD, 2025) — SWE-Debate uses competitive debate among five
copies of one model. Full synthesis: `notes/literature-summary.md`.

## 4. Gap and motivation

SWE-Debate's debate ablation measures end-to-end Pass@1 on SWE-bench Verified (41.4% with
debate, 37.2% without). It removes the debate's tokens along with the mechanism, varies one
component at a time, reports no cost, and is a single run. Debate was never ablated at the
localization level, where accuracy is about 80% and the capability-saturation account predicts
it adds little. No study has crossed a graph factor with a coordination factor under matched
compute, and none has measured whether the true fix location is even reachable in the graph.

This matters because graph construction is free while debate multiplies inference cost. Teams
building software engineering agents currently cannot tell which one earns its place. And if
debate does not pay as designed, the next question is whether a better-designed debate can.

## 5. Research questions

**Phase 1 — Diagnose**
- RQ1. What fraction of true fix locations is reachable in the dependency graph, and why are
  the rest not?
- RQ2. Does graph grounding keep its contribution under matched compute? (H1: yes)
- RQ3. Does debate add to localization under matched compute? (H2: little)
- RQ4. Do graph and debate interact? (H3: yes)
- RQ5. Does any debate benefit concentrate on high-candidate-density instances? (H4: yes)

**Phase 2 — Modify**
- RQ6. Does one evidence-led change to the debate beat both the original debate and a
  compute-matched single agent?

**Phase 3 — Validate**
- RQ7. Do the Phase 1 and 2 findings hold on issues created after the model's training cutoff?

## 6. Approach

### Phase 1 — Diagnose (Semester 1)

1. **Reachability ceiling.** Build the dependency graph as SWE-Debate does, take the true fix
   location from the gold patch, and check whether a path exists from the issue's entry nodes.
   Categorise unreachable cases (dynamic dispatch, decorators, `getattr`, configuration-driven
   wiring). Static analysis only — no model inference.
2. **Reproduction and instrumentation.** Serve an open-weights model at a pinned checkpoint with
   vLLM on NTU GPUs (the paper's model is no longer served). Reproduce the localization pipeline
   on the 75-instance SWE-Bench-Verified-S subset. Add per-stage token accounting, and log
   separately whether the true file appears in any candidate chain (retrieval, the graph's job)
   and whether it survives selection (the debate's job).
3. **Compute-matched factorial.** Cross graph grounding (multiple chains vs one) with debate
   (multi-agent vs single agent). Give each single-agent arm the same token budget as its
   multi-agent counterpart. Add majority-vote and self-consistency arms. Hold candidate ordering
   fixed across arms. Several seeds per cell; paired per-instance statistics (McNemar or paired
   bootstrap), expanding to the 300-instance SWE-bench Lite if power is marginal.

### Phase 2 — Modify (Semester 2, first half)

Build ONE modification, chosen from Phase 1 evidence:
- **Default: graph-grounded debate.** Agents must cite checkable graph facts — whether a
  claimed path exists, its length, its edge types — and disagreements are settled against the
  graph. Models cannot reliably correct themselves without an external signal; the graph is
  such a signal and costs nothing to consult.
- **Fallback: collaborative protocol (ColMAD) with agents from two model families.** The only
  protocol shown to beat a compute-matched single agent, and only with different models.
- Evaluate against the original debate and the compute-matched single agent, under the same
  controls as Phase 1.

### Phase 3 — Validate (Semester 2, second half)

Re-run the key configurations on SWE-bench-Live (arXiv:2505.23419), starting from its
300-instance Lite subset and keeping only issues created after the backbone's training cutoff.
It is Python-only, so the graph construction carries over, and localization-only evaluation
needs no Docker. Its multi-file tasks double as a candidate-density stratum for H4.

## 7. Scope

**Included:** fault localization; the static dependency graph; SWE-Debate's chain voting and
plan debate; one debate modification; token and latency cost as outcomes; SWE-bench subsets and
SWE-bench-Live.

**Excluded, with reasons:**
- Patch generation and end-to-end resolve rate — neither factor operates there, and it
  dominates cost and needs Docker test harnesses. (Pending the supervisor's confirmation.)
- Varying the model within a comparison — would reintroduce the confound being removed. The
  Phase 2 fallback's two-model arm is the one deliberate exception.
- Debate round count as a factor — hardcoded in the implementation.
- Non-Python repositories — the graph is built with Python's `ast`; Multi-SWE-bench is a
  stretch goal only.
- Training or fine-tuning models.

## 8. Schedule

| Period | Phase | Work | Milestone |
|---|---|---|---|
| Sep 2026 | 1 | Environment; one SWE-Debate instance end to end; GPU access; reachability measurement | Plan submitted 14 Sep; go/no-go on the framework 30 Sep |
| Oct 2026 | 1 | Serve backbone; reproduce localization baseline; token accounting; component switches; ordering control; retrieval/selection logging | Baseline reproduced |
| Early Nov 2026 | 1 | First factorial pass (not yet compute-matched); interim report and video | Interim report 10 Nov |
| Nov–Dec 2026 | 1 | Compute-matched arms, majority vote, self-consistency, multiple seeds, paired analysis | Phase 1 results |
| Jan – mid-Feb 2027 | 2 | Build and evaluate the chosen debate modification | Phase 2 results |
| Mid-Feb – early Mar 2027 | 3 | SWE-bench-Live validation; H4 stratification | Phase 3 results |
| Mar 2027 | — | Writing, figures, demonstration build | Draft final report 25 Mar |
| Apr 2027 | — | Revision; demonstration | Final report 9 Apr; demo 12–16 Apr |
| May 2027 | — | Oral presentation; final submissions | Oral 10–12 May; library 19 May |

The December vacation carries the compute-matched runs; the schedule depends on it.

## 9. Deliverables

1. Reachability analysis of code dependency graphs, with a taxonomy of unreachable cases.
2. An instrumented SWE-Debate fork with component switches and token accounting.
3. Compute-matched factorial results with paired statistics and cost-accuracy plots.
4. One improved debate mechanism, evaluated under matched compute.
5. Validation results on SWE-bench-Live.
6. A demonstration: original debate, improved debate and single agent on the same bug, with
   token counters.
7. Interim report and video, final report, demonstration, oral presentation.

## 10. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| SWE-Debate does not run or reproduce | High | Decision point 30 Sep; same design on LocAgent or CoSIL. The reachability analysis does not depend on it. |
| GPU unavailable or too old | Medium | MLDA first; EEE GPU Cluster (48–96 GB cards) as fallback; smaller model if needed. |
| The modification does not beat the baseline | Medium | A bounded null under proper controls is a result; Phase 1 findings stand; ColMAD fallback. |
| Too few post-cutoff SWE-bench-Live instances | Low–Medium | The benchmark updates monthly; a backbone with an earlier cutoff leaves more instances. |
| Differences within noise | Medium | Paired design, multiple seeds, expand to 300 instances. |
| Scope creep | Medium | One modification only; decisions logged in `notes/decisions.md`. |

## 11. Key references

Li et al., SWE-Debate, ICSE 2026 (arXiv:2507.23348) · Kim et al., Capable language models can
outgrow the benefits of collaboration, Nature Machine Intelligence 2026
(doi:10.1038/s42256-026-01268-y) · Chen et al., When and Why Does Multi-Agent Debate Fail,
arXiv:2510.20963 · Tran & Kiela, arXiv:2604.02460 · Huang et al., ICLR 2024 · Du et al.,
ICML 2024 · Rafi et al., LLM4FL, arXiv:2409.13642 · Chen et al., LocAgent, arXiv:2503.09089 ·
Jimenez et al., SWE-bench, ICLR 2024 · Zhang et al., SWE-bench Goes Live!, arXiv:2505.23419 ·
Cemri et al., NeurIPS 2025 · Liu et al., ACM TOSEM (doi:10.1145/3796507). Full list:
`notes/reading-order.md`.

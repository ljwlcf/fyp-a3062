# FYP A3062 — Project Plan

**Student:** Li Jingwei
**Supervisor:** A/P Chen Lihui
**Programme:** Information Engineering and Media (IEM), NTU
**Submission:** Week 6, FYP 2026 S1 — 14 September 2026

---

## 1. Title

**Does Debate Earn Its Tokens? A Compute-Matched Factorial Ablation of Graph-Grounded Multi-Agent Fault Localization**

---

## 2. Objective

To determine whether the performance attributed to multi-agent debate in graph-guided software issue localization survives a compute-matched comparison, through a factorial ablation of graph grounding and debate mechanisms on the SWE-Debate framework, evaluated on file-level localization accuracy against measured token and latency cost, in order to inform cost-aware design of future software engineering agents.

---

## 3. Background

### 3.1 LLMs for repository-level software engineering

Large language models have moved from function-level code completion to repository-level tasks, of which automated issue resolution is the most demanding. Given a natural-language issue report and a full codebase, a system must identify the defective code and produce a patch. The SWE-bench family of benchmarks (Jimenez et al., ICLR 2024) formalised this task on real GitHub issues and has become the standard measure of progress.

The task decomposes into two stages: **fault localization**, identifying which code must change, and **patch generation**, producing the change. Localization is widely treated as the bottleneck, since a patch generator cannot repair code it never retrieves.

### 3.2 From flat retrieval to graph-grounded retrieval

Early systems retrieved code by embedding similarity over chunks. This loses structure: an embedding of a function body does not encode which functions call it, which class it inherits from, or which module imports it. Since defects propagate along exactly those relationships, flat retrieval systematically misses multi-file faults.

Graph-based retrieval-augmented generation (GraphRAG) addresses this by indexing an explicit graph of entities and relations and retrieving over paths rather than points (Peng et al., *Graph Retrieval-Augmented Generation: A Survey*, ACM TOIS). In the code domain the graph is not extracted by an LLM from prose but recovered by static analysis: nodes are files, classes and functions; edges are calls, inheritance, imports and variable references. LocAgent, CoSIL, OrcaLoca, KGCompass and Prometheus all instantiate this idea, and all report gains over flat retrieval on SWE-bench localization.

### 3.3 Multi-agent coordination and debate

In parallel, a second line of work replaces the single reasoning agent with several. Multi-agent debate (Du et al., ICML 2024) has multiple model instances propose answers, critique one another over several rounds, and converge. The mechanism was reported to improve factuality and reasoning across arithmetic and factual QA.

Scepticism followed quickly. Huang et al. (*LLMs Cannot Self-Correct Reasoning Yet*) found debate failing to beat plain self-consistency. Later work found debate on par with a single agent once demonstrations are available, and found it failing to reliably surpass simple majority voting. Cemri et al.'s MAST taxonomy, built from over 1,600 annotated traces across seven frameworks, opens by observing that multi-agent performance gains on popular benchmarks are often minimal, and catalogues fourteen failure modes across specification, inter-agent misalignment and task verification.

Most recently, Tran and Kiela gave the scepticism a theoretical basis. Modelling inter-agent messages as a lossy function of the full context, they apply the Data Processing Inequality to show that a single agent with full context is information-theoretically guaranteed to do at least as well as a multi-agent system operating on summaries of that context. Empirically, across two datasets, three model families and five multi-agent architectures under matched thinking-token budgets, single-agent systems matched or outperformed every multi-agent variant. Their conclusion is that many reported multi-agent gains are better explained by unaccounted computation than by architecture.

Crucially, the same analysis identifies a **boundary condition**. When a single agent's effective context utilisation degrades — long contexts, noise, or distractors that are topically similar but irrelevant — the guarantee no longer holds, and structured multi-agent pipelines become competitive. In their degradation experiments the crossover was clearest under corruption that injects misleading content rather than merely removing information.

### 3.4 Where the two lines meet

SWE-Debate (Li et al., arXiv:2507.23348) sits at the intersection. It traverses a static dependency graph to generate candidate fault propagation chains, runs a three-round competitive debate among five specialised agents to select a chain and synthesise a modification plan, then hands that plan to an MCTS-based repair agent. It reports 41.4% Pass@1 on SWE-bench-Verified and 81.67% file-level localization accuracy on SWE-bench-Lite, both state of the art among open-source frameworks.

Its ablation removes three components individually: multiple chain generation (−10.0 points), the edit plan (−6.0), and multi-agent debate (−4.2).

### 3.5 The unresolved question

That ablation has four properties that leave the central question open.

1. **It is not compute-matched.** Removing the debate removes five agents across three rounds of inference. The 4.2-point drop therefore conflates architectural contribution with inference budget — precisely the confound the budget-controlled literature identifies as the usual explanation for multi-agent gains.
2. **It is one-factor-at-a-time, not factorial.** Components are removed singly and never crossed, so any interaction between graph grounding and debate is unmeasured.
3. **It reports no cost.** No token counts, no latency, no monetary cost appear anywhere in the paper, despite the practical claim being about whether a heavier architecture is worth adopting.
4. **It is a single run of a single model** (DeepSeek-V3-0324) with no seeds and no confidence intervals. The paper's own threats-to-validity section concedes the scope was budget-limited.

A related taxonomy of coding-agent architectures makes the same point at field level: SWE-bench comparisons confound scaffold design, model choice and configuration, and existing evaluations do not perform the architectural decomposition needed to separate them.

---

## 4. Motivation

Two literatures make opposite predictions about the same system, and no experiment adjudicates between them.

The budget-controlled literature predicts that SWE-Debate's debate component should contribute little once compute is held fixed, because message-passing between agents is a lossy channel and the extra tokens would buy more if spent inside one reasoning trajectory. The boundary condition in that same analysis predicts the opposite for this particular task: a large repository presents exactly the degraded-context regime that favours multi-agent structure, since dozens of files are topically similar to the issue text but only one or two are correct. Distractor-rich contexts are where multi-agent pipelines were found to close the gap and occasionally win.

Software issue localization is therefore not just another application of multi-agent debate. It is the most likely place for debate to genuinely earn its cost, and it has never been tested under the controls that would establish that. Confirming the benefit would be the first compute-controlled evidence that coordination pays for itself in a real engineering task. Failing to confirm it would show that a state-of-the-art result rests on unaccounted compute.

The practical stake is direct. Teams building agentic software engineering tools are choosing today between graph-grounded single-agent systems and heavier multi-agent ones, without any published measurement of what the coordination overhead buys. This project produces that measurement.

---

## 5. Research questions and hypotheses

**RQ1.** Does graph grounding retain its contribution to localization accuracy under a matched token budget?

**RQ2.** Does multi-agent debate retain its contribution to localization accuracy under a matched token budget, relative to a compute-equivalent single-agent baseline?

**RQ3.** Do graph grounding and debate interact, or are their contributions additive?

**RQ4.** Does the benefit of debate vary with the degree of context degradation in the instance — that is, is debate worth its cost only on hard instances?

Corresponding hypotheses:

- **H1.** Graph grounding survives compute matching, because it supplies information the model does not otherwise have rather than merely spending more tokens.
- **H2.** The measured contribution of debate shrinks substantially under compute matching, relative to the 4.2 points reported.
- **H3.** The two factors interact rather than sum: debate helps mainly when the graph has produced several plausible competing chains.
- **H4.** Any surviving debate benefit concentrates on instances with high candidate density — many topically similar files — consistent with the degraded-context boundary condition.

H4 matters for project risk. If H2 holds and debate's advantage largely disappears, H4 converts a negative result into a positive characterisation of *when* coordination is worth paying for.

---

## 6. Scope

### Included

- **Fault localization only.** Graph grounding and debate both operate entirely within SWE-Debate's localization stage, so this is where the research question lives.
- **The static code dependency graph** as constructed by SWE-Debate: call, inheritance, import and variable-reference edges recovered by AST analysis.
- **The multi-agent debate pipeline**, at both levels at which it operates: chain-level competitive ranking and modification-plan refinement.
- **A factorial design** crossing graph grounding against debate, with a compute-matched single-agent arm at each cell.
- **Cost as a first-class outcome:** tokens, wall-clock latency and monetary cost reported alongside every accuracy figure.
- **Instance-level stratification** by candidate density, to test H4.
- **A single model backbone,** DeepSeek-V3-0324, matching the original paper.

### Excluded, with reasons

- **Patch generation and resolve rate.** The MCTS repair stage is a third heavy component that neither factor of interest touches. Excluding it removes the dominant cost driver and the Docker test-harness dependency, at the price of not reporting end-to-end Pass@1.
- **The full SWE-bench-Verified set of 500 instances.** Compute budget. The project uses the 75-instance SWE-Bench-Verified-S subset defined in the original paper, which is built on a mini variant requiring roughly 5GB rather than 130GB of storage.
- **Varying the LLM backbone.** Holding the model fixed is what isolates architectural effects from model effects; varying it would reintroduce the confound the project exists to remove.
- **Multilingual repositories.** The dependency graph construction is Python-specific; extending it is engineering effort that answers no research question here.
- **RL-trained or fine-tuned localization agents.** Out of compute and time budget.
- **Proposing a new architecture.** The contribution is measurement, not a system.

---

## 7. Methodology

### 7.1 Experimental design

A 2×2 factorial over graph grounding (multiple chains vs. single chain) and debate (multi-agent vs. single agent), with debate rounds as a nested third factor at 1, 2 and 3 rounds. Each cell is run with multiple seeds and reported with bootstrap confidence intervals, following the practice of the budget-controlled literature rather than the single-run practice of the source paper.

### 7.2 Compute matching

The central methodological control. For every multi-agent cell, the total inference tokens consumed are measured, and the corresponding single-agent cell is granted the same budget through extended reasoning or best-of-N sampling with selection. Reported differences are then attributable to architecture rather than spend. A compute-matched majority-voting arm is included as a cheap baseline, since prior work finds debate frequently fails to beat it.

### 7.3 Separating recall from selection

SWE-Debate's two stages have distinct jobs, and the paper never measures them separately. The graph's job is recall: does the true fix location appear in *any* generated chain? The debate's job is selection: does the *chosen* chain contain it? Logging both yields a decomposition of every failure into retrieval failure or selection failure, and attributes each to the responsible component. This diagnostic is adapted from the error-bucketing methodology of the budget-controlled study.

### 7.4 Debate diversity audit

The original paper concedes that its five agents are one model differentiated only by system prompts. Logging inter-agent agreement rates at each round tests whether the agents genuinely disagree. Near-total agreement would indicate the debate is largely ceremonial and would independently explain a small ablation delta.

### 7.5 Metrics

- Acc@1 (File) — file-level localization accuracy, comparable to published figures
- Chain recall @ K — whether the true location appears in any candidate chain
- Selection precision — whether the chosen chain contains it, conditioned on recall
- Total tokens per instance, split by stage
- Wall-clock latency per instance
- Cost per correctly localized instance
- Inter-agent agreement rate per debate round

---

## 8. Deliverables

1. An instrumented fork of SWE-Debate with per-component switches and token accounting.
2. A reproducible ablation harness with versioned configurations for every cell.
3. A results dataset covering all cells with seeds and confidence intervals.
4. Cost-accuracy frontier plots for the architectural choices studied.
5. Interim report and video presentation.
6. Final report, project demonstration and oral presentation.

---

## 9. Schedule

| Period | Work | Milestone |
|---|---|---|
| Sep 2026 | Literature review; clone and run SWE-Debate and Moatless end to end on one instance | **Project Plan — 14 Sep 2026** |
| Late Sep – Oct 2026 | Reproduce reported localization baseline on the 75-instance subset; build token accounting and per-component switches | Baseline reproduced |
| Oct – early Nov 2026 | First factorial pass without compute matching; interim analysis | **Interim Report + Video — 10 Nov 2026** |
| Nov 2026 – Jan 2027 | Compute-matched arms; majority-voting baseline; multi-seed runs | Main results complete |
| Jan – Feb 2027 | Recall/selection decomposition; debate diversity audit; H4 stratification | Diagnostic results complete |
| Feb – Mar 2027 | Analysis, figures, writing | **Draft Final Report — 25 Mar 2027** |
| Mar – Apr 2027 | Revision | **Final Report — 9 Apr 2027** |
| Apr 2027 | Demonstration | **Project Demonstration — 12–16 Apr 2027** |
| May 2027 | Oral presentation; final revisions | **Oral — 10–12 May 2027; Library submission — 19 May 2027** |

---

## 10. Risks and contingencies

| Risk | Likelihood | Mitigation |
|---|---|---|
| SWE-Debate does not run or does not reproduce | Medium | Verified in September, before any dependent work. Fallback: run the same factorial on LocAgent or CoSIL, both open with graph-guided localization. |
| API cost exceeds available budget | Medium | Localization-only scope removes the MCTS stage entirely. DeepSeek-V3 pricing is low. Cell count reducible by dropping the round-count factor. |
| Differences between arms fall within noise | Medium | Multi-seed runs with confidence intervals from the outset. A precisely bounded null result under proper controls is itself the finding, and H4 stratification provides a positive result path. |
| Ambiguity in the original implementation notes | Medium | Resolve in September; document any deviation from the published setup as a threat to validity. |
| Judged as derivative of an existing ablation | Low–Medium | The compute-matched and factorial framing is not what the source paper did; positioning against the budget-controlled literature makes the distinction explicit in the report's framing. |

---

## 11. Key references

- Li, H. et al. (2025). SWE-Debate: Competitive Multi-Agent Debate for Software Issue Resolution. arXiv:2507.23348
- Tran, D. & Kiela, D. (2026). Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets. arXiv:2604.02460
- Cemri, M. et al. (2025). Why Do Multi-Agent LLM Systems Fail? arXiv:2503.13657
- Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures. arXiv:2604.03515
- When and Why Does Multi-Agent Debate Fail and Does It Really Underperform? arXiv:2510.20963
- Jimenez, C. E. et al. (2024). SWE-bench: Can Language Models Resolve Real-world GitHub Issues? ICLR. arXiv:2310.06770
- Xia, C. S. et al. (2024). Agentless: Demystifying LLM-based Software Engineering Agents. arXiv:2407.01489
- Chen, Z. et al. (2025). LocAgent: Graph-Guided LLM Agents for Code Localization. arXiv:2503.09089
- Jiang, Z. et al. (2025). CoSIL: Software Issue Localization via LLM-Driven Code Repository Graph Searching. arXiv:2503.22424
- Prometheus: Unified Knowledge Graphs for Issue Resolution in Multilingual Codebases. arXiv:2507.19942
- Antoniades, A. et al. (2024). SWE-Search: Enhancing Software Agents with Monte Carlo Tree Search. arXiv:2410.20285
- SWE-Effi: Re-Evaluating Software AI Agent System Effectiveness Under Resource Constraints. arXiv:2509.09853
- Du, Y. et al. (2024). Improving Factuality and Reasoning in Language Models through Multiagent Debate. ICML
- Huang, J. et al. Large Language Models Cannot Self-Correct Reasoning Yet. arXiv:2310.01798
- Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models? arXiv:2508.17536
- Peng, B. et al. Graph Retrieval-Augmented Generation: A Survey. ACM TOIS. arXiv:2408.08921

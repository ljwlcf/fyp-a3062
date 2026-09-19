# Reading order — FYP A3062

Sorted for the three-phase plan: **diagnose** SWE-Debate (Sem 1), **modify** its debate mechanism (Sem 2, first half), **validate** on uncontaminated data (Sem 2, second half). The PDFs live in `papers/` (gitignored) and their filenames start with these labels: A = read fully, B = method and results, C = skim and cite, D = cross-domain only. Original filenames are in brackets so any paper can be matched to its arXiv ID or DOI. Per-paper notes: `notes/literature.md`. Synthesis: `notes/literature-summary.md`.

## A — Read fully (A1–A9)

- **A1 SWE-Debate** — The system you reproduce, diagnose and modify. Read §3–5 and Appendix C, which holds the debate prompts you will change. [2507.23348v1]
- **A2 Capable language models can outgrow the benefits of collaboration** — The prediction your results test: coordination gains largely vanish above a ~45% single-agent baseline. Published version of C14. Its SWE-bench arm uses only 20 instances per cell. [s42256-026-01268-y]
- **A3 When and Why Does Multi-Agent Debate Fail** — Design basis for Phase 2. Both competitive debate (what SWE-Debate uses) and consensus-seeking debate fail through "debate hacking". Their collaborative protocol, ColMAD, beats a single agent under the same budget, but only when the debaters are different models. [2510.20963v2]
- **A4 Single-Agent LLMs Outperform MAS Under Equal Thinking Token Budgets** — How to match compute. The §3.1 boundary condition is why localization is the interesting test case, though plain distractors were their weakest lever. [2604.02460v2]
- **A5 Multi-Agent Fault Localization via Graph-Based Retrieval and Reflexion (LLM4FL)** — Closest prior work. Candidate ordering alone swings Top-1 by 22 points, so your design must control for it. [2409.13642v2]
- **A6 LocAgent** — Graph-guided localization through tool calls. Your fallback platform, and a model for letting debating agents query the graph. [2503.09089v2]
- **A7 SWE-bench** — Your Phase 1–2 dataset: how instances, repository snapshots and gold patches work. [2310.06770v3]
- **A8 SWE-bench Goes Live!** — Your Phase 3 dataset: 1,319 tasks from GitHub issues created since 2024, across 93 Python repositories. Use only instances created after your backbone model's training cutoff, or the contamination argument does not hold. [2505.23419v2]
- **A9 Rethinking the Value of Multi-Agent Workflow (OneFlow)** — One agent can simulate same-model workflows like SWE-Debate's. Supports the case for heterogeneous agents. [2601.12307v1]

## B — Method and results (B1–B12)

- **B1 Multiagent Debate (Du et al.)** — The original debate protocol everything builds on. [2305.14325v1]
- **B2 Entropy Perspective on Multi-Agent Collaboration** — Outcomes largely settle in round one: basis for adaptive stopping and your agreement audit. [2602.04234v6]
- **B3 Multi-Agent Systems are Mixtures of Experts** — Debate helps when influence tracks competence rather than confidence. Relevant to weighting agents by graph evidence. [2605.25929v2]
- **B4 Why Do Multi-Agent LLM Systems Fail? (MAST)** — Failure taxonomy for labelling your debate traces. [2503.13657v3]
- **B5 Reasoning in Token Economies** — How budget-matched evaluation is done properly. [2406.06461v3]
- **B6 More Agents Is All You Need** — Sampling and voting: your majority-vote baseline arm. [2402.05120v2]
- **B7 Agentless** — A simple pipeline that rivals agents; hierarchical localization baseline and per-stage cost reporting. [2407.01489v2]
- **B8 SWE-Search** — SWE-Debate is built on this codebase. [2410.20285v6]
- **B9 LLMs Cannot Self-Correct Reasoning Yet** — Debate fails to beat self-consistency, and models can't fix their own errors without an external signal. That is the argument for using the graph as the signal. [2310.01798v2]
- **B10 Advances and Frontiers of LLM-based Issue Resolution (survey)** — Map of the field; names the missing efficiency evaluation; other datasets for Phase 3. [2601.11655v1]
- **B11 Inside the Scaffold** — SWE-bench comparisons confound scaffold, model and configuration. [2604.03515v2]
- **B12 SWE-Effi** — Cost-aware evaluation of SWE agents; closest prior art to your cost plots. [2509.09853v2]

## C — Skim and cite (C1–C14)

C3–C6 are the localization history your related work needs; don't let it start in 2024.

- **C1** LLM-Based Agents for SE: A Survey (TOSEM) — source of the "only 46.7% report efficiency" figure [3796507]
- **C2** LLMs for SE: A Systematic Literature Review (TOSEM) [3695988]
- **C3** LLM-Based Explainable Fault Localization / AutoFL (FSE 2024) [2308.05487v3]
- **C4** LLMs for Test-Free Fault Localization / LLMAO (ICSE 2024) [2310.01726v1]
- **C5** Where Should the Bugs Be Fixed? / BugLocator (ICSE 2012) [2337223.2337226]
- **C6** Bug Localization using Structured IR / BLUiR (ASE 2013) [ASE.2013.6693093]
- **C7** Scaling LLM-based Multi-Agent Collaboration / MacNet (ICLR 2025) [2406.07155v3]
- **C8** Graph RAG: A Survey (TOIS) [2408.08921v2]
- **C9** From Local to Global / Microsoft GraphRAG [2404.16130v2]
- **C10** Evaluation and Benchmarking of LLM Agents (KDD 2025) [2507.21504v1]
- **C11** Survey on Benchmarks and Solutions in SE of LLM Agentic Systems [2510.09721v3]
- **C12** Software Testing With LLMs (IEEE TSE) [Software_Testing_With_Large_Language_Models_Survey_Landscape_and_Vision]
- **C13** Earlier arXiv version of C1 — read C1 instead [2409.02977v2]
- **C14** Preprint of A2 (same study, same authors) — read A2 instead [2512.08296v3]

## D — Cross-domain, for the methodology point only (D1–D6)

Not debate systems. Useful only as evidence that single-run, one-factor-at-a-time ablations are the norm across fields.

- **D1** Multi-agent KG-RAG for intelligent maintenance (J Manuf Syst) [1-s2.0-S0278612526000452-main]
- **D2** Agentic Graph-RAG (IEEE ICCC) [Agentic_Graph-RAG_A_Multi-Agent_Framework_for_Robust_Decomposed_Multi-Hop_Reasoning]
- **D3** Agentic RAG for Software Testing (IEEE ICoDSE) [Agentic_RAG_for_Software_Testing_with_Hybrid_Vector-Graph_and_Multi-Agent_Orchestration]
- **D4** MedRAG-Agent (IEEE GCAT) [MedRAG-Agent_Medical_Query_Resolution_By_Employing_A_Multi-Agent_Knowledge_Graph-Enhanced_RAG-Based_AI_Framework]
- **D5** Multi-Agent OSINT with Graph RAG (IEEE INISTA) [Multi-Agent_OSINT_Architecture_with_Graph_RAG_Integration_and_Hierarchical_Bloom-Filter_Deduplication]
- **D6** Multi-agent KG for news bias detection (Neural Comput Appl) [s00521-026-11944-0]

## Not in the folder yet

- **The SWE-Bench Illusion** (2025) — why uncontaminated data matters. B-tier.
- **Debate or Vote** (arXiv 2508.17536) — whether debate beats plain voting. B-tier.
- **CoSIL** (arXiv 2503.22424) — second fallback platform. B-tier.
- Lower priority: OrcaLoca, KGCompass, Prometheus (competitor systems); Multi-SWE-bench (only if Phase 3 goes beyond Python).

`papers/_extracted-text/` holds plain-text copies of C1 and C2.

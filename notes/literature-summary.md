# Literature summary — the gist of each paper

Plain-language summaries of all 41 papers, written from the full text of each PDF (A1, A2 … match
the file names in `papers/`). Technical notes for report writing stay in `notes/literature.md`.

**How to read this file**
- Start with section 3 (one sentence per paper) to see the whole field at a glance.
- A and B papers each follow the same order: the problem → how it works → how they tested it →
  what they found → **limitations and threats to validity (the authors' own)** → **future work
  they suggest** → **our own caveats** (things we noticed that the authors don't say) → why it
  matters to us → numbers worth quoting.
- C and D papers are shorter: what it is, key findings, limitations/future work, why it matters.
- Every number has its location in the paper (Table, §, Fig.) so you can check it.
- Where a paper has no limitations section, the entry says so.

## 1. Key terms

- **Fault localization** — finding which file or function a bug is in. Our focus.
- **Issue resolution** — the whole job: find the bug *and* write a fix that passes the tests.
- **Agent** — an AI model that works in steps (search, open files, decide), not in one reply.
- **Multi-agent debate** — several AI agents answer, read each other's answers, and revise.
- **Single agent** — one AI doing the whole task alone.
- **Tokens** — the chunks of text an AI reads and writes. The unit of AI cost.
- **Same budget / compute-matched** — comparing systems that are each allowed the same number
  of tokens, so nobody wins just by thinking more.
- **Ablation** — switching one part off to see how much it mattered.
- **Majority vote / self-consistency** — asking one AI the same question several times and
  taking the most common answer.
- **Code map / dependency graph** — which functions call, import or inherit from which.
- **GraphRAG** — AI retrieval that follows a graph of connections instead of searching text.
- **SWE-bench** — the standard test set of real GitHub bugs from Python projects.
- **Pass@1** — share of bugs fully fixed on the first try.
- **Acc@1 (File)** — share of bugs where the AI's first-guess file is correct.
- **Contamination** — the AI saw the test answers during training, so scores look too good.
- **Threats to validity** — the authors' own list of reasons their results might be wrong or
  might not carry over. *Internal*: something in the experiment itself could explain the result
  (e.g. the model memorised the test data). *External*: the result may not hold elsewhere (other
  languages, datasets, models). *Construct*: the metric may not measure what they claim.
- **Data contamination** — the test questions were in the model's training data, so a high score
  may be memory rather than skill.
- **pp (percentage points)** — the plain difference between two percentages (41.4% → 37.2% is
  −4.2 pp). A "relative" gain divides instead (41.4 / 38.8 = +6.7%), which looks bigger.

## 2. The big picture, and where our project fits

**What the papers add up to**

1. **Finding where a bug lives is the hard part, and a code map helps.** Every study here that
   removes the map loses accuracy.
2. **Debate looked powerful at first (B1), but mostly stops helping once a single AI gets the
   same budget** (B9, B5, A4, A2). Much of its gain turns out to be "more thinking" or
   "voting", not the arguing itself (B6).
3. **Debate can still win under specific conditions:** the agents are *different* models and
   are rewarded for sharing useful information rather than winning (A3), and influence goes to
   the competent agent rather than the confident one (B3).
4. **Most papers in this area don't report cost**, and test one part at a time in a single run
   (C1, B10, D1–D6).
5. **Old benchmarks may be memorised:** agents fix about twice as many old SWE-bench bugs as
   fresh ones (A8).

**Where our project fits**

SWE-Debate (A1) uses a code map plus five copies of the *same* AI in a *competitive* debate —
exactly the setup the recent evidence says should struggle. Its evidence for debate: switching
it off drops the full fix rate from 41.4% to 37.2%. But that was measured on the whole fixing
pipeline, in one run, with the debate's extra thinking removed at the same time. And because
37.2% is below A2's ~45% line, the two papers don't actually contradict each other.

What nobody has tested: **does debate help at the file-finding step itself** — where accuracy
is about 80% and A2 predicts little benefit — once a single AI gets the same budget? And **can
the map even reach the right file** in the first place? That's Phase 1. Phase 2 improves the
debate (ideas from B9 and A3). Phase 3 re-tests on fresh bugs (A8).

Caution: A2's 45% line was measured on task success in other benchmarks. Applying it to
file-finding accuracy is our assumption to test, not an established fact.

---

## 3. Quick reference — every paper in one sentence

| Paper | What it's about, in one sentence |
|---|---|
| **A1** SWE-Debate: Competitive Multi-Agent Debate for Software Issue Resolution | Build a code dependency graph, walk it to get many candidate "fault-propagation chains", let several LLM agents vote on a chain and debate a fix plan, then hand that plan to a tree-search patching agent. The result is 41.4% Pass@1 on SWE-bench Verified. |
| **A2** Capable language models can outgrow the benefits of collaboration | In a large, compute-matched comparison, multi-agent systems help only on some tasks, and once a single agent already scores above roughly 45%, adding more agents usually does not help and often hurts. |
| **A3** When and Why Does Multi-Agent Debate Fail and Does It Really Underperform? | Debate often loses to a single agent because the usual debate rules reward the wrong thing (winning or agreeing), and a "collaborative" rule set, ColMAD, with two *different* models fixes this on error-detection tasks. |
| **A4** Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets | When a single LLM (SAS) and a multi-agent system (MAS) get the same "thinking token" budget, SAS matches or beats every MAS design tested on multi-hop QA. MAS only catches up when the single agent's context is heavily corrupted. |
| **A5** A Multi-Agent Approach to Fault Localization via Graph-Based Retrieval and Reflexion | LLM4FL is a pipeline of three GPT-4o-mini agents. They split test-coverage data into chunks, walk the call graph to rank suspicious Java methods, then self-critique the ranking. It beats earlier LLM fault localizers on Defects4J. |
| **A6** LocAgent: Graph-Guided LLM Agents for Code Localization | LocAgent turns a Python repository into a typed code graph and gives one LLM agent three tools to search and walk it. It gets the best localization scores on SWE-bench-Lite, and fine-tuned open Qwen models come close to Claude-3.5 at about 1/7 of the cost. |
| **A7** SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | SWE-bench is the standard benchmark for our area: 2,294 real GitHub issues from 12 Python repos, where a model must write a patch (a code change) that makes the repo's own tests pass. |
| **A8** SWE-bench Goes Live! | SWE-bench-Live is a version of SWE-bench that is updated every month from fresh GitHub issues, built by an automated pipeline, and the same agents score much lower on it than on the old benchmark. |
| **A9** Rethinking the Value of Multi-Agent Workflow: A Strong Single Agent Baseline | If every agent in a multi-agent system uses the same LLM, one LLM playing all the roles in a single conversation does about as well, and is cheaper because it can reuse its KV cache. |
| **B1** Improving Factuality and Reasoning in Language Models through Multiagent Debate | Several copies of ChatGPT each answer a question, read each other's answers, and revise over a few rounds; this "multi-agent debate" beats a single model, self-reflection and majority voting on maths, chess and factual tasks. |
| **B2** When Does Multi-Agent Collaboration Help? An Entropy Perspective | Across 5 small open-weights models, 6 benchmarks and 5 set-ups, a single agent beats every multi-agent set-up in 43.3% of cases, and whether multi-agent works is mostly decided by how uncertain the agents are in round 1. |
| **B3** Multi-Agent Systems are Mixtures of Experts: Who Becomes an Influencer? | Debate between LLM agents behaves like a "mixture of experts" that decides, question by question, whose opinion wins, and in practice the winner is mostly the *most confident* (and stubborn) agent, which is not always the most competent one. |
| **B4** Why Do Multi-Agent LLM Systems Fail? | The authors read over 1,600 run logs from 7 multi-agent LLM systems and sorted the ways they fail into a taxonomy called MAST (14 failure modes in 3 groups). They then show that many failures come from how the system is designed, not only from the model. |
| **B5** Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies | When a plain baseline gets the same token budget, "chain-of-thought + self-consistency" matches or beats fancier strategies such as multi-agent debate and Reflexion. Much of their reported gain comes from spending more compute, not from a cleverer algorithm. |
| **B6** More Agents Is All You Need | Sampling the same LLM many times and taking a majority vote ("Agent Forest") improves accuracy steadily as the number of samples grows. With enough samples, a small model can beat a larger one. |
| **B7** Agentless: Demystifying LLM-based Software Engineering Agents | A fixed pipeline (localize → repair → validate) with no autonomous agent beats every open-source SWE-bench Lite agent of its time, cheaply. |
| **B8** SWE-Search: Enhancing Software Agents with Monte Carlo Tree Search and Iterative Refinement | SWE-Search adds tree search, an LLM "value" judge that writes feedback, and a final multi-agent debate on top of the Moatless agent. It resolves 23% more SWE-bench Lite issues (relative) across five models. |
| **B9** Large Language Models Cannot Self-Correct Reasoning Yet | Without outside feedback, LLMs asked to "review and fix" their own reasoning usually get *worse*. Multi-agent debate does no better than simple majority voting once you give both the same number of LLM calls. |
| **B10** Advances and Frontiers of LLM-based Issue Resolution in Software Engineering: A Comprehensive Survey | A survey of 175 papers and online resources on "issue resolution" (turning a GitHub issue into a working patch), sorted into Data, Methods and Analysis, with a list of open challenges. |
| **B11** Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures | The author read the source code of 13 open-source coding agents and built a 12-dimension taxonomy of their "scaffolds". A scaffold is the non-LLM code around the model: the control loop, tools, state and context handling. |
| **B12** SWE-Effi: Re-Evaluating Software AI Agent System Effectiveness Under Resource Constraints | The paper re-scores 15 scaffold+LLM pairs on 50 SWE-bench Verified issues. The scores measure how many issues get solved *per unit of tokens, dollars, CPU time and inference time*, not just resolve rate. |
| **C1** Large Language Model-Based Agents for Software Engineering: A Survey | A systematic survey of 124 papers on LLM-based agents (an LLM plus tools, memory and planning, sometimes several LLMs working together) for software engineering (SE), sorted by SE task and by agent design. |
| **C2** Large Language Models for Software Engineering: A Systematic Literature Review | A systematic literature review (SLR: a survey that follows a fixed, documented search-and-filter procedure) of 395 papers from Jan 2017 to Jan 2024. It covers which LLMs are used in SE, what data they use, how they are tuned and evaluated, and which SE tasks they handle. |
| **C3** A Quantitative and Qualitative Evaluation of LLM-Based Explainable Fault Localization | AutoFL lets one LLM (GPT-3.5/GPT-4) explore a repository through four tool calls, write an explanation of the bug, then name the buggy method; it matches or beats classic fault-localization (FL) methods while needing only one failing test. |
| **C4** Large Language Models for Test-Free Fault Localization | LLMAO adds a small trainable "bidirectional adapter" on top of a frozen code LLM (CodeGen) to score every line of a file as buggy or not. It needs no tests at all. |
| **C5** Where Should the Bugs Be Fixed? More Accurate Information Retrieval-Based Bug Localization Based on Bug Reports | BugLocator is a classic, pre-LLM method: it treats a bug report as a search query, ranks source files by text similarity, and boosts files that were changed to fix similar past bugs. |
| **C6** Improving Bug Localization using Structured Information Retrieval | BLUiR improves on BugLocator (C5) by treating each source file as a structured document with separate class, method, variable and comment fields, and matching them separately against the bug report's summary and description. |
| **C7** Scaling Large Language Model-based Multi-Agent Collaboration | MacNet arranges LLM agents on a directed acyclic graph (DAG: arrows, no loops) of up to 64 nodes (over 1,000 agents in the densest layout). The authors report a "collaborative scaling law": quality rises in an S-shape as agents are added. |
| **C8** Graph Retrieval-Augmented Generation: A Survey | This survey claims to be the first overview of GraphRAG (retrieval-augmented generation, RAG, that retrieves nodes, triples, paths or subgraphs from a graph instead of plain text chunks). It splits GraphRAG into three stages: G-Indexing, G-Retrieval and G-Generation. |
| **C9** From Local to Global: A GraphRAG Approach to Query-Focused Summarization | GraphRAG uses an LLM to build a knowledge graph from a document collection, groups the graph into communities and summarises each one. It then answers "big picture" questions by map-reducing over those summaries. It beats ordinary vector RAG on comprehensiveness and diversity. |
| **C10** Evaluation and Benchmarking of LLM Agents: A Survey | A short survey from SAP Labs that sorts LLM-agent evaluation along two axes: *what* to evaluate (behaviour, capabilities, reliability, safety) and *how* to evaluate (interaction mode, datasets, metric computation, tooling, environment). |
| **C11** A Comprehensive Survey on Benchmarks and Solutions in Software Engineering of LLM-Empowered Agentic System | An NTU-led survey of 150+ papers and 50+ benchmarks. It links SE benchmarks (code generation, translation, repair, etc.) to three kinds of solution: prompt-based, fine-tuning-based and agent-based. |
| **C12** Software Testing With Large Language Models: Survey, Landscape, and Vision | A survey of 102 studies that used LLMs for software testing, organized from the testing side (which task) and the LLM side (which model, prompt style and extra techniques). |
| **C13** Large Language Model-Based Agents for Software Engineering: A Survey | This is the arXiv preprint of **C1** (same authors, same 124 papers, same structure). Cite C1, the ACM TOSEM version, instead. |
| **C14** Towards a Science of Scaling Agent Systems | Same study as A2: 5 architectures (single agent, and four multi-agent types: Independent, Centralized, Decentralized/debate, Hybrid) × 9 models × 6 agentic benchmarks, with prompts, tools and token budget held fixed. It concludes that coordination stops helping once a single agent is above ~45%. |
| **D1** A Multi-Agent and synergistic Knowledge Graph retrieval-augmented generation framework for intelligent maintenance | A pipeline of four LLM "agents" (split the query, retrieve KG subgraphs + text, filter, self-reflect) plus a fine-tuned embedding model answers industrial-robot fault questions with 90.1% "reasoning accuracy". |
| **D2** Agentic Graph-RAG: A Multi-Agent Framework for Robust, Decomposed Multi-Hop Reasoning | A Planner, a Graph Navigator, a Corpus Retriever and a Synthesizer-Verifier work through a shared "blackboard" (a shared state that all agents read and write) instead of chatting, to answer multi-hop questions over Wikidata + Wikipedia. |
| **D3** Agentic RAG for Software Testing with Hybrid Vector-Graph and Multi-Agent Orchestration | An industry report: five specialised agents plus a vector database and a TigerGraph graph (15+ edge types such as Validates, Depends-on, Impacts) generate test plans and test cases for an SAP S/4HANA migration. |
| **D4** MedRAG-Agent: Medical Query Resolution By Employing A Multi-Agent, Knowledge Graph-Enhanced RAG-Based AI Framework | Four sequential agents (Query Decomposer, KG Navigator, Document Retriever, Synthesizer-Verifier) answer medical questions over a MedlinePlus + PubMed knowledge base, and the authors claim 78.5% accuracy on MedQA. |
| **D5** Multi-Agent OSINT Architecture with Graph RAG Integration and Hierarchical Bloom-Filter Deduplication | A software-architecture paper that redesigns an OSINT (open-source intelligence) pipeline. One "mega-agent" becomes several micro-agents, a single graph database holds both the KG and the vectors (GraphRAG), and a Bloom filter checks for duplicate URLs. |
| **D6** Improved multi-agent knowledge sharing system using knowledge graphs for news bias detection and fact-checking | Fact-checker and bias-detector agents share a Neo4j news KG as memory. With Claude 3.5 Sonnet, this beats LLM-only and RAG baselines on political bias detection and fact-checking. |

## 4. A — Read fully (the papers our project stands on)

### A1 — SWE-Debate: Competitive Multi-Agent Debate for Software Issue Resolution (arXiv preprint 2507.23348, July 2025)
**In one sentence:** Build a code dependency graph, walk it to get many candidate "fault-propagation chains", let several LLM agents vote on a chain and debate a fix plan, then hand that plan to a tree-search patching agent. The result is 41.4% Pass@1 on SWE-bench Verified.

**The problem:** Single agents explore a repository on their own. They often lock onto the first plausible location and miss the real root cause when several places look relevant. The paper calls this the "limited observation scope" problem (§1–2).

**How it works (§3, hyperparameters in §4.5 and App. B):**
1. **Graph:** Python `ast` static analysis builds a graph. Nodes are code entities. Edges are calls, inheritance, imports and variable references.
2. **Entry points:** An LLM pulls out the K=5 entities that the issue text names directly, such as class and function names (Prompt 1). It only keeps names that literally appear in the issue. A second prompt reads code snippets around them and adds 4 more entities from different files, for diversity (Prompt 2).
3. **Chain building:** From each entry point, the method first keeps the W=4 most relevant neighbours (breadth-first). It then extends each one depth-first, up to L=5 nodes. At each step it picks the next node with a score that mixes semantic similarity and structural importance (an LLM node-selection prompt; it can also stop early). This gives K×W = 20 chains.
4. **Chain selection (the "voting" step):** The method keeps m=6 chains: the longest one plus the 5 most different ones, measured by embedding distance. N=5 agents each vote for ONE chain, with a confidence score (Prompt 5). The chain with the most votes wins.
5. **Round 1:** Each of the 5 agents independently writes a modification plan for the winning chain (Prompt 6). The plan is JSON listing the locations, the change type (fix_bug/add_feature/refactor/optimize), the priority and the reasoning.
6. **Round 2:** Each agent reads all the other plans, defends or refines its own and writes a refined plan (Prompt 7).
7. **Discriminator:** A "lead architect" agent merges the refined plans into one step-by-step plan (Prompt 8).
8. **Patching:** MCTS (Monte Carlo Tree Search, from SWE-Search) builds a tree of Search/Plan/Edit actions. The first branches come from the plan. It uses UCT selection and an LLM value function, with max 20 iterations and max depth 20 (Table 5).
- All agents are the same model, DeepSeek-V3-0324, given different system prompts. The paper calls the process a "three-round debate". It describes the rounds both as vote → propose → refine (§1) and as analysis → refinement → final selection (§6.1).

**How they tested it:**
- **Data:**
  - SWE-bench Verified (500 issues) for resolution.
  - SWE-bench Lite (300) for localization.
  - SWE-Bench-Verified-S (75 issues = the 50-issue verified-mini set + 25 random ones; App. A) for the chain-depth study.
- **Metrics:**
  - Pass@1 = % of issues whose first patch passes the tests.
  - Acc@1 (File) = % of issues where the top-1 prediction contains all the files that need changing.
- **Baselines:** Agentless, AutoCodeRover, SWE-Agent, SWE-Search, Moatless, SWESynInfer, OpenHands, CodeAct. For localization they add LocAgent and KGCompass. Most baseline numbers are copied from leaderboards or papers, and some DeepSeek-V3 ones were re-run (§4.5).
- K, W, L, m and N were tuned on a "held out set in the full SWE-Bench dataset" (§4.5).

**What they found:**
- **Resolution (Table 1):** 41.4% (207/500). Same-model baselines: SWE-Agent 38.8%, OpenHands 38.8%, Agentless 36.6%, SWE-Search 35.4%, Moatless 34.6%.
- **Ablation (Table 2, Pass@1 on Verified):**
  - Without multiple chains: 31.4% (−10.0)
  - Without edit plan: 35.4% (−6.0)
  - Without multi-agent debate: 37.2% (−4.2)
  - The paper does not say how the arms were matched for compute. It says that without debate "the system relies on individual agent exploration".
- **Localization (Table 3, Lite):** Acc@1 (File) 81.67%, against LocAgent (Claude-3.5) 77.74% (+3.93), KGCompass 76.67%, SWE-Agent (DeepSeek-V3) 67.00% and SWE-Search (GPT-4o) 73.36%. The baseline numbers are taken from the LocAgent paper.
- **Chain depth (Fig. 3, Verified-S, Acc@1 File):** depth 1 → 70.7%, 3 → 72.0%, **5 → 86.7% (peak)**, 7 → 82.7%. The depth-to-value mapping is read from the figure. The authors say longer chains add distracting information and make the debate less focused (Finding 4).
- **Headline numbers:** "6.7%" and "5.1%" in the abstract are *relative* gains (41.4/38.8 and 81.67/77.74). The absolute gains are +2.6 pp and +3.93 pp. The "14.67%" over SWE-Agent is actually percentage points.
- **Cost:** The paper reports no token, cost or runtime numbers.

**Limitations and threats to validity (the authors' own; §6.2 and §7):**
- Graph construction is computationally expensive for large codebases, which limits scalability.
- Static analysis misses dynamic and runtime relationships.
- The debate uses one model with different prompts. This may not capture the full range of how real developers reason.
- Batch processing limits use inside real-time development workflows.
- **Internal:** DeepSeek-V3's pre-training data may contain SWE-bench repositories (data contamination). They argue that same-model gains show reasoning rather than memorisation.
- **Internal:** Time and budget limits restricted the study to one model (DeepSeek-V3-0324) and "a subset of SWE-Bench-Verified". This limits how far the results generalise across models.
- **External:** One Python-only dataset, which may not transfer to other languages or domains. They say the components are language-agnostic by design.
- The paper has **no construct-validity section**.

**Future work they suggest:**
- More efficient graph construction and incremental analysis for enterprise-scale repositories.
- Several different (heterogeneous) models, or domain-specific knowledge bases, to make the debate more diverse. Study how models with different reasoning abilities can be combined in the debate.
- Lightweight continuous analysis, tightly integrated with development environments, to help while coding.
- Evaluation on contamination-free datasets.
- More foundation models and larger datasets.
- Multi-SWE-bench (other languages).

**Our own caveats:**
- **No compute matching:** The −4.2 debate ablation is end-to-end Pass@1, not localization. Removing the debate also removed its tokens, so it is not compute-matched.
- **No localization ablation:** Localization-level ablations are never reported. The 81.67% figure is on Lite, not Verified, and it is unclear how a single "top-1 file" is taken from a chain or plan.
- **Single runs:** Every result is from one run, with no variance or significance tests.
- **Chain-depth study:** It uses only 75 issues.
- **Unclear scope:** §4.5 says "due to unsuccessful testbed setup, we did not utilize it", yet §3.4 describes test execution. §7 also says a "subset" of Verified was used, while Table 1 reports 207/500.
- **Tuning data:** The hyperparameters were tuned on SWE-bench data, which could overlap with the test issues.
- **Retrieval vs selection:** The paper never reports whether the right file is in any of the 20 or 6 chains (retrieval), separately from whether the vote picks it (selection).

**Why it matters to us:**
- **Phase 1:** This is the baseline we reproduce. Our reachability ceiling and our retrieval-vs-selection split fill the gaps above, and our compute-matched 2×2 tests the untested claim that debate helps localization.
- **Phase 2:** The authors themselves name single-model prompting as a weakness and propose heterogeneous models. That directly motivates our ColMAD fallback. Graph-grounded debate targets the fact that agents never check their claims against the graph.
- **Phase 3:** The authors flag contamination and call for contamination-free datasets, which is what SWE-bench-Live gives us.

**Numbers worth quoting in the report:**
- 41.4% Pass@1 on SWE-bench Verified, against 38.8% for the best same-model baseline (Table 1).
- Ablation: −10.0 without multiple chains, −6.0 without edit plan, −4.2 without debate (Table 2; end-to-end, not compute-matched).
- 81.67% Acc@1 (File) on SWE-bench Lite, against 77.74% for LocAgent (Table 3).
- Chain depth 5 is best at 86.7% on 75 issues; depth 7 gives 82.7% (Fig. 3).

---

### A2 — Capable language models can outgrow the benefits of collaboration (Nature Machine Intelligence, 2026)
Kim et al. (Google Research / MIT / Google DeepMind). Vol. 8, pp. 1157–1172, published 24 July 2026.

**In one sentence:** In a large, compute-matched comparison, multi-agent systems help only on some tasks, and once a single agent already scores above roughly 45%, adding more agents usually does not help and often hurts.

**The problem:** Many papers claim "more agents is better", but they usually compare systems that use different prompts, tools and compute budgets, so you cannot tell whether the gain came from the multi-agent design or just from extra compute. They also mostly test on static, one-shot benchmarks, not "agentic" tasks (tasks where the model must act over many steps in an environment, e.g. fix a GitHub repo). The paper asks: when does coordinating several agents actually beat one strong agent?

**How it works / what they did:**
1. Defined five architectures (Table 1): **SAS** (single-agent system); **Independent** (agents work in parallel, outputs just concatenated, no talking); **Decentralized** (peer debate rounds, then a consensus threshold of 0.7 or plurality vote — this is the "debate" arm); **Centralized** (an orchestrator agent assigns and checks sub-agents' work); **Hybrid** (orchestrator plus some peer talk).
2. Held prompts, tools and the per-system compute ceiling fixed. "Matched compute" here means the same total reasoning-token budget per system; a multi-agent system splits it across agents (Methods, "LLMs and intelligence scaling"). Mean budget ≈ 4,800 reasoning tokens.
3. Ran 9 models from OpenAI, Google and Anthropic (GPT-5 nano/mini/full, Gemini 2.0 Flash/2.5 Flash/2.5 Pro, Claude Sonnet 3.7/4/4.5) on 6 agentic benchmarks → 260 configurations.
4. Measured process metrics from traces (e.g. overhead = extra turns vs SAS; error amplification = how much errors grow vs one agent) and fitted a linear regression predicting performance from them.

**How they tested it:**
- **Benchmarks and n per (model, architecture) cell** (Fig. 1 caption, Data availability): BrowseComp-Plus, PlanCraft, WorkBench n = 100; Finance Agent n = 50; **SWE-bench Verified n = 20** (random 20 of 500, seed 42) and **Terminal-Bench n = 20** (first 20 of an 89-task snapshot). SWE-bench and Terminal-Bench used only 8 models (Claude Sonnet 3.7 was deprecated).
- **SWE-bench arm:** the metric is end-to-end issue resolution (does the patch pass the tests), with 7 tools (bash, file editing, test execution). All sub-agents of a multi-agent system share **one Docker container** per task, so "Independent" there means "no messages", not separate workspaces (Methods).
- **Metrics:** task success/accuracy; cross-validated R² (share of variance the regression explains on held-out data); architecture-selection accuracy.

**What they found:**
- **No universal benefit.** Across all benchmarks the mean multi-agent gain was 0.0% (95% CI −58.7% to +77.2%). Range: +80.8% (Finance Agent, centralized) to −70.0% (PlanCraft, independent) (Results, Fig. 2).
- Tasks that split into parallel parts gain (Finance Agent); step-by-step tasks lose under every design (PlanCraft).
- **SWE-bench Verified: every multi-agent design was slightly worse than one agent** (SAS mean 0.488): hybrid −1.3%, centralized −2.6%, **decentralized (debate) −6.4% (0.456)**, independent −12.8%. The authors link this to most models already being above the ~45% threshold (Results).
- **The ~45% capability-saturation threshold.** From the fitted baseline × team-size rule: if single-agent accuracy is above ~0.45, extra agents give zero or negative gain. It predicted the sign of the multi-agent gain in **94% of 16** SWE-bench Verified + Terminal-Bench model×benchmark configurations (P < 0.001, binomial test). But the underlying interaction term is **not** significant under cluster-robust statistics, so the authors call it a "selection rule", not a scaling law (Abstract; Robustness section).
- **Single-agent baseline is the only robust predictor** (P_robust = 0.004, P_Holm = 0.018).
- **Error amplification** (Ext. Data Table 2): independent 17.2×, decentralized 7.8×, hybrid 5.1×, centralized 4.4×. Having a verifier (orchestrator) contains errors. The baseline × error-amplification effect survives cluster-robust testing (P_robust = 0.030).
- **Coordination is expensive:** success per 1,000 tokens 67.7 (SAS) vs 23.9 (decentralized) (Ext. Data Table 2).
- **Regression:** cross-validated R² = 0.373; picks the best architecture in 87% of held-out within-domain cases, but leave-one-benchmark-out R² = −2.09 (cannot predict scores on a new domain).
- **Mixing models** (13 configurations, BrowseComp-Plus only): did not beat the threshold. Mixed centralized teams were 12.6 pp worse than strong-only teams; mixed decentralized teams +2.0 pp, mostly from the stronger model (Discussion; Ext. Data Fig. 2).

**Limitations and threats to validity (the authors' own, from Discussion and Methods; no section is labelled "threats to validity"):**
- Only tested up to 9 agents; overhead grows faster than linearly, so it is unknown whether bigger teams would show useful emergent behaviour.
- Heterogeneity was limited: agents shared base architectures and differed only in scale and role prompt; the mixed-model study was preliminary (13 configurations).
- Prompts were identical for all models and not tuned per model; tuned prompts might change the results.
- Six benchmarks may not cover all agentic tasks (e.g. embodied, multi-user, long-horizon).
- SWE-bench Verified and Terminal-Bench use only 20 instances (Docker cost); per-cell bootstrap CIs are about ±20 pp, so single comparisons are underpowered; only aggregate trends are claimed.
- Token-based communication makes multi-agent systems costly and slow.
- Benchmarks lack long-horizon time dependencies and real-world feedback loops.
- Only 6 benchmark clusters, so cluster-robust errors are conservative and several effects (tool×efficiency, intelligence, baseline×agents) are only "directional patterns".
- Negative leave-one-domain-out R² — absolute prediction on unseen domains is not feasible; the 87% result is within-domain interpolation, and high-overhead designs may need extra corrections for newer frontier models.
- Reproducibility: public Finance Agent/WorkBench adapters differ from upstream harnesses; shared Docker containers; provider non-determinism. Model-family differences are unexplained "signatures"; the BERTScore < 0.3 contradiction cut-off is an uncalibrated heuristic.
- "Agentic" is relative to today's models — SWE-bench may become one-shot solvable later.

**Future work they suggest:**
- Study larger teams and whether specialisation / self-organisation emerges.
- Teams mixing different model architectures, domain fine-tuning or complementary reasoning strategies.
- Role-specialised training or selection (some models suit orchestrator vs executor roles).
- Coordination protocols for tool-heavy tasks: tool-access scheduling, capability-aware routing, hierarchical tool delegation.
- More benchmark clusters with varied tool counts to properly test the tool-efficiency effect.
- Non-token communication (latent-space reasoning, activation sharing).
- Cheaper designs: sparse communication, early exit, distilled coordinators; speculative parallel branches to cut latency.
- Embodied and multimodal settings (robotics, medical triage, multi-user interaction).

**Our own caveats:**
- Each cell appears to be a **single run** ("canonical cluster run", Code availability; Fig. 3 caption). No repeated seeds.
- SWE-bench result is **end-to-end resolution on 20 issues**, not fault localization. A −6.4% relative change at n = 20 is about 1 issue per model — well inside ±20 pp noise.
- Their "debate" arm (decentralized) is generic peer debate, not SWE-Debate's graph-chain voting.
- Compute matching caps the budget but realised turns differ 1.6–6.2× (Results), so "matched" means a matched ceiling, not equal spend.
- Coordination metrics in Ext. Data Table 2 are architecture-level constants applied to all benchmarks, which limits what the regression can learn from them.
- Only closed API models; no open-weights models like ours. Study funded by Google, most authors Google employees (Competing interests).

**Why it matters to us:**
- **Phase 1:** This is the closest precedent for our compute-matched 2×2. It supports designing each multi-agent arm with a same-budget single-agent arm. It also gives a testable prediction: if our single-agent localization accuracy is above ~45%, debate should help little or hurt. We should report the single-agent baseline first.
- Their SWE-bench arm cannot answer our question (n = 20, end-to-end, no localization split) — which supports our claim that no one has tested debate at the localization level under equal compute.
- **Phase 2:** Error amplification is lowest when there is a verifier (centralized 4.4× vs 17.2×). This fits our graph-grounded debate idea (the graph acts as the checker). Their mixed-model result is weak evidence *against* the ColMAD fallback's "different backbones" premise, but it was only tested on BrowseComp-Plus.

**Numbers worth quoting in the report:**
- SWE-bench Verified, n = 20 per cell: SAS 0.488 vs decentralized debate 0.456 (−6.4%); all 4 multi-agent designs below SAS (Results, Fig. 2).
- ~45% threshold predicts the sign of the multi-agent gain in 94% of 16 SWE-bench Verified + Terminal-Bench configurations; per-cell CIs ≈ ±20 pp (Robustness; Discussion).
- Mean multi-agent gain across 260 configurations = 0.0% (95% CI −58.7% to +77.2%) (Results).
- Error amplification: independent 17.2× vs centralized 4.4× (Ext. Data Table 2).
- Success per 1K tokens: SAS 67.7 vs decentralized 23.9 (Ext. Data Table 2).

---

### A3 — When and Why Does Multi-Agent Debate Fail and Does It Really Underperform? (arXiv 2510.20963v2, July 2026; preliminary version at the ICML 2026 Workshop on Failure Modes of Agentic AI)
Chen, Niu, Cheng, Han, Sugiyama (CUHK / RIKEN AIP / HKBU / U. Tokyo).

**In one sentence:** Debate often loses to a single agent because the usual debate rules reward the wrong thing (winning or agreeing), and a "collaborative" rule set, ColMAD, with two *different* models fixes this on error-detection tasks.

**The problem:** Many studies find multi-agent debate (MAD) no better, or worse, than one agent using chain-of-thought or self-consistency (sampling several answers and voting), even though debate costs far more tokens. The authors ask *why*, and whether a better protocol (the rules of the debate) can fix it.

**How it works / what they did:**
1. **Sorted existing debate into two types** (§1, §2.2):
   - **CopMAD** (competitive): each debater is assigned a side and tries to convince a judge.
   - **CosMAD** (consensus-seeking): debaters revise until they agree (e.g. Du et al.'s "Society of Minds", SoM).
2. **Game-theory analysis** (§2.2, App. B), with a simplified model: two debaters, a yes/no label, and an ideal (Bayes-optimal) judge.
   - CopMAD is a "cheap-talk" game: messages cost nothing, so in equilibrium they carry no information about the truth. The best judge would ignore them (Prop. 2.4).
   - CosMAD throws away disagreements to reach agreement, so it loses information (Prop. 2.6).
   - Result: collaborative ≤ consensus ≤ competitive in error (Corollary 2.9).
3. **Named the failure "debate hacking"** (Fig. 4): three behaviours. **Fabricated evidence** (misreading the task requirements), **overconfident claims** ("fundamentally flawed"), and **redundancy** (copying the other debater's argument). The first two are typical of CopMAD, the third of CosMAD.
4. **Proposed ColMAD** (collaborative MAD, §2.3, App. E, Alg. 1):
   - Both debaters answer alone first. **If they agree, that answer is final, with no debate.**
   - If they disagree, they still defend a side, but they are told to find what the *other* side missed, adopt valid opponent points, and seek the truth.
   - Prompt tools: quotes from the task are checked by exact string match (verified vs unverified quotes); each debater self-audits one possible flaw in its own claim; each gives a confidence score.
   - A judge reads the transcript and decides.

**How they tested it:**
- **Main data:** ReaLMistake (App. F, Table 6). The task is to decide whether an LLM's response contains an error. It has 3 tasks: math word-problem generation, fine-grained fact verification, and answerability classification. There are 140 examples per task for GPT-4 responses and 160 per task for Llama-2-70B responses.
- **Extra data:** GSM8K and AIME-2024 (maths, metric = accuracy) and Anthropic-Harmful (safety, metric = attack success rate, where lower is better).
- **Models:** GPT-4o-mini, Llama-3.1-70B, Mistral-7B, Qwen-2.5-72B, DeepSeek-R1 and QwQ-32B; Qwen2.5-7B and Llama3.1-8B for the extra tasks. Temperature is 0 by default.
- **Baselines:** CopMAD (Kenton et al.), CosMAD/SoM, MP (debate with personas), Voting (use the answer if both agree, otherwise pick one at random), single agents, and self-consistency (SC) at matched tokens.
- **Metrics:** F1, and mainly **F2**. F2 is an F-score that weights recall (catching every error) more than precision. The judge is the same model as Debater #1 (Table 1).

**What they found:**
- **Diverse models could help a lot in principle.** With perfect ("oracle") combining, pairs of models from different companies remove over 30% of errors, while same-family pairs remove little (Fig. 2).
- **Old protocols fall below a single agent.** GPT-4o-mini + DeepSeek-R1 under CopMAD scores 24.89 average F2, against 82.20 for GPT-4o-mini alone. CosMAD lands near the average of the two agents, and below Voting (Table 1). The strong agent gives up correct answers to reach early agreement (§2.1).
- **ColMAD is best in every pairing in Table 1.** For example, GPT-4o-mini + Llama-3.1-70B scores 86.29 average F2, against 82.20 for the best single agent, 57.34 for CopMAD and 75.40 for CosMAD. On Llama-2 responses it never falls below the best single agent (Table 7).
- **Matched compute.** At about 14.7K tokens per sample, ColMAD (86.29) beats SC@14 for GPT-4o-mini (81.98, +4.3) and for Llama (77.36, +8.9). SC plateaus within a 3-point band (Fig. 5).
- **Significance.** Over 10 seeds at temperature 1, ColMAD scores 83.38 average F2 (95% CI 82.54 to 84.21), against 80.86 for GPT-4o-mini. It is the only method whose CI does not overlap with the single agents, but only on fact verification and average F2 (Table 12).
- **Same model debating itself fails.** With two GPT-4o-mini debaters, ColMAD scores 80.93 average F2 and CopMAD 61.16, against 82.20 for a single agent. **Every debate method is below the single agent** (App. F.3, Table 9). The authors conclude that heterogeneous (different-model) debaters are a key driver of the gains.
- **Prompt add-ons matter little.** Removing quote checking, confidence and self-audit together only drops F2 from 86.26 to 85.58. The authors credit the collaborative objective itself (Table 8).
- **Robustness.** Changing the judge moves ColMAD by 0.03 F2 but CopMAD by 22.88. CopMAD also gets worse with more rounds, while ColMAD stays stable (App. F.7).
- **Other tasks.** ColMAD gains about 7 points on AIME at 16 calls and pushes Anthropic-Harmful attack success to about 0%, but gives about zero gain on GSM8K, where accuracy is already about 90% (Table 2).
- **Tokens.** ColMAD uses about 15% more tokens than CopMAD (App. F.4, Table 10).

**Limitations and threats to validity (the authors' own):**
- The paper has no limitations or threats-to-validity section. The only self-critique is in App. A, "Discussion and Future Work", plus scattered admissions:
  - ColMAD relies only on prompting, while LLMs are trained on single-agent objectives.
  - ColMAD still shows some failure modes, for example overconfident claims. The underlying calibration problem is that LLMs sound confident about things they cannot verify.
  - Same-model debaters: all debate methods underperform a single agent (App. F.3).
  - In the main setting, the judge is the same LLM as Debater #1. F.3 was added "to probe" this concern.
  - The original ReaLMistake models are "a bit outdated" (§4.1).
  - There is little gain when the base score is already high, as on GSM8K (§4.3).

**Future work they suggest (App. A):**
- Fine-tune debaters with multi-agent objectives, for example rewarding information gain instead of persuasion.
- Train for honesty, penalising confident claims on uncertain points.
- Apply ColMAD to code review, scientific claim checking and content moderation.
- Extend to more than two debaters and to heterogeneous roles, such as specialist verifiers for different requirement types.

**Our own caveats:**
- **Small and binary.** The main tasks are yes/no with 140–160 items each. The main table is a single temperature-0 run, and the 10-seed check covers only one model pair.
- **ColMAD only debates on disagreement.** When the two models agree, it is plain voting. Part of its edge may therefore come from model diversity plus a judge, not from the debate itself.
- **Theory rests on strong assumptions.** It assumes two agents, a binary label and a Bayes-optimal judge. Real LLM judges are not optimal, which the authors admit (§2.2).
- **Matched-compute check covers one model pair only** (GPT-4o-mini + Llama-3.1-70B, Fig. 5). The other pairs in Table 1 are not token-matched.
- **No code or localization tasks.**
- **"Up to 10 points" is an average.** The abstract's "up to 10 percentage points over previous MAD protocols" understates the gap to CopMAD in some rows, for example about 29 F2 points. It likely refers to CosMAD.

**Why it matters to us:**
- **Phase 1 (Diagnose).** SWE-Debate runs 5 copies of the same LLM that vote and then work towards a plan. That is close to CosMAD in a same-model setup, which is exactly where A3 finds that every debate method loses to one agent (Table 9). This gives a concrete hypothesis for our "selection" split: does the debate talk agents out of a correct chain (premature consensus)? We can log how often the debate changes an agent's first choice, and whether the change helps.
- **Phase 2 (Modify).** The results argue for the ColMAD fallback *only* if we use different backbone models. Our plan has one self-hosted model, so we would need a second model on the NTU GPUs. For our primary graph-grounded idea, note that ColMAD's closest equivalent, exact-match quote checking, added only about 0.1 F2 (Table 8). Grounding on its own may not be the active ingredient; the objective may matter more.
- **Phase 1 design.** Their matched-token comparison against self-consistency (Fig. 5) is a model for our single-agent arms.

**Numbers worth quoting in the report:**
- Same-model debate (2× GPT-4o-mini): ColMAD 80.93 and CopMAD 61.16, against 82.20 for a single agent (App. F.3, Table 9).
- Heterogeneous ColMAD (GPT-4o-mini + Llama-3.1-70B): 86.29 average F2, against 82.20 for the best single agent and 57.34 for CopMAD (Table 1).
- Matched tokens (about 14.7K per sample): ColMAD 86.29 against SC@14 at 81.98 (GPT-4o-mini) and 77.36 (Llama) (§4.2, Fig. 5).
- Oracle combining of cross-family model pairs removes over 30% of errors; same-family pairs remove little (Fig. 2).
- Judge swap: ColMAD changes by 0.03 F2, CopMAD by 22.88 (App. F.7).

---

### A4 — Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets (Tran & Kiela, Stanford; arXiv preprint 2604.02460v2, "under review", Apr 2026)

**In one sentence:** When a single LLM (SAS) and a multi-agent system (MAS) get the same "thinking token" budget, SAS matches or beats every MAS design tested on multi-hop QA. MAS only catches up when the single agent's context is heavily corrupted.

**The problem:** MAS usually spend more compute than a single model, so reported MAS gains may come from the extra compute, not the design. The authors ask why SAS might win at a fixed budget, when MAS become competitive, and how to compare them fairly (§1).

**How it works / what they did:**
1. **Theory (§3).** The Data Processing Inequality (processing data can never add information about the answer) implies that messages passed between agents cannot carry more than the full context. So a single agent that *uses its context perfectly* can always do at least as well. If its effective context is degraded, that guarantee breaks, and a structured MAS may help (§3.1).
2. **Budget.** The thinking budget B counts only intermediate reasoning tokens. SAS gets all of B in one call, and each MAS splits B across its agents.
3. **Systems (§4.2–4.3).**
   - SAS.
   - SAS-L: SAS plus a prompt telling it to list ambiguities and interpretations before answering.
   - Five MAS:
     - **Sequential** (the main comparator): a planner, then step-workers, then an aggregator.
     - Subtask-parallel.
     - Parallel-roles: Solver, Fact Extractor, Skeptic and Second Solver.
     - **Debate**: 2 debaters answer, critique each other once, then a judge picks.
     - Ensemble: workers at temperature 0.7, then a judge picks.
4. **Degradation test (§5.3).** They corrupt text with deletion, masking or random-token substitution (fraction α), or add k distractor sentences, then compare SAS with Sequential.

**How they tested it:**
- Data: FRAMES and MuSiQue (4-hop only). Sizes are not stated; the Table 2 buckets add up to 1,175 MuSiQue items.
- Models: Qwen3-30B-A3B, DeepSeek-R1-Distill-Llama-70B, Gemini-2.5-Flash and Gemini-2.5-Pro. A version sweep adds Gemini-2-Flash-Lite, 2-Flash and 3-Pro-Preview.
- Budgets: 100 to 10k thinking tokens.
- Metric: accuracy by LLM-as-judge (a model checks whether the gold answer's meaning appears in the prediction). The judge is the same model that answered (App. D.7). Results carry 95% bootstrap confidence intervals (CIs).

**What they found:**
- SAS is best, or statistically tied with the best, at every budget above 100 tokens (Table 1).
  - Averages at 1k: SAS 0.418, Debate 0.388, Sequential 0.379.
  - Averages at 10k: SAS 0.426, Debate 0.420, Sequential 0.387.
- SAS spends far fewer *actual* tokens. Qwen3 FRAMES, 10k cap: SAS used 1,307, Debate 4,061, Ensemble 5,571 (Table 3).
- Debate is the most consistently strong MAS. Accuracy plateaus around 1k–2k tokens. SAS-L helps mainly on Gemini (§5.1).
- The pattern SAS ≥ Sequential holds across Gemini generations, e.g. 3-Pro-Preview 0.491 vs 0.489 (Table 12).
- MAS wins only under heavy corruption. At α=0.7, substitution gives SAS 0.200 vs Sequential 0.225. With distractors, SAS leads at every level (Table 13).
- Gemini's API over-reports thinking tokens. For Flash SAS at 10k, the API reported 1,687, but the visible thoughts were about 359 tokens (4.7x). Visible SAS thinking plateaus at about 350 tokens (App. G).
- Error analysis (App. B, Table 2):
  - When MAS wins, the gold answer appears in its thoughts more often (Gemini 41.7% vs 12.5%).
  - When SAS wins, MAS had "over-explored and drifted".
  - Both systems sometimes found the gold answer in their reasoning but dropped it from the final answer.
- Deep paraphrasing *raised* accuracy (Gemini-Flash SAS 0.331 → 0.358), which hints that the models memorised the original questions (App. A).

**Limitations and threats to validity (the authors' own):** App. C lists three. The paper has no threats-to-validity section.
- Text-only multi-hop reasoning only. Tools, vision and safety settings are out of scope.
- Gemini token accounting is approximate. They report API counts and visible-text counts, and compare systems at the same *requested* budget. They say a comparison based on observed tokens is "intractable" (App. G).
- They cap only the maximum budget and do not force models to use it all.

**Future work they suggest:**
- Study the specific regimes where multi-agent structure gives a real benefit (§6).
- Researchers should acknowledge the token-count discrepancy, and API providers should explain how thinking tokens are counted (App. G).
- Use deep paraphrasing to build more reliable benchmarks (App. A).

**Our own caveats:**
- "Matched" means the same cap, not the same spend. MAS spent 2–4x more and still lost, which strengthens their claim but is not strict compute matching.
- The judge model grades its own answers, and no human validation is reported. The number of runs is not stated. One point lies outside its own CI (Table 8: Debate at 10k, 0.458 with CI 0.461–0.477).
- The degradation setup is described inconsistently. §5.3 says it corrupts the context; App. E says it corrupts the model's generated thinking. It also uses only Qwen3, one budget and one dataset.
- Their Debate (2 agents, 1 critique) is much lighter than SWE-Debate's. The domain is QA, not code.

**Why it matters to us:**
- **Phase 1:** This is the template for our compute-matched 2x2. Fix the budget per arm, log actual tokens as well as caps, and use bootstrap CIs. Self-hosted vLLM gives exact token counts, which avoids their Gemini problem.
- **Phase 1 hypothesis:** Expect single-agent localization to match debate at equal compute, unless the context is noisy. SWE-Debate's ~20 candidate chains may be exactly the "degraded context" case where MAS helped.
- **Phase 2:** Their failure types map onto our retrieval-vs-selection split. "Gold in thoughts but dropped from the final answer" is a selection failure, and "drift" is another.
- **Phase 3:** The paraphrase result supports using post-cutoff SWE-bench-Live issues.

**Numbers worth quoting in the report:**
- 1k budget, average accuracy: SAS 0.418 vs Debate 0.388 vs Sequential 0.379 (Table 1).
- Qwen3 FRAMES, 10k cap: SAS 0.263 using 1,307 tokens vs Debate 0.240 using 4,061 (Table 3).
- Substitution at α=0.7: Sequential 0.225 > SAS 0.200, the only clear MAS win (Table 13).
- Gemini-2.5-Flash API over-counts thinking tokens by 4.7x (App. G).

---

### A5 — A Multi-Agent Approach to Fault Localization via Graph-Based Retrieval and Reflexion ("LLM4FL"; Rafi, Kim, Chen, Wang; arXiv 2409.13642v2, Mar 2025)

**In one sentence:** LLM4FL is a pipeline of three GPT-4o-mini agents. They split test-coverage data into chunks, walk the call graph to rank suspicious Java methods, then self-critique the ranking. It beats earlier LLM fault localizers on Defects4J.

**The problem:** Classic fault localization such as SBFL (spectrum-based fault localization: score code by how often failing vs passing tests run it) is cheap but inaccurate. Learning-based methods need training data. LLMs need no training, but whole repositories exceed their token limits, accuracy drops on long inputs, and they struggle with call relationships between methods (§1).

**How it works / what they did** (§3, Fig. 1):
1. **Context Extraction Agent.**
   - Collects the methods covered by the failing test (with the GZoltar tool) and sorts them by Ochiai score (a standard SBFL formula).
   - Splits them into K groups that fit the context window. This is "order-aware division".
   - Prunes the stack trace (drops external libraries) and the test code (drops everything after the failing assertion), then writes a "failure reason".
   - Uses that failure reason to shortlist suspicious methods in each group.
2. **Debugger Agent (Graph-RAG, i.e. retrieval over a graph).**
   - Builds a caller/callee call graph from the coverage data.
   - Has two tools: `get_MethodBody` and `get_CallGraph`. For each shortlisted method it reads the code, can walk to neighbouring methods, and writes a failure reason per method.
   - Outputs a ranked list.
3. **Reviewer Agent (Reflexion).** "Verbal reinforcement learning" means the model critiques its own output in words and revises it. The agent re-checks the ranking, may fetch more code, and iterates until the ranking stabilises or hits an iteration limit. Finally it writes a probable fix for each method and re-ranks (chain-of-thought).

**How they tested it** (§4):
- Data: Defects4J v2.0.0, 675 real Java bugs from 14 projects (2K–90K lines of code; Table 2). Three projects were excluded because coverage collection failed (JacksonDatabind, JxPath, Chart).
- Granularity: method level.
- Model: gpt-4o-mini, temperature 0.
- Baselines: Ochiai (statistical); DeepFL, Grace and DepGraph (trained neural or graph neural models); AutoFL and SoapFL/AgentFL (LLM-based, re-run with gpt-4o-mini).
- Metric: Top-N, the number of bugs where a truly faulty method appears in the top N of the ranking (N = 1, 3, 5, 10).
- Cost: token usage × price.

**What they found:**
- **RQ1 (Table 3), Top-1:** LLM4FL 326, SoapFL 311 (+4.82%), AutoFL 275 (+18.55%), Grace 298, DeepFL 257, Ochiai 121. The *supervised* DepGraph still wins Top-1 with 359, and also wins Top-3/5/10.
- Cost per bug: LLM4FL about $0.050, SoapFL about $0.055, AutoFL about $0.065 (§4 RQ1).
- **RQ2 ablation (Table 4), Top-1 from a base of 327:**
  - Without division: 251 (−23.24%).
  - Without code navigation: 273 (−16.51%).
  - Without Reflexion: 290 (−11.31%).
  - Self-critique helped even though no external feedback or ground truth was given.
- **RQ3 ordering (Fig. 3), Top-1:** raw execution order 299, Ochiai order 323, DepGraph order 366. The initial order changes Top-1 by up to 22%, even though the LLM eventually sees every method. Closer-to-truth input order gives a better final result.

**Limitations and threats to validity (the authors' own, §5):**
- *Internal:* The LLM may have seen Defects4J during training (data leakage). They argue with Ramos et al. that larger, newer models show limited leakage. They also kept project names, bug reports and bug IDs out of the prompts.
- *External:* Only Defects4J, and mostly Java, so results may not generalise to other languages or domains.
- *Construct:* Top-N assumes developers only look at the top-ranked methods. Different development practices could change how useful the approach is.

**Future work they suggest:**
- Scale LLM4FL to larger and more diverse codebases (§6).
- Further refine how the agents collaborate and reason (§6).
- Extend the evaluation to other programming languages and domains (§5).
- Explore other ordering strategies, and use traditional SE techniques to pre-process LLM inputs (RQ3).
- Study whether input order matters in other SE tasks that take a list of artifacts (RQ3).
- Use self-reflection even without external feedback, and adopt coverage division and code navigation in future FL tools (RQ2).

**Our own caveats:**
- **Setting:** The input is a failing test with coverage and stack trace, not a GitHub issue. That is a different setting from SWE-Debate and SWE-bench.
- **Not debate:** "Multi-agent" here means a sequential pipeline of roles. Nobody argues or votes, so it tells us nothing about debate itself.
- **No compute matching:** The ablations remove whole stages. There is no single-agent baseline with the same token budget, so gains may simply come from more LLM calls.
- **Single run:** One run at temperature 0, with no variance or significance tests.
- **Internal inconsistencies:**
  - Top-1 is 326 in Table 3 but 327 in Table 4, and the Ochiai-ordered run gives 323 in Fig. 3.
  - The results text says "185.55%" where 18.55% is meant.
  - The RQ2 text says "removing prompt chaining" is the second-largest drop, but no row has that name.
- **Weak leakage mitigation:** Well-known Defects4J bugs could still be recognised from their code.
- **Training-free only in the default setup:** The best DepGraph ordering relies on a trained GNN.
- **Paper metadata:** The ACM template placeholders were never filled in, so the paper is unrefereed as given.

**Why it matters to us:**
- **Phase 1:** The ordering result warns that SWE-Debate's candidate-chain order may bias the agents' votes. We should log the order of the chains, and possibly shuffle them as a control. The ablation shows graph navigation adds about 17% in Top-1, which is support for grounding localization in a graph.
- **Phase 2:** It is a precedent for agents that query a code graph through tools (`get_CallGraph`, `get_MethodBody`). That is close to our "agents must cite checkable graph facts" idea. The Reflexion result is a single-agent alternative to debate, which is another reason for our equal-compute controls.
- **Framing:** It is one of the few multi-agent fault-localization papers, and it shows the field reports multi-agent gains without compute matching. That supports our gap statement.

**Numbers worth quoting in the report:**
- Top-1 on Defects4J (675 bugs): LLM4FL 326 vs SoapFL 311 vs AutoFL 275, but supervised DepGraph 359 (Table 3).
- Ablation Top-1: removing division gives −23.24%, removing graph navigation −16.51%, removing Reflexion −11.31% (Table 4).
- Input ordering changes Top-1 from 299 to 366, up to 22% (Fig. 3, RQ3).
- About $0.05 per bug with gpt-4o-mini (RQ1).

---

### A6 — LocAgent: Graph-Guided LLM Agents for Code Localization (Chen, Tang, Deng et al.; Yale/USC/Stanford/All Hands AI; arXiv 2503.09089v2, Apr 2025)

**In one sentence:** LocAgent turns a Python repository into a typed code graph and gives one LLM agent three tools to search and walk it. It gets the best localization scores on SWE-bench-Lite, and fine-tuned open Qwen models come close to Claude-3.5 at about 1/7 of the cost.

**The problem:** Code localization means finding the files, classes and functions that must change to resolve an issue. Issues often describe symptoms, not causes, so the right code can be several dependency "hops" away from anything the issue names. Embedding retrieval ignores code structure. Existing agents mostly browse directories and grep, so they miss dependencies across files (§1–2).

**How it works / what they did:**
1. **Graph (§3.1).** Parse each Python file's AST (abstract syntax tree) to get directory, file, class and function nodes. Add *contain*, *import*, *invoke* (calls) and *inherit* edges. Indexing takes seconds per repo.
2. **Sparse index.** Look up entities in layers: exact ID → name dictionary → BM25 (a keyword-matching ranker) over IDs → BM25 over code chunks.
3. **Three tools (Table 2).**
   - `SearchEntity`: keyword search.
   - `TraverseGraph`: breadth-first search where the agent picks direction, number of hops, and node and edge types. The output is an indented tree, the best of six formats in a 37-sample test (Table 9).
   - `RetrieveEntity`: fetches full code.
4. **Agent.** A chain-of-thought prompt guides it through four steps (App. D):
   - extract keywords from the issue;
   - link them to graph entities;
   - trace the logic from fault to failure;
   - output ranked locations.

   Two runs at temperature 1.0 are merged by reciprocal-rank score (App. A.2).
5. **Fine-tuning (§3.3).** Qwen2.5-Coder 7B and 32B, fine-tuned with LoRA only on *successful* trajectories from the SWE-bench training set. The trajectory counts differ between sections: §3.3 says 433 from Claude-3.5 plus 335 from the 32B model, while App. C.1.3 says 447 from Claude.
6. **Loc-Bench (§4).** A new benchmark of 560 Python issues: 242 bug, 150 feature, 139 performance, 29 security. The bug issues were created after Oct 2024, to limit contamination.

**How they tested it:**
- Data: SWE-bench-Lite filtered to 274 of 300 issues, plus Loc-Bench.
- Baselines: BM25 and 4 embedding retrievers; Agentless; SWE-agent, OpenHands and MoatlessTools, each with GPT-4o and Claude-3.5.
- Metric: Acc@k. A hit needs *all* gold locations in the top k, which is strict. It is reported at three levels:
  - file;
  - module (any function in the patched class);
  - function.
- Ranking quality: NDCG, a score that rewards putting correct items near the top (Table 11).
- Downstream: Agentless repair with Claude-3.5, scored by Pass@k (an issue counts as solved if any of k patches passes the tests).

**What they found:**
- **SWE-bench-Lite (Table 4):**
  - LocAgent with Claude-3.5 is best at every level: file Acc@5 94.16, function Acc@10 77.37.
  - Fine-tuned Qwen-32B: 92.70 and 77.01.
  - Best baseline, OpenHands with Claude: 90.15 and 70.07.
- **Difficulty (Fig. 3).** Difficulty here means graph hops from the functions named in the issue to the patched functions. Every method gets worse as hops grow. Agents degrade least; Agentless collapses once the hop count is 1 or more.
- **Cost per example (Table 5):**
  - Qwen-7B(ft) $0.05 and Qwen-32B(ft) $0.09.
  - LocAgent with Claude $0.66, OpenHands with Claude $0.79.
  - Rounds per example range from 5 to 15.
- **Ablation with Qwen-7B(ft) (Table 6), function Acc@10:**
  - Full system: 71.53.
  - Without SearchEntity: 53.28.
  - Without the BM25 index: 60.22.
  - Without TraverseGraph: 66.06.
  - Contain edges only: 66.42.
  - Hops fixed at 1: 66.79.
- **Loc-Bench (Table 7).** LocAgent with Claude: file Acc@5 83.39, function Acc@15 60.71. OpenHands: 79.82 and 59.29. All methods are weaker on non-bug issues (Fig. 5).
- **Downstream (Table 8).** Pass@10 rises from 33.58 with Agentless localization to 37.59 with LocAgent + Claude; that is the "+12%" in the abstract. Pass@1 rises only from 26.31 to 27.92.

**Limitations and threats to validity (the authors' own):** The paper has a "Limitations" section and no threats-to-validity section. Their items:
- Only Qwen-2.5-Coder was fine-tuned. Other open models (CodeLlama, Mistral, Yi) are untested.
- Only LoRA was tried.
- The downstream test covers only bug repair.
- The fine-tuning data leans heavily on Claude-3.5 trajectories.
- Python only.
- Metrics are limited to accuracy and NDCG.
- Performance is weaker on feature, performance and security issues, probably because the training data was mostly bug reports (§5.7).

**Future work they suggest:**
- Try more base models, and other fine-tuning methods such as full fine-tuning.
- Evaluate downstream on refactoring, feature addition, security patching and performance optimisation.
- Use more diverse training data (other models, tasks, repos), and study how data composition and filtering affect results.
- Support other programming languages.
- Develop more nuanced localization metrics.
- Use balanced training data and category-specific optimisation for non-bug issues (§5.7).
- Keep refreshing Loc-Bench as model training cutoffs advance (§1).

**Our own caveats:**
- It is a single agent. The paper has no multi-agent comparison and no compute matching (rounds range from 5 to 15).
- No variance is reported. The ablations use only the 7B model.
- The paper gives inconsistent numbers:
  - trajectory counts (433 vs 447);
  - cost reduction, stated as both "over 80%" and "86%".
- The Loc-Bench table omits Qwen-32B(ft). Only the bug issues are stated to be post-Oct-2024.
- A static graph cannot resolve dynamic Python calls. The paper does not discuss this.

**Why it matters to us:**
- **Phase 1, reachability:** LocAgent's graph is the same kind of static AST graph that SWE-Debate walks. Its hop-distance difficulty measure (App. C.1.2) is a ready-made way to group issues by how far the fault sits from the issue text. The drop with contain-only edges shows which edge types drive reachability.
- **Phase 1, baseline:** It is a strong *single-agent*, graph-grounded localizer, a natural reference for our "graph, no debate" arm. We should match its strict Acc@k definition, or say clearly how ours differs.
- **Phase 2:** `TraverseGraph` and `SearchEntity` are exactly the kind of checkable graph queries that graph-grounded debaters could cite. Tree-formatted subgraphs read best (Table 9).
- **Phase 3 / backbone:** Loc-Bench's post-cutoff design mirrors our SWE-bench-Live plan. The Qwen results show that an open-weights model on vLLM can be competitive.

**Numbers worth quoting in the report:**
- SWE-bench-Lite (274 issues): LocAgent with Claude-3.5 reaches file Acc@5 94.16 and function Acc@10 77.37, vs 90.15 and 70.07 for OpenHands with Claude (Table 4).
- Fine-tuned Qwen-32B reaches 92.70 and 77.01 at $0.09 per example, vs $0.66 with Claude (Tables 4–5).
- Removing TraverseGraph cuts function Acc@10 from 71.53 to 66.06 (Table 6).
- Better localization lifts Pass@10 from 33.58 to 37.59, but Pass@1 only from 26.31 to 27.92 (Table 8).

---

### A7 — SWE-bench: Can Language Models Resolve Real-World GitHub Issues? (ICLR 2024; arXiv v3, Nov 2024)

**In one sentence:** SWE-bench is the standard benchmark for our area: 2,294 real GitHub issues from 12 Python repos, where a model must write a patch (a code change) that makes the repo's own tests pass.

**The problem:** Older coding benchmarks such as HumanEval ask for short, self-contained functions. Real bug fixing is harder. You must find the right place in a codebase with thousands of files, understand how files depend on each other, and edit several places at once. The authors wanted a benchmark that is realistic but still easy to grade automatically, by running tests (§1).

**How it works / what they did:**
1. **Collect PRs (§2.1, App. A.1).** Take about 90,000 pull requests (PRs) from 12 popular Python repos, e.g. django, sympy and scikit-learn (93,139 exactly, Table 10).
2. **Filter by attributes.** Keep merged PRs that (a) fix a linked issue ("fixes #24") and (b) change test files.
3. **Filter by execution.** Run the tests before and after applying the PR's code change. Keep a task only if it installs and runs, and at least one test goes **fail → pass** (a *FAIL_TO_PASS* test). Tests that pass both before and after are recorded as *PASS_TO_PASS*: they check that nothing else broke. Tasks are also dropped if their tests call new functions whose names the issue text never gives (App. A.1).
4. **Result.** 93,139 PRs → 11,407 candidates → **2,294 tasks** (Table 10).
5. **The task (§2.2).**
   - **Input:** the issue text plus the repo at the PR's base commit.
   - **Output:** a patch file.
   - **"Resolved"** means the patch applies *and* every FAIL_TO_PASS and PASS_TO_PASS test passes (App. A.4).
6. **Extras.**
   - **SWE-bench Lite:** 300 more self-contained tasks focused on functional bug fixes, from 11 of the 12 repos (§2.4).
   - **SWE-bench-train:** 19,000 issue–PR pairs from 37 *other* repos.
   - **SWE-Llama 7b/13b:** CodeLlama-Python fine-tuned on SWE-bench-train with LoRA (a cheap fine-tuning method) (§3).

**How big the tasks are (Table 1):**
- **Issue text:** 195 words on average.
- **Codebase:** about 3,010 non-test files and 438K lines on average.
- **Gold patch** (the real human fix): edits **1.7 files, 3.0 functions and 32.8 lines** on average. The median task edits one function and about 15 lines (App. A.5).

**How they tested it:**
- **Retrieval (§4.1).** Whole repos do not fit in the context window, so a retriever picks which files to show the model:
  - **BM25** (a classic keyword-match search) retrieves files up to a 13k/27k/50k-token limit.
  - **"Oracle"** retrieval simply gives the files the gold patch edits. It is unrealistic and is used only for analysis.
- **Models (§4.3, Table 5).** ChatGPT-3.5, GPT-4, Claude 2 and SWE-Llama. Claude 3 Opus and GPT-4-turbo were added in the v3 version. One greedy sample per task (App. D.2).
- **Metrics.**
  - **% Resolved:** tests pass.
  - **% Apply:** the patch applies cleanly.
  - **BM25 recall:** the share of gold-patch files that BM25 found.

**What they found:**
- **Very low scores.** The best BM25 result is **Claude 2 at 1.96%** in the original paper (Table 2). With the v3 additions, Claude 3 Opus reaches 3.79% (Table 5). Oracle retrieval raises Claude 2 to 4.8% (Table 18).
- **Retrieval often misses the right file (Table 3, §4.1).** At a 27k-token limit:
  - BM25 finds *all* gold files in only 39.83% of tasks, and *any* gold file in 51.27%.
  - In almost half the tasks it finds *none* of them.
- **More context makes results worse.** Claude 2 drops from 1.96% (13k) to 1.87% (27k) to 1.22% (50k) even though recall rises (Table 2). The authors say models "are simply ineffective at localizing problematic code" (§5).
- **Showing only the relevant lines helps.** Giving just the edited lines ±15 lines ("oracle-collapsed") raises GPT-4 from 1.3% to 3.4% and Claude 2 from 4.8% to 5.9% (Table 6).
- **No clear effect of task date** (Tables 7, 21). Results before and after 2023 are similar, so the authors think models are not simply "cheating" from memory.
- **Most failed patches do nothing useful.** Among patches that apply but fail, most pass zero FAIL_TO_PASS tests (Table 23). Of those, 60–70% change nothing that matters ("No-Op"); the rest break existing behaviour. The authors blame the baselines' lack of inter-file dependency information (App. C.5).

**Limitations and threats to validity (the authors' own):**
The paper has no separate threats section. §7 "Limitations and future directions" says:
- **Python only.**
- **Simple baselines on purpose.** The experiments use only the simplest retrieval + one-shot generation methods, not agents or tool-using systems.
- **Tests are not a full check of quality.** Passing tests does not guarantee a good patch. Model patches can be less complete, efficient or readable than human ones. App. C.7 shows an example where a passing patch adds more complexity than the gold patch.

Other caveats stated in the text:
- GPT-4 was run on only a 25% random subset (574 tasks) because of budget (Table 7, Table 18, App. C.3).
- The oracle setting is unrealistic, and even the gold files may not hold all the context needed (§4.1).
- 32% of matplotlib and 10% of seaborn issues contain images, which may need multimodal models (§5).
- SWE-Llama was trained with oracle context, so it performs poorly when given BM25 context (§5).
- Token counts differ across tokenizers: Llama-tokenized text is about 42% longer than GPT-4's (Table 4).

**Future work they suggest:**
- Extend the collection pipeline to other programming languages and domains (§7, App. A.1).
- Try agent-based and tool-augmented approaches (§7).
- Keep adding new tasks created after each model's training date (§2.3, App. A.1).
- Give models execution feedback, so they can run tests and keep editing before they submit (App. C.5).
- Use the unused `hints_text` field (App. A.2).
- Use software-engineering metrics such as cyclomatic complexity (the number of independent paths through the code) to judge patch quality (App. C.7).
- Use it as a testbed for safe AI coding (App. E).

**Our own caveats:**
- **Old issues, likely seen in training.** The tasks come from PRs made up to 2023, so today's models have probably seen them. The date analysis in Tables 7 and 21 used 2023-era models. A8 later finds signs of overfitting to SWE-bench repos.
- **Some tasks are unclear or unsolvable.** Humans never checked whether each issue text is clear or whether its tests are fair. That was why SWE-bench Verified came later.
- **Small repo set.** 850 of the 2,294 tasks (37%) come from django (Fig. 3).
- **Lite details are missing from our copy.** The App. A.7 text on how Lite was filtered is cut off in our extracted copy, so we cannot quote its filter rules from here.

**Why it matters to us:**
- **Task and metric definitions.** SWE-bench defines the task, the data fields (`base_commit`, `patch`, `FAIL_TO_PASS`) and "% Resolved", which SWE-Debate (A1) uses on SWE-bench Lite.
- **Phase 1 (retrieval vs selection).** The paper already shows that *localization is the bottleneck*: BM25 misses every gold file in about half the tasks, and oracle files roughly double the resolve rate. This motivates separating "is the right file even reachable" (our graph ceiling) from "did the debate pick it".
- **Localization labels.** Our file-level labels come from the gold `patch` field, the same way oracle retrieval does (App. D.1).
- **Phase 3.** The contamination concern here is why we validate on SWE-bench-Live (A8).

**Numbers worth quoting in the report:**
- 2,294 tasks, 12 repos; gold patch averages 1.7 files, 3.0 functions, 32.8 lines (Table 1).
- BM25 at 27k tokens finds all gold files in 39.83% and any gold file in 51.27% of tasks (Table 3).
- Claude 2 resolves 1.96% with BM25 vs 4.8% with oracle files (Table 2, Table 18).
- Claude 2's resolve rate falls from 1.96% to 1.22% as BM25 context grows from 13k to 50k tokens (Table 2).

---

### A8 — SWE-bench Goes Live! (Microsoft; arXiv preprint 2505.23419v2, June 2025, written in NeurIPS format)

**In one sentence:** SWE-bench-Live is a version of SWE-bench that is updated every month from fresh GitHub issues, built by an automated pipeline, and the same agents score much lower on it than on the old benchmark.

**The problem:** SWE-bench (A7) has three weaknesses, listed in §1:
- **Staleness.** It was never updated, so its tasks may have leaked into LLM training data (*contamination*). High scores could then be memory, not skill.
- **Few repos.** It covers only 12 repositories.
- **Manual effort.** Building each runnable test environment by hand is slow. SWE-Gym needed 200+ hours of manual work (§3.2), and Multi-SWE-bench took about one year with 68 annotators (footnote 2).

**How it works / what they did:**
1. **Pick repos (§3.1).** Python repos on GitHub with >1,000 stars (8,577 repos). Keep those with >200 issues/PRs, >200 forks and ≥60% Python code (3,316). Keep only those with an open-source license (2,609).
2. **Pair issues with fixes (§3.1).** Find issues that were fixed by a pull request (PR) that also changes the tests. They reuse SWE-bench's script plus SWE-Fixer's heuristics. Only issues created after January 2024 are used.
3. **REPOLAUNCH (§3.2).** An LLM agent builds a Docker environment for each task. It (a) finds setup files such as README and CI configs, (b) picks a base image (e.g. `python:3.11`), (c) runs bash commands in a ReAct loop (think → act → observe) until the tests run, and may search the web, (d) hands over to a second "verify" agent that writes the test command and checks the result, and (e) saves the container as an image.
   - A **"time-machine"** pip proxy only allows package versions released before the task's base commit. This stops newer libraries from breaking old code.
4. **Validate each task (§3.3).** A task is kept only if at least one test goes from failing to passing when the real fix is applied (**FAIL_TO_PASS**). Tests that pass both before and after are recorded as **PASS_TO_PASS** (checks the fix breaks nothing). The runs are repeated, and tasks with *flaky* (inconsistent) results are dropped.

**What the dataset contains (§3.4, Table 2):**
- **Full set:** 1,319 tasks from 93 repos. Issues were created between 1 Jan 2024 and 20 Apr 2025.
- **Lite subset:** 300 tasks, 50 per month from Oct 2024 to Mar 2025 (random seed 42).
- **Repo size:** on average 85k lines of Python and 423 files per repo.
- **Gold fix size:** the real ("gold") fix touches 3.3 files on average (median 2). It changes 102.6 lines on average (median 24).
- **Updates:** monthly updates are planned.

**How they tested it (§4.1, App. E):**
- **Agents:** OpenHands (max 60 iterations), SWE-agent (max 100 LLM calls) and Agentless. Agentless was run with one sample and *without* its regression-test reranking step.
- **Models:** GPT-4o, GPT-4.1, Claude 3.7 Sonnet and DeepSeek V3. Temperature 0 (except 0.8 in Agentless localization).
- **Metrics:**
  - **Resolved %:** the patch makes the tests pass.
  - **Apply %:** the patch applies cleanly to the code.
  - **Localization Success %:** the set of files the patch edits *matches* the gold patch's files (file level).

**What they found:**
- **Low scores.** The best result on the full set is **19.25%**, from OpenHands + Claude 3.7 Sonnet (Table 4). Leaderboard scores on SWE-bench Verified are above 60%.
- **Same setup, fewer solves (§4.2).** The same OpenHands + Claude 3.7 setup, re-run on SWE-bench Verified, scores **43.20%**, more than double. The authors read this as a sign of overfitting to SWE-bench.
- **Old SWE-bench repos are easier for agents (Table 5).** Tasks from the 8 repos that are also in SWE-bench (216 tasks) are solved at 22.96%. Tasks from the other repos (1,103 tasks) are solved at 18.89%, even though those repos are smaller: 68k vs 223k LoC on average.
- **File-level localization is weak.** On Lite it ranges from 28.67% to 48.00%; on Full it is 45.86–49.50% for the top 3 (Tables 3–4).
- **No trend over time (Fig. 4):** solve rate by quarter (2024Q1–2025Q1) is roughly flat.
- **Bigger fixes fail more (Fig. 5).**
  - A fix touching 1 file and fewer than 5 lines is solved **48%** of the time.
  - A fix touching 3 or more files, or more than 100 lines, is solved less than 10% of the time.
  - A fix touching 7 or more files is never solved.
- **Bigger repos fail more (Fig. 7).** Repos with more than 500 files are rarely solved above 5%.

**Limitations and threats to validity (the authors' own):**
From App. F "Limitations" and the checklist:
- **LLM randomness.** Each experiment was run **once** because of budget. They tried to reduce the randomness with temperature 0, top_p 0 and a fixed environment. Note that App. E says top_p = 1.0, which contradicts App. F.
- **No error bars or significance tests** (checklist item 7).
- **Python only.**
- Also, in §4.1: Agentless's reranking stage was left out because it needs too much infrastructure. This means the Agentless numbers are not its full pipeline.

**Future work they suggest:**
- Extend SWE-bench-Live to other languages, e.g. Java and Go (App. F).
- Update the dataset monthly (§3, §3.4).
- Open-source REPOLAUNCH, which could also help developers set up unfamiliar codebases (§3.2).

**Our own caveats:**
- **"After Jan 2024" is not the same as "after our model's cutoff".** The benchmark's start date does not match any particular model's training cutoff, so we must filter by issue date ourselves.
- **The overfitting evidence is suggestive, not proof.** The gap from 43.2% to 19.25% mixes contamination with other changes (different repos, different difficulty), and each result is a single run.
- **Their localization metric requires an exact match of the edited file set.** Ours is "is the gold file in the candidate set / top-k". The numbers are not directly comparable.
- **No human check** that each issue text is clear enough to solve (unlike SWE-bench Verified).

**Why it matters to us:**
- **Phase 3 (Validate):** this is our validation set. Its instance fields (`base_commit`, `problem_statement`, `patch`, FAIL_TO_PASS) match SWE-bench (Table 6), so SWE-Debate's pipeline should transfer. We only need the gold patch's files for localization, and probably not the Docker images.
- **Contamination:** the 43.2% vs 19.25% gap is a strong reason to validate on issues created after the model's cutoff. SWE-Debate's results come from SWE-bench Lite.
- **Phase 1 (reachability ceiling):** multi-file fixes are common here (mean 3.3 files), and large repos are hard. Both can lower how often the gold file appears in a candidate chain. We should report the ceiling separately on Live.

**Numbers worth quoting in the report:**
- 1,319 tasks, 93 repos, issues from 1 Jan 2024 to 20 Apr 2025; Lite = 300 tasks (§3.4).
- Best resolved rate 19.25% on SWE-bench-Live vs 43.20% on SWE-bench Verified, same OpenHands + Claude 3.7 Sonnet setup (Table 4, §4.2).
- 22.96% on tasks from the old SWE-bench repos vs 18.89% on tasks from new repos (Table 5).
- File-level localization success is only 45.86–49.50% for the top-3 systems on the full set (Table 4).
- Fixes touching 1 file and fewer than 5 lines: 48% solved; 7 or more files: 0% (Fig. 5).

---

### A9 — Rethinking the Value of Multi-Agent Workflow: A Strong Single Agent Baseline (arXiv preprint 2601.12307, Jan 2026)

**In one sentence:** If every agent in a multi-agent system uses the same LLM, one LLM playing all the roles in a single conversation does about as well, and is cheaper because it can reuse its KV cache.

**The problem:** Most multi-agent systems (MAS) are *homogeneous*: every agent is the same base LLM, and only the prompt, tools and position in the workflow differ. So is having several separate "agents" really needed? Or can one LLM act out each role in turn in one long chat and get the same result? (§1, §2)

**How it works / what they did:**
1. **A formal argument (Proposition 1, §3.1).** A workflow is a graph of agents. If (i) tools are deterministic, (ii) routing depends only on what is visible in the history, and (iii) decoding is deterministic (e.g. greedy), then one LLM that swaps in each agent's prompt at each step gives the *same distribution of transcripts* as separate agents.
2. **The cost argument (§3.1).** Separate agents re-read (re-"prefill") the shared context every time. One conversation keeps a *KV cache* (the stored attention keys/values of tokens already read), so it only pays for the *new* tokens. Cost is never higher, and equal only when agent contexts do not overlap.
3. **The simulator (§3.2).** Keep one chat history. At each step, append the next agent's system prompt as a user message, call the model, append any tool output, and follow the workflow's routing.
4. **OneFlow (§3.3, Alg. 1, App. A.2–A.3).** A workflow-search method built on AFlow. It uses MCTS (Monte Carlo Tree Search, a trial-and-error tree search) for 20 rounds. It starts from a plain input→output workflow. Each round, a "Creative Designer" LLM proposes a change aimed at accuracy, and a "Critical Reviewer" LLM edits it to cut cost. The objective is α·performance − β·cost (Eq. 1). It is scored on a 20% validation split.

**How they tested it:**
- **Benchmarks (§4.1, App. A.7):** HumanEval (131 test problems), MBPP (341), GSM8K (1055), MATH (486), HotpotQA (800), DROP (800), TravelPlanner (180), and 10 Shopping-MMLU tasks. They picked those 10 because Claude 3.5 Sonnet scored under 80% on them.
- **Models:** GPT-4o-mini runs the workflows (temperature 0). Claude 3.5 Haiku and Qwen-3 8B (served with vLLM, 16k context) are used as robustness checks. Claude-4-Sonnet designs the workflows.
- **Baselines:** IO (direct answer), CoT (chain-of-thought), CoT self-consistency ×5 (majority vote over 5 samples), MultiPersona, AFlow, and a *heterogeneous* AFlow workflow that mixes GPT-4o-mini with Claude 3.5 Haiku.
- **Metrics:** pass@1 (share of coding problems solved on the first try); F1 (word overlap with the gold answer) for QA; solve rate for math; accuracy; task success rate; USD cost. They also report latency and throughput for Qwen. Results are the mean ± std over 3 runs.
- **Note:** GPT-4o-mini is a closed API, so its KV-cache savings are *simulated* by costing the final message list, not measured (§4.1).

**What they found:**
- **One agent matches many (Table 1).** Running the AFlow and OneFlow workflows as a single agent gives about the same accuracy, e.g. OneFlow HumanEval 91.6 → 92.1 and MBPP 81.1 → 81.4. One clear exception: AFlow on HotpotQA drops from 72.1 to 68.4.
- **Cheaper (Table 2).** AFlow on HotpotQA costs $1.438 as multi-agent vs $0.530 as a single agent; on GSM8K, $1.134 vs $0.697. OneFlow is already much cheaper than AFlow (HumanEval $0.026 vs $0.198).
- **Open-weights check (Table 4, Qwen-3 8B, HumanEval).** AFlow scores 86.8% with separate stateless calls vs 90.5% as a single agent. Latency is about the same (54.98 s vs 53.53 s) even though the single agent reads +967 more input tokens. Qwen writes longer answers in multi-turn chats, which eats into the savings (§4.2.4).
- **Heterogeneous pilot (Table 3, §4.2.3).** The mixed GPT-4o-mini + Haiku workflow is "largely bounded by" the best single-model workflow. Example: DROP F1 85.5 vs 87.5 for OneFlow on Haiku alone.
- **TravelPlanner (Fig. 3).** The single-agent versions keep the same success rate at lower cost.

**Limitations and threats to validity (the authors' own):**
The paper has **no limitations or threats-to-validity section**. Caveats it states elsewhere:
- One LLM cannot simulate a truly *heterogeneous* workflow, because a KV cache cannot be shared between different models (Abstract, §1, §6).
- The heterogeneous pilot used auto-generated workflows that are "not perfectly optimized". Well-designed mixed-model workflows (e.g. sending easy tasks to a small model and hard ones to a strong model) could still help (§4.2.3).
- The equivalence proof only holds under its three conditions: deterministic tools, routing based only on visible history, and deterministic or shared-randomness decoding (Prop. 1).
- KV-cache costs for GPT-4o-mini are an *ideal simulation*, not measured (§4.1).
- Qwen-3 8B writes longer answers in multi-turn chats, which partly cancels the efficiency gain (§4.2.4).
- The context grows over many turns. They suggest optional summarisation ("compaction") to limit this and reduce interference (§3.2).

**Future work they suggest:**
- Train a single agent to run complex workflows end-to-end (§4.2.3, §6).
- Design heterogeneous workflows that mix models of different strengths and costs, where the gain from diversity outweighs the lost KV sharing (§1, §4.2.3, §6).

**Our own caveats:**
- **Their "single agent" is not our "single agent".** Here, one LLM runs the *same workflow*, so its token spend is similar or lower. It is not a single agent given the *same token budget* as the MAS. So it is only indirect evidence for our compute-matched 2x2.
- **No debate on code-repair tasks.** They never test debate or SWE-bench-style tasks. The coding tasks are short function-writing problems (HumanEval, MBPP).
- **Small gaps, few runs.** Most differences are 0.5–1.5 points with 3 runs, and there is no significance test. The Claude 3.5 Haiku rows show ±0.0, which suggests a single run.
- **Possible copy error in Table 1.** The MultiPersona row is identical to the CoT row on 5 of 6 columns. This looks like a copy error.
- Preprint; not peer-reviewed.

**Why it matters to us:**
- **Phase 1 (compute-matched 2x2):** This is a recent, direct argument that a same-model MAS may add little beyond what one agent with the same prompts could do. That is exactly why each debate arm needs a single-agent arm with the same budget. SWE-Debate's 5 agents are homogeneous (the same LLM), which is the case this paper covers.
- **Phase 2 (fallback: ColMAD with different backbones):** The paper argues that heterogeneity is the part a single agent *cannot* copy. That supports trying different backbone models if graph-grounded debate fails. Their own pilot, however, found no gain from mixing models.
- **Practical point:** we run on vLLM with one open-weights model, so prefix/KV caching can cut the cost of debate rounds. We must count tokens the same way in every arm, whether or not caching is on.

**Numbers worth quoting in the report:**
- Qwen-3 8B, HumanEval: AFlow as separate stateless calls 86.8% vs single-agent execution 90.5% (Table 4).
- GPT-4o-mini, HotpotQA cost: AFlow multi-agent $1.438 vs single-agent $0.530, with F1 72.1 vs 68.4 (Tables 1–2).
- OneFlow HumanEval: 91.6 (multi-agent) vs 92.1 (single-agent), and cost $0.026 vs $0.020 (Tables 1–2).
- Heterogeneous GPT-4o-mini + Haiku AFlow on DROP scores F1 85.5, below Haiku-only OneFlow at 87.5 (Table 3).

---

## 5. B — Method and results (read the key sections)

### B1 — Improving Factuality and Reasoning in Language Models through Multiagent Debate (Du, Li, Torralba, Tenenbaum, Mordatch; arXiv preprint v1, May 2023 — later ICML 2024)

**In one sentence:** Several copies of ChatGPT each answer a question, read each other's answers, and revise over a few rounds; this "multi-agent debate" beats a single model, self-reflection and majority voting on maths, chess and factual tasks.

**The problem:** LLMs make up facts (hallucinate) and make reasoning slips. Earlier fixes (chain-of-thought, self-reflection, self-consistency) all use one model instance. The authors ask whether letting several instances critique each other gives better answers (§1).

**How it works / what they did:**
1. Each of N agents (copies of the same model) answers alone.
2. Each agent sees the others' answers and gives an updated answer (Fig. 3). This repeats for several rounds, usually ending in one shared answer (§2.2).
3. Only black-box text access is needed (no logits). The same prompts are used for every task.
- Main setting: **3 agents, 2 rounds of debate**, gpt-3.5-turbo-0301, zero-shot (§3.1, App. A.2).

**How they tested it:**
- Reasoning (Table 1): Arithmetic (100 made-up expressions with six numbers), GSM8K (100 grade-school maths word problems), Chess move prediction (300 grandmaster games; score = Stockfish pawn advantage after the suggested move, higher is better).
- Factuality (Table 2): Biographies (a new dataset of 524 computer scientists; ChatGPT judges whether each true Wikipedia fact agrees with the generated biography), MMLU (100 multiple-choice exam questions), Chess move validity (100 BIG-Bench tasks: is the move legal?).
- Baselines: single agent; single agent + self-reflection (the model critiques its own answer); multi-agent majority vote over 3 answers (reasoning tasks only).
- Metric: accuracy (%), except chess optimality (pawn score).

**What they found:**
- Debate is best on every task. Arithmetic 67.0 → 81.8, GSM8K 77.0 → 85.0, chess ΔPS 91.4 → 122.9 (single agent → debate). Majority vote reaches only 69.0 / 81.0 / 102.2 (Table 1).
- Factuality: Biographies 66.0 → 73.8, MMLU 63.9 → 71.1, chess validity 29.3 → 45.2. Self-reflection *hurt* MMLU (57.7) (Table 2).
- Sometimes every agent starts wrong and the group still reaches the right answer, so debate is not just picking the majority (Figs. 4, 5).
- More agents and more rounds both help on arithmetic. Gains stop after about 4 rounds (Fig. 10).
- "Stubborn" prompts (agents told to trust their own answer more) make debates longer and final answers better. The authors describe the models as naturally "agreeable" (§2.2, Fig. 12).
- Mixed models: ChatGPT + Bard on 20 GSM8K problems solved 17, against 14 (ChatGPT alone) and 11 (Bard alone) (§3.3).
- Facts the agents disagree on tend to be dropped. Facts they all share are hard to shake (§3.2).

**Limitations and threats to validity (the authors' own, §5):**
- Costs more compute than other prompting methods (many generations plus debate rounds).
- In long debates, models struggle to read the whole debate and mostly look at the most recent answers.
- Debates settle on one answer, but it can be wrong. Models then confidently claim it is correct and agreed. The authors blame poor uncertainty expression.
- Biography metric: generated biographies can contain false facts that aren't in the ground-truth list, so the metric can't catch them (App. A.2; Fig. 27: "many facts remain incorrect").
- There is no separate threats-to-validity section.

**Future work they suggest:**
- Distil debate outputs back into the base model (self-improvement loop) (§1, §5).
- Use longer-context models or summarise early rounds to fix the long-debate problem (§5).
- Combine debate with methods that improve uncertainty expression (§5).
- Different persona prompts per agent (MMLU 71.1 → 74.2) and summarising other agents' answers (Fig. 13) as further gains (§3.3).
- "Ease of persuasion" as a confidence measure (§3.2).

**Our own caveats:**
- **No compute matching.** Debate (3 agents × several rounds) uses several times more calls than majority vote (3 answers) or a single agent. The gain may partly be extra tokens. This is exactly the gap our 2×2 targets.
- Small test sets (100 items for most tasks), one model version, and no stated number of runs. The ± values are not explained in the text.
- ChatGPT judges its own biographies, so the evaluator is the same model family as the system.
- The mixed-model result uses only 20 problems.
- Short-answer tasks only; no code or long context.

**Why it matters to us:**
- **Phase 1:** This is the root paper for SWE-Debate's debate idea. Its headline gain has no equal-token single-agent control, which is exactly what our compute-matched 2×2 tests. Its "converges confidently to a wrong answer" limitation maps onto our *selection* failure (the right chain is among the candidates but the debate picks another).
- **Phase 2:** "Agreeable" agents and the benefit of stubborn prompts show that debate quality depends on *why* agents change their minds. Graph-grounded debate makes agents change position only when a checkable graph fact says so. The ChatGPT+Bard result is early support for the ColMAD fallback (mixed backbones).
- The "only reads the latest answers" limitation matters for our long prompts (issue plus ~20 chains).

**Numbers worth quoting in the report:**
- GSM8K: single 77.0 → majority vote 81.0 → debate 85.0 (3 agents, 2 rounds; Table 1).
- Arithmetic: 67.0 → 81.8. MMLU: 63.9 → 71.1 (Tables 1–2).
- Gains flatten after about 4 rounds (§3.3, Fig. 10).
- ChatGPT+Bard debate: 17/20 vs 14/20 and 11/20 (§3.3).

---

### B2 — When Does Multi-Agent Collaboration Help? An Entropy Perspective (Zhao, Chen, Su; arXiv preprint 2602.04234v6, June 2026)

**In one sentence:** Across 5 small open-weights models, 6 benchmarks and 5 set-ups, a single agent beats every multi-agent set-up in 43.3% of cases, and whether multi-agent works is mostly decided by how uncertain the agents are in round 1.

**The problem:** People assume more agents means better answers, but single agents often match multi-agent systems (MAS). Earlier studies only compared accuracy, cost and latency, so they could not say *why* MAS fail. The authors look inside the agents using **entropy** (how spread out the model's next-token probabilities are; high entropy = unsure) (§1, §2).

**How it works / what they did:**
1. They build five set-ups from one base model, all with **R = 2 rounds** (App. B.2). *Single*: one agent refining its own answer (R calls). *Sequential*: planner → solver → critic → judger (4R calls). *Centralized*: 3 domain experts + orchestrator (4R). *Debate*: 3 agents, each sees all earlier answers, then majority vote (3R). *Hybrid*: centralized + peers see each other (4R).
2. They log token-level entropy for every agent and round. From these logs they build **245 features** at the token, agent, round and sample levels (§4.2).
3. They train the **Entropy Judger** (average of XGBoost + LightGBM classifiers) to predict whether a sample's answer is correct from those features. SHAP (a method that scores each feature's contribution to a prediction) shows which features matter (§4.3).
4. They run causal-discovery algorithms (PC/FCI, which infer cause-effect graphs from observational data) to test cause, not just correlation (§5.4). They also use the Judger to pick the best of k runs without labels (App. I.5).

**How they tested it:**
- Models: LLaMA-3.1-8B, LLaMA-3.2-3B, Qwen3-0.6B/4B/8B (14B only in appendices), temperature 0.6 (App. B.1).
- Benchmarks: GSM8K, MATH500, AIME24, AIME25 (maths), HumanEval (code; debate was excluded because majority voting doesn't work for code), MMLU. Agentic: GAIA (165 questions) and FinanceAgent (App. E).
- Metrics: accuracy. For the Judger: 5-fold cross-validated classification accuracy and best-of-k accuracy.

**What they found:**
- Single agent is best in **13/30 cases (43.3%)**, 6.28% above average MAS accuracy. It matches or beats at least one MAS set-up in 26/30 (§4.4, Fig. 1).
- Higher base-model entropy means lower MAS accuracy (Fig. 2).
- MAS failures come from agents disagreeing (e.g. Qwen: variance across agents ρ ≈ −0.92). MAS needs lower, more uniform entropy than a single agent to succeed (§4.4).
- **Peak entropy is always harmful.** Debate "depends critically on early consensus" (§5.2).
- **More rounds don't help:** going from R = 2 to R = 5 mostly hurt debate and hybrid. Entropy is flat after round 2 (§5.3, Fig. 5).
- Causal: base-model entropy (ATE ≈ −0.12), round-1 total entropy and maximum answer-token entropy (ATE ≈ −0.31) directly cause correctness. ATE (average treatment effect) = expected change in correctness when the feature goes up. 30–33% of round-1 disagreement's effect passes through round 2 (§5.4).
- Judger CV accuracy: 72.6% / 79.1% (LLaMA / Qwen) from MAS features alone (§5.5).
- Round 1 → 2: 89.5% of samples lose entropy, but only **6.2% genuinely improve**, while **83.4% are "possible anchoring"** (agents converge without getting more correct). Debate's mean accuracy change is −0.020 (App. K.3–K.4).

**Limitations and threats to validity (the authors' own, App. M):**
- Models are only up to 14B because of compute. 27–70B models may behave differently.
- Benchmark coverage: 6 reasoning benchmarks plus GAIA/FinanceAgent only. Web-browsing and multi-step environment tasks are untested.
- All agents share one base model (homogeneous). Mixed-model teams may behave differently.
- The causal claims come from observational data and algorithms, not controlled interventions. Why entropy falls without accuracy gains (83.4%) is "incompletely understood".
- Entropy is a predictive feature, not a universal uncertainty measure. Its calibration depends on model family and task (§4.4, App. J).
- The Judger is a selection tool, not an uncertainty-quantification method (App. I).
- The App. K split into role-assignment vs interaction effects is "attributional", not a proven causal split.

**Future work they suggest (App. M):**
- Test on broader agentic benchmarks (web browsing, multi-step environments).
- Study mixed-model teams: can agents with different entropy profiles cover for each other, and how should teams be composed?
- Stronger causal tests: message-ablation studies that separate *information content* from *social influence*, and counterfactual interventions that change entropy directly (e.g. via temperature).

**Our own caveats:**
- **Compute is not matched:** single = R calls, MAS = 3R–4R. Since MAS gets *more* compute and still often loses, this probably strengthens their point, but it is not an equal-budget test.
- The Judger uses stratified random 5-fold CV over samples (App. I.3). The same question can appear in training and test across set-ups and models, which could inflate accuracy. This is our concern; the authors don't discuss it.
- Majority vote collapses at k = 2 (e.g. GSM8K 0.895 → 0.293, Table 10) because of how ties are handled. That makes it a weak baseline for the Judger.
- Small inconsistency: the text says the Judger "marginally underperforms" Random on AIME25 "(0.223 vs. 0.222)", but those numbers favour the Judger. The abstract's "consistent improvements across all … tasks" also skips this exception.
- Single runs, small models; the only code task is HumanEval (not repository-level).

**Why it matters to us:**
- **Phase 1:** This is independent evidence that MAS often doesn't beat one agent, and that extra rounds mostly produce anchoring, not correction. That supports testing whether SWE-Debate's 2 rounds + discriminator add anything at localization level. Our vLLM open-weights backbone gives full logprobs, so we can cheaply log round-1 entropy and disagreement per issue and relate them to retrieval vs selection failures.
- **Phase 2:** Their suggested "information vs social influence" ablation is close to our graph-grounded debate: agents may change position only because of a checkable graph fact, not peer pressure. Their homogeneous-agent limitation matches our ColMAD fallback with mixed backbones.

**Numbers worth quoting in the report:**
- Single agent best in 13/30 model-dataset cases (43.3%) (§4.4).
- Round 1 → 2: genuine improvement 6.2% vs possible anchoring 83.4% of samples (App. K.4).
- Debate mean Δaccuracy after interaction: −0.020 (App. K.3).
- R = 5 does not beat R = 2; entropy flat after round 2 (§5.3, Fig. 5).
- Max answer-token entropy causal effect ATE_PS = −0.31 (§5.4).

---

### B3 — Multi-Agent Systems are Mixtures of Experts: Who Becomes an Influencer? (Bause, Niederle, Pawelczyk, Burkholz; ICML 2026 Workshop on Compositional Learning, arXiv 2605.25929v2)

**In one sentence:** Debate between LLM agents behaves like a "mixture of experts" that decides, question by question, whose opinion wins, and in practice the winner is mostly the *most confident* (and stubborn) agent, which is not always the most competent one.

**The problem:** Multi-agent systems (MAS) sometimes beat single agents or plain ensembles and sometimes don't. The authors ask what makes one agent more influential than others during deliberation, and when that helps accuracy (§1).

**How it works / what they did:**
1. **Model the debate with Friedkin-Johnsen (FJ) opinion dynamics** (§2, Eq. 1). FJ is a classic social-science model. Each round, an agent's belief (a probability over answer options) is a mix of three things: its original belief (weight γ, "stubbornness"), its previous belief (α), and its peers' beliefs (influence matrix W).
2. At equilibrium, the final answer is a **weighted average of the agents' initial beliefs** (Prop. 2.1). Fixed weights would make it just an ensemble. The fitted weights change per question, so the MAS acts as a **mixture of experts (MoE)**: a hidden "router" picks whose opinion counts for each input (Hypothesis 2.2, Fig. 1a).
3. **Theory** (Thm. 2.4, 2.5). An MoE-style MAS beats the best single agent only if *specialisation gain + local diversity > routing regret* (the loss from giving weight to the wrong agent). It beats a fixed ensemble only if the *routing gain > diversity lost*. Confidence-based routing helps only if confidence is well calibrated (confidence tracks correctness); overconfident wrong agents can erase the gain (§2.2).
4. **Experiments:** fit FJ parameters to real debates, then use regression on observable signals to explain which agent becomes most influential: confidence (1 − normalised entropy of its initial belief), confidence relative to the runner-up, alignment with the group, and role prompt.

**How they tested it:**
- Data: MMLU-Pro (300 questions), BBQ (300), CommonsenseQA (100) — all multiple choice (§3).
- Models: GPT-5.4 Mini, Qwen2.5-14B-Instruct, Qwen2.5-72B-Instruct (GPTQ-Int8); 3 seeds.
- Set-up: 5 agents, fully connected, 5 rounds. Agents state an explicit probability distribution over the options. Diversity comes from role / expert / communication-style prompts, or none ("neutral") (§3, App. E).
- Comparisons (Table 3): *Baseline* = argmax of the averaged initial beliefs (a plain ensemble); *FJ ensemble* = one fixed set of FJ weights for all questions; *MAS* = actual deliberation.
- Metrics: FJ fit (KL divergence and MSE between predicted and observed beliefs), accuracy, and R²/accuracy of the influence predictors.

**What they found:**
- FJ fits the debates well: KL 0.0470 ± 0.0034, MSE 0.00198 (Table 1).
- FJ weights vary a lot across questions, so routing is input-dependent (MoE) (Fig. 1a).
- Agents almost always reach **consensus**, even though FJ would only predict this with little stubbornness. Influence is concentrated in **a few agents**, and **the most stubborn agents become the most influential** (§3, Fig. 17b).
- **Confidence drives influence.** Relative confidence is a stronger predictor than absolute confidence. Random forests predict influence with test R² ≈ 0.7 and pick the most influential agent with ≈ 0.9 accuracy (§3, Fig. 5, Fig. 16).
- Competence is linked to influence, but more weakly (Fig. 18). Confidence–competence correlation per MAS is r = 0.65 ± 0.61, a very wide spread (Fig. 2).
- The role prompt alone changes influence (e.g. "teacher" vs "student"), suggesting that *perceived* confidence matters (Figs. 4, 5).
- MAS is often slightly better than both baselines, e.g. MMLU-Pro GPT-5.4 Mini neutral 0.804 → 0.820 (FJ ens.) → 0.826 (MAS). But gains are small and sometimes negative, especially on CSQA and with persona prompts (Table 3, App. B).
- Thm. 2.4 mostly holds per sample for GPT-5.4 Mini. Qwen-72B's MAS loses more often, but usually when the condition is not met (Figs. 20–21).

**Limitations and threats to validity (the authors' own):**
The paper has no dedicated limitations or threats-to-validity section. The limitations it states:
- Routing relies on imperfect competence signals. Miscalibrated confidence, uninformative behavioural confidence, or agreement that just reflects shared errors can amplify the wrong agents. High agreement is good only if it is independent corroboration; high confidence is good only if calibrated (§2 "Strengths and limitations"; §5).
- The theory does not rule out a stronger single model (e.g. distilled from the MAS, or self-consistency) doing as well (§2.1).
- Persona/communication-style prompts sometimes make MAS slightly *worse* than the baseline (App. B).
- The FJ solver failed to converge on <1% of samples (skipped). 4% had ill-conditioned fits and were excluded from the influence analyses (App. B).
- Confident agents are more stubborn, but that confidence is "not necessarily grounded in competence" (§3).

**Future work they suggest (§4, §5):**
- Build better router models that use all agents, not only the most confident one.
- Use graph neural networks (especially attention-based ones) as routers that generalise across communication topologies.
- Measure how much optimal routing would gain over the routing that emerges from debate (open question).
- Extend to open-ended generation and tool use.
- Mitigate overconfident agents and improve communication.

**Our own caveats:**
- **No compute-matched single-agent baseline.** The baseline is the same agents' round-0 average, while MAS adds 5 × 5 generations. Accuracy gains are small with overlapping error bars over 3 seeds.
- FJ is fitted per question with many free parameters (γ, α and a 5×5 W), so a good fit is partly expected.
- Beliefs are self-reported probabilities, whose calibration is itself uncertain.
- Only multiple-choice QA; no code.
- Workshop paper.
- Table 3's columns were scrambled in the text extraction; the numbers above come from our reconstruction, so check the PDF before quoting them.

**Why it matters to us:**
- **Phase 1:** SWE-Debate's vote over ~20 candidate chains is a multiple-choice problem, so this framework applies directly. Our "selection" failures are B3's **routing regret**: the right chain was among the options, but influence went to a confident wrong agent. We could log each agent's initial chain pick/confidence and who "wins".
- **Phase 2:** B3 says influence follows confidence and stubbornness, not evidence. Graph-grounded debate replaces that with a checkable signal (graph facts), which is exactly a better router. Their Theorem 2.4 also says gains need *local diversity*. 5 copies of one model may lack it, which supports the ColMAD fallback with different backbones.

**Numbers worth quoting in the report:**
- FJ fit: KL 0.0470 ± 0.0034, MSE 0.00198 ± 0.00026 (Table 1).
- Predicting the most influential agent: ≈ 0.9 accuracy; influence regression R² ≈ 0.7 (§3).
- Confidence vs competence: r = 0.65 ± 0.61 per MAS (Fig. 2, GPT-5.4 Mini, MMLU-Pro).
- Stubborn agents become the most influential (§3, Fig. 17b).

---

### B4 — Why Do Multi-Agent LLM Systems Fail? (NeurIPS 2025, Datasets & Benchmarks Track)

**In one sentence:** The authors read over 1,600 run logs from 7 multi-agent LLM systems and sorted the ways they fail into a taxonomy called MAST (14 failure modes in 3 groups). They then show that many failures come from how the system is designed, not only from the model.

**The problem:** Multi-agent systems (MAS, several LLM "agents" talking to each other) often beat a single agent or simple best-of-N sampling (draw N answers, keep the best) by only a small margin. Before this paper there was no shared, evidence-based vocabulary for *why* they fail. Without one, fixes are guesswork.

**How it works / what they did:**
1. They collected 150 traces (full conversation logs of a run, averaging over 15,000 lines each) from 5 MAS. Six experts labelled them using Grounded Theory (a qualitative method where categories come out of the data, not from a list decided beforehand) (§3.1).
2. Three annotators labelled batches of 5 traces each and settled their disagreements, over 3 rounds, until agreement reached Cohen's κ = 0.88 (κ = agreement corrected for chance; 1 = perfect) (§3.2).
3. The result is MAST. **FC1 System design** covers disobeying the task or role, step repetition, lost history, and not knowing when to stop. **FC2 Inter-agent misalignment** covers conversation reset, not asking for clarification, derailment, withholding information, ignoring another agent's input, and reasoning–action mismatch. **FC3 Task verification** covers premature termination, no or incomplete verification, and incorrect verification (Figure 1, App. A).
4. They built an "LLM annotator": OpenAI o1 is given a trace, the MAST definitions and few-shot examples, and labels the failures (§3.3). They used it to label 1,642 traces (MAST-Data, Table 1).
5. They tried simple fixes (better prompts, a new agent topology) on AG2 and ChatDev (App. H).

**How they tested it:**
- **Systems:** ChatDev, MetaGPT, HyperAgent (on SWE-Bench Lite), AppWorld, AG2/MathChat, Magentic-One, OpenManus.
- **Models:** GPT-4/4o/4o-mini, Claude-3.7-Sonnet, Qwen2.5-Coder-32B, CodeLlama-7B.
- **Benchmarks:** ProgramDev (30 coding tasks; v2 has 100), GSM-Plus, OlympiadBench, MMLU, GAIA.
- **Annotator checks:** accuracy, precision/recall/F1 and κ against the human labels (Table 2). They also checked it on 2 unseen MAS and 2 unseen benchmarks.

**What they found:**
- Failure rates on the 7 MAS ranged from 41% to 86.7% (§1, Fig. 5). HyperAgent solved only 25.3% of SWE-Bench Lite.
- Share of failures by category over 1,642 traces: FC1 44.2%, FC2 32.3%, FC3 23.5% (Fig. 1). The biggest single modes were step repetition (15.7%), reasoning–action mismatch (13.2%) and unaware of termination (12.4%) (§4).
- The LLM annotator with few-shot examples reached 94% accuracy and κ = 0.77. Without examples it reached κ = 0.58 (Table 2). On the unseen systems, human agreement was κ = 0.79 (§3.4).
- Having a verifier helps but is "not a silver bullet". Many verifiers only check shallow things, such as whether the code compiles (Insight 3, §4).
- Tested fixes (Table 5):
  - ChatDev on ProgramDev-v0: 25.0% → 34.4% with better prompts, and → 40.6% with a cyclic topology (+15.6).
  - AG2 with GPT-4: 84.75 → 89.75 with better prompts. The topology gain was not significant (Wilcoxon p = 0.4).
  - AG2 with GPT-4o: both fixes significant (p = 0.03).
  - The authors say these gains are real but not large (App. H).
- Some modes almost only appear in failed runs, e.g. 1.5 and 2.4. Verification failures (3.2, 3.3) also show up often in *successful* runs (App. J.1, Table 7).
- Harder benchmarks produce more failures per trace (Table 8).
- The LLM annotator costs about $1.8 per trace on average (App. K).

**Limitations and threats to validity (the authors' own):**
The paper has **no limitations or threats-to-validity section**. The caveats they state elsewhere are:
- MAST is not claimed to be exhaustive. It is "a foundational first step" and may not cover every failure pattern (§1, §4).
- Some failures come from basic LLM limits, such as hallucination. MAST deliberately focuses on design, coordination and verification (§4).
- Modes with similar symptoms are moderately correlated (up to 0.63). This may lead automated judges to confuse root causes (App. E).
- Closed-source systems (e.g. Manus) could not be included because their traces are not available (App. B.3).
- The per-system failure profiles in Fig. 4 and Fig. 5 use different benchmarks. They are not meant as performance comparisons (Fig. 4 and 5 captions).
- The tactical fixes gave inconsistent results that depend on the LLM (App. G.1, H.1).

**Future work they suggest:**
The paper gives no dedicated list. Its open directions (§4, §5.3, App. G.2, Table 4) are:
- Stronger multi-level verification, including domain-specific checks, unit-test generation and external knowledge.
- Standardised or structured communication protocols between agents.
- Training for "social reasoning" / theory of mind (modelling what other agents need to know), e.g. with RL methods like MAPPO or Optima.
- Confidence thresholds, so agents act only when confident and gather more information otherwise.
- Better memory and state management for multiple agents.
- Better open-source models for MAS work (App. I).

**Our own caveats:**
- The percentages disagree across the paper. Figure 2 shows 37.17 / 31.41 / 31.41, Figure 4 shows 41.8 / 36.9 / 21.3 (210 traces), and Figure 1 shows 44.2 / 32.3 / 23.5. Quote Figure 1 and say which figure you used.
- Almost all of MAST-Data was labelled by o1, not humans. With recall 0.77, the annotator misses roughly a quarter of the failures that humans find.
- The ChatDev results in Table 5 are single numbers with no variance. The AG2 results used 6 repetitions.
- Table 7 appears to rest on very few traces. The percentages move in steps of 5% and 8.3%, which suggests about 20 and 12 traces per row.
- There is no compute matching when they compare interventions.

**Why it matters to us:**
- **Phase 1:** MAST gives us a ready-made vocabulary for labelling SWE-Debate debate transcripts. For example, when the debate picks the wrong chain even though the right file was among the candidates (a *selection* failure), we can tag it as FM-2.5 (ignored input), 2.6 (reasoning–action mismatch) or 3.3 (incorrect verification by the discriminator).
- **Phase 2:** Insight 3 says verification should use external knowledge and more than one level of checks. That directly supports graph-grounded debate, where claims are checked against the dependency graph. Insight 1 (design matters when the model is held fixed) supports changing the debate protocol rather than the model.
- **Our own annotation:** if we build our own annotator, we must check it against human labels as they did. We cannot assume it works.

**Numbers worth quoting in the report:**
- 1,642 traces from 7 MAS; 14 modes in 3 categories; human κ = 0.88 (Abstract, §3.2).
- MAS failure rates of 41%–86.7%; HyperAgent solves 25.3% of SWE-Bench Lite (Fig. 5).
- FC1 44.2% / FC2 32.3% / FC3 23.5% of failures (Fig. 1).
- LLM annotator (o1, few-shot): accuracy 0.94, κ = 0.77 (Table 2).
- ChatDev ProgramDev-v0: 25.0 → 40.6 with the topology change, same model (Table 5).

---

### B5 — Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies (arXiv preprint 2406.06461, 2024; Amazon / AWS AI Labs)

**In one sentence:** When a plain baseline gets the same token budget, "chain-of-thought + self-consistency" matches or beats fancier strategies such as multi-agent debate and Reflexion. Much of their reported gain comes from spending more compute, not from a cleverer algorithm.

**The problem:** New reasoning strategies are usually compared on accuracy alone. But some of them, like debate, tree search and reflection, use many more LLM calls and tokens than their baselines. So a "better" method may simply be one that spent more.

**How it works / what they did:**
1. They defined three budget measures (§3.1): number of queries (LLM calls), total tokens (input + output), and dollar cost. They argue tokens is the most complete measure, because one query can be very long (App. D.3.2).
2. They plotted accuracy against budget for each strategy. The baseline is **CoT SC**: sample N chain-of-thought answers independently and take a majority vote.
3. They gave all strategies the same cap: at most 20 queries or 10k tokens per question. Multi-Agent Debate (MAD, Liang et al.) used 6 agents × 3 rounds = 18 queries. Reflexion used up to 10 tries, which is 19 queries (§4.1).
4. They analysed *why* SC wins. They measured answer diversity (entropy) per debate round, and built a binomial/Dirichlet model of majority voting (§5.1, App. C).
5. They ran ablations on the evaluator ("self-evaluation") inside Tree-of-Thoughts and Reflexion, and proposed SC² (voting weighted by the model's own yes/no confidence) (§5.2–5.4).

**How they tested it:**
- **Data:** GSM8K, MATH, TheoremQA (442-question math subset), CommonsenseQA, HotpotQA, and Game of 24. They used 100 random test questions per dataset (App. A.1).
- **Models:** GPT-3.5 (0301 and 0125), GPT-4-0613, Mistral-7B, Mixtral-8x7B, and LLaMA-2-70B. Temperature was 1 (App. A.2, G).
- **Metric:** accuracy at a given number of queries or tokens.

**What they found:**
- At equal budget, SC beats MAD and Reflexion on every dataset except HotpotQA, where it only ties (§4.1, Fig. 3). The trend holds for all the extra models (App. G.1).
- MAD and Reflexion can get *worse* as budget grows. SC improves smoothly (Abstract, §5.1).
- MAD and SC are the same method for the first 6 queries. After that, MAD's gain flattens and its token cost per round climbs, because every agent reads the whole history (§5.1).
- **Why debate stalls:** answer entropy (diversity) falls every debate round, so agents "tunnel" on one answer, including wrong ones. SC's samples are independent, so diversity does not collapse (Fig. 6, §5.1.1).
- **Why voting works:** if the model is right more than 50% of the time on a question, majority vote tends to 100% correct as N grows. If it is right less than 50%, the vote tends to 0% (App. C, Eq. 3). Fig. 9 confirms that SC hurts on questions where the correct answer is not the majority.
- Plan-and-Solve, Least-to-Most and Progressive Hints also gain mainly from budget (§4.2, Fig. 4).
- Tree-of-Thoughts beats SC on Game of 24 with GPT-4, even under budget. It loses badly with GPT-3.5, so "a strong model is needed" (§4.3, Fig. 5).
- A cheaper evaluator mostly works. ToT with a GPT-3.5 evaluator cost $33.53 for 72% accuracy, versus $159.87 for 76% with a GPT-4 evaluator. A random evaluator gets close to 0 (§5.2, Table 3).
- LLM self-evaluation is weak on wrong answers. GPT-4 recognised only 15.6% of wrong answers on GSM8K and 2.9% on HotpotQA (Table 1). The harder the question, the noisier the self-evaluation: correlation 0.347, p = 0.00026 (App. D.2).
- Reflexion with an oracle (told the right answer) beats SC. Reflexion with a GPT-4 evaluator does not (Fig. 10).
- SC² beats SC on GSM8K and MATH but falls behind on the other three datasets (Fig. 11).

**Limitations and threats to validity (the authors' own):**
- §7 is the only limitation stated. Because of money and time, they tested only some representative strategies and tasks. A more thorough evaluation "might reveal additional nuances".
- In passing: LLaMA-2-70B's context limit of about 4k tokens meant MAD and Reflexion could not be run to the same budget as SC (App. G.1).

**Future work they suggest:**
The paper has no future-work section. The directions it states:
- More research on using the budget efficiently, and on better reasoning strategies (§1).
- Better LLM evaluators: "LLMs as a better evaluator could unlock significantly more performance" (§5.3–5.4).

**Our own caveats:**
- Only 100 questions per dataset, and the main curves show no error bars or seeds. Small gaps may be noise.
- The tasks have short answers that are easy to vote on. They are not software engineering tasks.
- The models are older (2023 generation).
- The debate tested is one variant (Liang et al.). Other debate designs may behave differently.
- Token counts assume no prompt caching. The authors note that caching changes the cost of self-evaluation (App. D.3).

**Why it matters to us:**
- **Phase 1:** this is the key evidence for our compute-matched 2×2. A multi-agent arm must be compared with a single-agent arm that gets the same tokens. The natural single-agent arm is "sample N times, then vote on a chain", i.e. SC.
- **Budget measure:** use tokens, not queries, as the budget unit.
- **Diversity collapse:** this predicts that 5 copies of the same model will converge on one chain. That supports the ColMAD fallback with different backbone models.
- **Phase 2:** weak self-evaluation supports settling disagreements against an *external* check (the graph) rather than against the model's own opinion.

**Numbers worth quoting in the report:**
- Budget cap of 20 queries or 10k tokens; MAD = 6 agents × 3 rounds = 18 queries (§4.1).
- At equal budget, CoT SC beats MAD and Reflexion on 4 of 5 datasets and ties on HotpotQA (§4.1, Fig. 3).
- Debate answer entropy falls every round (Fig. 6).
- GPT-4 flags only 15.6% (GSM8K) and 2.9% (HotpotQA) of its wrong answers (Table 1).
- ToT: $33.53 / 72% with a GPT-3.5 evaluator vs $159.87 / 76% with a GPT-4 evaluator (§5.2).

---

### B6 — More Agents Is All You Need (Transactions on Machine Learning Research, 10/2024)

**In one sentence:** Sampling the same LLM many times and taking a majority vote ("Agent Forest") improves accuracy steadily as the number of samples grows. With enough samples, a small model can beat a larger one.

**The problem:** Earlier work, such as LLM-Debate and CoT self-consistency, hinted that adding more agents helps. Nobody had studied that scaling on its own. The question: does accuracy generally rise just by adding more raw agents, without any clever collaboration?

**How it works / what they did:**
1. **Sampling:** send the same query N times, either to a plain LLM or to an existing method such as CoT, Debate or Reflection (§3, Alg. 1).
2. **Voting:** pick the sample most similar to all the others. For multiple-choice and math answers, similarity means identical answers (i.e. majority vote). For code, it is BLEU score (a text-overlap measure between pairs of answers) (§3, App. A.4).
3. They scaled the ensemble up to 40 samples and averaged over 10 runs. Debate was capped at 10 samples because of its communication cost (§4).
4. They built a synthetic maths task that separates three kinds of difficulty: how hard each step is (I), the number of steps (S), and the prior chance of guessing the right answer (1/K). They varied each one separately (§6.1).

**How they tested it:**
- **Data:** GSM8K, MATH, MMLU, Chess state tracking, and HumanEval (code).
- **Models:** Llama2-Chat 13B and 70B, GPT-3.5-Turbo, and GPT-4 (single-sample reference only).
- **Methods combined with voting:** CoT, zero-shot CoT, Solo Performance Prompting (SPP), LLM-Debate and Reflection.
- **Metric:** accuracy. Significance was checked with one-way ANOVA across ensemble sizes (App. B.2).

**What they found:**
- Accuracy rises with ensemble size on every task and model (Fig. 3, Table 2). Gains: GSM8K +12–24 points, MATH +6–10, Chess +1–4, MMLU +5–11, HumanEval +4–9 (§5.1). All ANOVA p-values are below 0.05 (Table 7).
- Llama2-13B with 40 votes scores 0.59 on GSM8K. That beats a single Llama2-70B at 0.54 (Table 2).
- Adding voting on top of other methods helps too: +10–21 points on GSM8K, +1–15 on MATH (§5.2, Table 3).
- **Exception:** Debate + voting failed on HumanEval with both Llama models (0 → 0). The authors blame "noise" from agents referencing each other's answers, which broke the code logic (§5.2).
- Plain voting has the best average rank (2.5) among all the combined methods (Table 4).
- Voting helps more on hard tasks and weak models. The relative gain is 200% for Llama2-13B on MATH and 16% for GPT-3.5 on GSM8K (Table 6).
- The synthetic task (GPT-3.5) gave three properties:
  - Gains rise and then fall as each step gets harder. They peak at I = 100–200 and taper at I = 400, where the task exceeds the model's ability (§6.2).
  - Gains grow with the number of steps (§6.3).
  - Accuracy rises with the prior probability of the correct answer (§6.4).
- Two derived variants:
  - Step-wise voting (vote at each step) gives 15–42% gains (§6.3).
  - Hierarchical voting (solve a coarse version first, then the fine one) raises accuracy from 21% to 31%. Using GPT-3.5 for the coarse step and GPT-4 for the fine step gives 35% → 47% (§6.4, Fig. 7).
- Token cost grows in proportion to the number of agents (§5.5).

**Limitations and threats to validity (the authors' own):**
The paper has no limitations section. It notes these issues:
- Cost rises with more agents. This is common to all multi-call methods (§7).
- Current benchmarks focus narrowly on accuracy, which encourages costly agents (§7, citing Kapoor et al.).
- There is a lack of proper holdout sets and standard evaluation practice (§7).
- Under extreme difficulty, the task exceeds the model's reasoning ability and voting gives diminishing returns (§6.2).
- Debate combined with voting can add noise and hurt code generation (§5.2).

**Future work they suggest:**
- Optimise the sampling phase to cut cost, since the input is the same for every agent (§7).
- Address cost-aware evaluation and standardisation so agents become practical. The authors "leave it as a future work to optimize" (§7).

**Our own caveats:**
- Table 3 compares 40-sample voting against *single runs* of CoT, Debate and so on, so it is not compute-matched. "More agents" partly just means "more tokens" (compare B5).
- The standalone Debate score of 0 on HumanEval with the Llama models looks like an implementation or format problem, not a real result.
- BLEU voting picks the most "typical" code, not code that has been checked to be correct.
- The synthetic analysis used only GPT-3.5. §6.4 contains a typo ("constant values for I and K").
- The title overclaims. The gains depend on the model being right more often than chance.

**Why it matters to us:**
- **Phase 1:** Agent Forest is exactly the single-agent baseline for our 2×2: sample one model N times and vote on a candidate chain, at the same token budget as SWE-Debate's 5 agents. SWE-Debate's 5-agent vote is already largely an Agent Forest, so any benefit must come from the *debate* rounds on top of it.
- The finding that debate adds noise supports testing whether the debate rounds help at all.
- **Phase 2:** the "prior probability" property matters. Picking 1 of ~20 chains has a low prior. The hierarchical idea (choose the file first, then the function) is a cheap extra we could note.

**Numbers worth quoting in the report:**
- Llama2-13B with 40 votes: 0.59 on GSM8K vs 0.54 for a single Llama2-70B (Table 2).
- GSM8K gains of +12 to +24 points from voting alone (§5.1).
- Debate + voting fails on HumanEval with the Llama2 models (§5.2, Table 3).
- Relative gain is 200% (Llama2-13B, MATH) vs 16% (GPT-3.5, GSM8K) (Table 6).

---

### B7 — Agentless: Demystifying LLM-based Software Engineering Agents (arXiv 2407.01489 v2, Oct 2024)

**In one sentence:** A fixed pipeline (localize → repair → validate) with no autonomous agent beats every open-source SWE-bench Lite agent of its time, cheaply.

**The problem:** Most SWE-bench systems are "agents" (the LLM chooses its own next action and tools, for 30–40 turns). The authors say this causes hard tool design, little control over decisions, and weak self-reflection, so errors snowball (§1). Do we need agents at all?

**How it works** (§3, Fig. 1):
1. **Files:** the LLM ranks suspicious files from a `tree`-style repo listing; this is merged with **embedding retrieval** (issue and code chunks turned into vectors, most similar chunks picked).
2. **Elements:** the LLM sees a **skeleton** of each file (class/function headers only) and picks relevant classes/functions.
3. **Edit lines:** from those elements' full code, the LLM names exact edit locations; sampled 4 times.
4. **Repair:** 10 Search/Replace patches per location set → 40 patches.
5. **Validate:** LLM-written reproduction tests + existing regression tests filter patches; then **majority vote** over normalised patches.

**How they tested it** (§4): SWE-bench Lite (300 Python GitHub issues), plus SWE-bench Verified (500) and their filtered Lite-S (249). GPT-4o. 26 agent baselines (numbers taken from leaderboards) + a BM25 RAG baseline. Metrics: **% Resolved** (hidden tests pass), cost, tokens, **% Correct Location** (submitted patch edits all the developer patch's files / functions / lines).

**What they found:**
- 96/300 = 32.00% resolved, $0.70 per issue (Table 1). Final patch hits the right file 69.7%, function 52.0%, line 35.3%.
- Localization (Table 2, "Contains GT" = right location still among candidates): files by prompting 78.67%, by embedding 70.33%, combined 81.67%. Skeletons beat full files (58.33% vs 53.67%). Skipping the element step hurts (47.00% vs 50.67%).
- Repair (§5.2.2): if any of the 40 samples counted, 126 issues (42.0%) are solvable; selection keeps 96.
- Selection (Table 4): vote only 77 → + regression tests 81 → + reproduction tests 96.
- Benchmark audit (§6.1): 4.3% of issues contain the exact patch, 5.0% mislead, 10.0% lack information; about half name the file to edit. On Lite-S Agentless scores 33.73%, rank unchanged (Table 5).
- With **no location hint** in the issue, closed-source agents beat Agentless (Fig. 9c).
- SWE-bench Verified: 38.80%, best among GPT-4o systems (Table 6).

**Limitations and threats to validity (the authors' own):**
- *Internal (§7):* GPT-4o may have seen the developer patches during training (data leakage). They cannot check a closed model. Fully fixing this would need retraining.
- *External (§7):* results may not generalise beyond SWE-bench Lite. OpenAI's independent runs give partial support.
- Elsewhere in the text: most closed-source baselines publish no trajectories, so their results cannot be verified (§4). Matching the ground-truth location is only approximate, because a bug can be fixed elsewhere (§5.1.2). Only 94 of 213 bug-reproducing tests also pass the real fix, because issues often lack detail (§5.1.3). Reproduction tests add cost (§5.2.3). The method is weaker when the issue gives no location clue (§6.2).

**Future work they suggest:** test on other benchmarks (§7). Build better patch re-ranking/selection (§5.2.2). Handle issues without location clues (§6.2).

**Our own caveats:** one run per setting, with no variance reported. Baselines use different models and budgets, so the comparison is not compute-matched. Text says StarShip's file accuracy is 90.0%, but Table 1 says 90.7%. "Correct Location" is scored on the final patch, so localization and repair quality are mixed together.

**Why it matters to us:**
- **Phase 1:** Agentless already shows the retrieval-vs-selection gap. The right file is among the candidates 81.67% of the time (Table 2), but the final patch edits it only 69.7% of the time (Table 1). Its "Contains GT" metric is a template for our retrieval and reachability measure. It is also the standard single-agent localizer to compare our arms against.
- **Phase 2:** 42.0% (any sample) vs 32.00% (selected) shows that selection is a bottleneck. Selection is exactly where the debate operates.
- **Phase 3:** their leakage threat supports our use of post-cutoff SWE-bench-Live. The finding that about half of issues name the file means we should report results split by location-hint type.

**Numbers worth quoting in the report:**
- 32.00% resolved at $0.70/issue, GPT-4o, SWE-bench Lite (Table 1).
- File-level candidates contain ground truth: 78.67% / 70.33% / 81.67% (prompt / embedding / combined) (Table 2).
- 42.0% solvable across samples vs 32.00% after selection (§5.2.2).
- 4.3% exact patch, 5.0% misleading, 10.0% insufficient-info issues in Lite (§6.1).

---

### B8 — SWE-Search: Enhancing Software Agents with Monte Carlo Tree Search and Iterative Refinement (ICLR 2025)

**In one sentence:** SWE-Search adds tree search, an LLM "value" judge that writes feedback, and a final multi-agent debate on top of the Moatless agent. It resolves 23% more SWE-bench Lite issues (relative) across five models.

**The problem:** Most software agents work in a straight line. Once they go down a bad path, they cannot back up and try something else (§1). The authors want agents that explore alternatives, learn from feedback and backtrack, the way engineers do.

**How it works** (§3, Fig. 1):
1. **Action Agent** (built on moatless-tools): searches, plans and edits code. It can run existing tests and write new ones, but it never sees the hidden fail-to-pass tests. States are git commits, so it can revert.
2. **MCTS (Monte Carlo Tree Search):** each node is a state and each edge is an action. The next node to expand is chosen by a modified UCT score (a formula that trades off "known good" against "under-explored"). It adds a shallow-depth bonus and a deep-node penalty (Eq. 3).
3. **Value Agent:** an LLM scores each state from −100 to 100 and writes an explanation. When the parent node is expanded again, that explanation is fed back as "hindsight feedback".
4. **Discriminator Agent:** up to 5 final candidate patches go into a multi-agent debate (5 agents, 3 rounds, temperature 1.0; Table 2), and a concluding prompt picks one (App. L).

**How they tested it** (§4): SWE-bench Lite (300 issues). Five models: GPT-4o, GPT-4o-mini, Qwen2.5-72B-Instruct, DeepSeek-V2.5, Llama-3.1-70B-Instruct. Baseline: Moatless-Adapted, the same agent without search. Search budget: at most 100 iterations and 3 expansions per node (§4; Table 2 lists a default of 5). Metrics: **Pass@1 / resolve rate** (% of issues fixed by the one submitted patch) and **Pass@5** (fixed by any of 5 candidates).

**What they found:**
- Resolve rate went from 25.7→31.0 on GPT-4o, 13.0→17.0 on 4o-mini, 18.0→24.7 on Qwen, 16.3→21.0 on DeepSeek and 13.6→17.7 on Llama. The mean relative gain is +23% (Table 1).
- The more flexible transitions alone gave only 24.3→25.7, because the agent can get stuck in loops (§4.1.2).
- More search iterations steadily resolve more issues (Fig. 4b). Qwen-72B with search (24.7) beats GPT-4o on the original Moatless-v0.0.2 (24.3) (§4.1.1).
- Picking the correct solution when one exists: the value function alone manages 73%, the debate discriminator 84% (§3.5, Fig. 5a). The discriminator is better for every model except GPT-4o-mini.
- Different models solve different issues. 33 issues were solved by other models but not by GPT-4o (Fig. 5b).
- **Cost (App. I, Table 3):** GPT-4o costs $576.00 with search vs $40.86 without (about 14×). Other models cost about 5×.
- **Compute-matched check (App. J, Table 4):** SWE-Search Pass@5 vs 5 separate baseline runs: 4o-mini 22.3 vs 17.0, Qwen 25.7 vs 22.3, DeepSeek 23.3 vs 22.0, Llama 22.3 vs 21.7. GPT-4o was skipped because of cost.

**Limitations and threats to validity (the authors' own):** The paper has no limitations or threats-to-validity section. Scattered admissions:
- The value function sometimes misreads what an action is for and undervalues good steps. State-specific prompts were added to fix this (§4.2).
- They used conservative search settings (100 iterations) to keep 300 instances feasible. Normal MCTS runs thousands of iterations (§4.2).
- Better ways of picking the correct final solution are still needed (§4.2).
- Search costs much more (App. I).

**Future work they suggest** (§5): (a) study how search agents scale with compute. (b) apply search to more complex use cases, such as finding vulnerabilities or generating large codebases. Also (§4.2): improve final solution identification.

**Our own caveats:**
- Only one run per model, and no variance is reported, even though they cite Brown et al. showing that repeated runs vary a lot (§2).
- The main +23% is **not** compute-matched. The compute-matched Pass@5 gaps are small for DeepSeek (+1.3) and Llama (+0.6).
- The 73%→84% debate gain is compared only with the value function. It is never compared with a same-cost baseline such as majority voting.
- Numbers disagree: Llama Pass@1 is 17.7 in Table 1 and Table 4 but 21.0 in the Fig. 3 table. Expansions per node are 3 in the text but 5 in Table 2.

**Why it matters to us:**
- This is the lineage of SWE-Debate's MCTS patch stage (which we ignore) and of its debate-based discriminator. It shows debate used for *selection*, which is exactly the step we isolate.
- **Phase 1:** their gain shrinks once compute is matched (App. J). That supports running our compute-matched 2x2.
- **Phase 2:** 33 issues were solved only by non-GPT-4o models (Fig. 5b). This supports the ColMAD fallback of using different backbone models.

**Numbers worth quoting in the report:**
- Mean +23% relative resolve-rate gain across 5 models; GPT-4o 25.7→31.0 (Table 1).
- Debate discriminator picks the correct solution 84% of the time vs 73% for the value function (§3.5).
- Compute-matched Pass@5: DeepSeek 23.3 vs 22.0, Llama 22.3 vs 21.7 (App. J, Table 4).
- GPT-4o cost $576.00 vs $40.86 (App. I, Table 3).

---

### B9 — Large Language Models Cannot Self-Correct Reasoning Yet (ICLR 2024)

**In one sentence:** Without outside feedback, LLMs asked to "review and fix" their own reasoning usually get *worse*. Multi-agent debate does no better than simple majority voting once you give both the same number of LLM calls.

**The problem:** Many papers report that LLMs improve by critiquing themselves. The authors ask why a model that could fix its answer did not give the right answer in the first place (§1). They test **intrinsic self-correction**, meaning the model corrects itself using only its own judgement, with no ground-truth labels, tools or humans (§2).

**What they did:**
1. **Oracle vs intrinsic (§3):** they re-ran the self-correction setup of RCI and Reflexion in 3 steps: answer, critique, re-answer. They compared two versions: stopping when the *true label* says the answer is correct (oracle), and letting the model decide for itself.
2. **Debate vs self-consistency (§4):** they replicated Du et al.'s multi-agent debate (3 agents, 2 rounds) on the full GSM8K. They compared it with **self-consistency** (sample N answers and take the majority vote) at the *same number of responses*.
3. **Prompt fairness (§5):** they re-tested Self-Refine's constrained-generation task. This time the initial prompt also stated the requirement ("include *ALL* concepts"), which had previously appeared only in the feedback prompt.

**How they tested it:** GSM8K (1,319 grade-school maths problems), CommonSenseQA (1,221 multiple-choice questions), HotpotQA (100 multi-hop questions, closed-book, exact match) and CommonGen-Hard (metric: concept coverage). Models: GPT-3.5-Turbo, GPT-4, GPT-4-Turbo and Llama-2-70b-chat. Non-GPT-3.5 runs use 200 random questions per dataset. At most 2 self-correction rounds were run. The main metric is accuracy.

**What they found:**
- **With oracle labels it looks great:** GPT-3.5 goes from 75.9→84.3 on GSM8K and 75.8→89.7 on CommonSenseQA (Table 2). But oracle labels are not available in real use.
- **Intrinsic self-correction hurts every model on every benchmark** (Tables 3–4). After 2 rounds:
  - GPT-3.5: CommonSenseQA 75.8→41.8.
  - GPT-4: GSM8K 95.5→89.0, HotpotQA 49.0→43.0.
  - Llama-2: GSM8K 62.0→36.5.
- Changing the feedback prompt does not help (Tables 5–6).
- **Why:** GPT-3.5 keeps its GSM8K answer 74.7% of the time. When it does change an answer, it more often turns a correct answer wrong than a wrong answer correct (§3.3, Fig. 1). The model cannot judge whether its own reasoning is correct.
- **Debate vs voting (Table 7, GSM8K, gpt-3.5-turbo-0301):**
  - Standard prompting: 76.7.
  - With 6 responses: debate 83.2 vs self-consistency 85.3.
  - With 9 responses: debate 83.0 vs self-consistency 88.2.
  - The authors conclude that debate's gain comes from *consistency across samples*, not from critique (§4).
- **Prompting (Table 8):** a better initial prompt alone scores 81.8. Self-Refine's self-corrected result scores 67.0. Adding self-correction on top of the better prompt *lowers* the score to 75.1.

**Limitations and threats to validity (the authors' own, §7):**
- They study reasoning only. Self-correction may still help in other areas, such as changing style or improving safety, where LLMs *can* judge their own outputs.
- They note that earlier work already found self-correction weakens without external feedback and can be misled by bad feedback. Their contribution is to clear up confusion in the literature, not to make an entirely new claim.
- HotpotQA was left out of the answer-change analysis because its sample of 100 is too small (footnote, §3.3).
- They used subsets of 200 questions to save cost (§3.1).

**Future work they suggest (§6–7):**
- Use real external feedback where it exists, such as code execution or unit tests, tools, trained verifiers, or humans. Build ways for LLMs to learn from such feedback.
- Always compare self-correction with baselines at the same inference cost, including strong multi-sample baselines like self-consistency, and report a cost analysis.
- Develop models (for example, through alignment) that are more likely to decode the best answer the first time.
- Put equal effort into the initial prompt and the feedback prompt.
- Look for methods that genuinely improve reasoning.

**Our own caveats:**
- The tasks have short answers (maths, multiple choice), not code or localization.
- The debate test used one model, one dataset and one debate design.
- Different models used different temperatures (1 vs 0), and each setting was run once with no variance reported.

**Why it matters to us:**
- **Phase 1:** this is the core justification for our compute-matched 2x2. Debate must be compared with a single-agent arm at the same budget, such as self-consistency or voting over chains. Otherwise any gain may simply come from "more samples". SWE-Debate's −4.2 ablation removed the debate's tokens too, which is exactly the flaw this paper describes.
- **Phase 2:** the result that debate does not beat voting without outside feedback motivates graph-grounded debate. Checkable graph facts act as the *external feedback* that the authors say is needed.

**Numbers worth quoting in the report:**
- GSM8K with 9 responses: debate 83.0 vs self-consistency 88.2 (Table 7).
- GPT-3.5 on CommonSenseQA: 75.8 → 41.8 after 2 rounds of intrinsic self-correction (Table 3).
- Llama-2 on GSM8K: 62.0 → 36.5 (Table 4).
- Oracle-label "gains" (GPT-3.5 on GSM8K, 75.9 → 84.3) disappear without labels (Tables 2–3).

---

### B10 — Advances and Frontiers of LLM-based Issue Resolution in Software Engineering: A Comprehensive Survey (arXiv preprint 2601.11655, Jan 2026)

**In one sentence:** A survey of 175 papers and online resources on "issue resolution" (turning a GitHub issue into a working patch), sorted into Data, Methods and Analysis, with a list of open challenges.

**The problem:** Since SWE-bench, research on repository-level issue resolution has grown fast but is scattered. Earlier surveys covered code generation (writing a function from a prompt), not the harder job of navigating a real multi-file repo. The authors want one map of the field (§1).

**How it works / what they did:**
1. Define the task formally: given issue text D, codebase C and environment E, produce patch P; success = hidden tests T pass. Main metric is **Resolved Rate** (share of issues where all tests pass after the patch) (§2, Eq. 2; §A.2 splits T into fail→pass and pass→pass tests).
2. Collect literature by citation tracking (e.g. papers citing SWE-bench) and snowballing (following references) (§9).
3. Sort it into a taxonomy (Figs. 2–4):
   - **Data** (§3): evaluation sets, training sets (text, environments, trajectories = recorded agent runs), automated collection and synthesis.
   - **Training-free methods** (§4.1): frameworks (single-agent, multi-agent, fixed workflow), tool modules (bug reproduction, fault localization, code search, patch generation, patch validation, test generation), memory, inference-time scaling (e.g. MCTS, parallel sampling).
   - **Training-based methods** (§4.2): SFT (supervised fine-tuning) and RL (reinforcement learning: algorithms like GRPO/PPO/DPO, reward design, scaffold used for rollouts).
   - **Analysis** (§5): benchmark defects; agent behaviour (e.g. "overthinking").
4. Appendix tables list 40+ datasets (Table 1), trajectory datasets (Table 2), SFT models (Table 3), RL-trained models (Table 4) and general foundation models (Table 5).

**How they tested it:** No experiments. It is a literature survey; all numbers are copied from other papers.

**What they found:**
- SWE-Debate (A1) is listed as a multi-agent framework that "adopts graph-based structures to orchestrate a three-round debate… along code dependency traces" (§4.1.1). Graph-based fault localization that "construct[s] code dependency graphs to trace fault propagation" is a named tool category, citing SWE-Debate (§4.1.2).
- Benchmarks are often inflated by solution leakage (answer hints in the issue), vague issues and weak tests (§5.1).
- Dataset sizes (Table 1): SWE-bench 2,294; Verified 500; Lite 300; SWE-bench-Live 1,565 issues from 164 repos; Loc-Bench 560.
- OpenHands is the most-used RL rollout scaffold (§4.2.2). Small dense models (7B–32B) can compete when trained with domain-specific rewards (§A.4).

**Limitations and threats to validity (the authors' own):** (§9; no threats-to-validity section)
- They give high-level summaries, not full details, because of space.
- Their search used citation tracking and snowballing, so it may miss niche or very new work. They promise to keep their GitHub list updated.

**Future work they suggest:** (§7, "Challenges and Opportunities")
- Cut compute overhead: cheaper sandboxing and scheduling for RL rollouts and data checks.
- **Evaluate efficiency** (API cost, inference time) alongside resolve rate.
- Better visual reasoning: multimodal benchmarks and code-centric vision models.
- Safety: agents have deleted user code and cheated on evals. Need safer frameworks and alignment against reward hacking.
- Finer-grained (process) rewards instead of only test pass/fail.
- Fight data leakage and contamination: models may have memorised solutions (unclear training cutoffs), and benchmarks contain bad instances. Need decontamination and careful curation.
- Autonomous context management (compress or curate long interaction history, against "context rot").
- Stronger patch validation (regression tests, dependency analysis) and interfaces that help humans review patches.
- Cover more of the software lifecycle (requirements, design), not just implementation.

**Our own caveats:**
- No quantitative synthesis. The "Res.(%)" columns in Tables 3–5 never name the benchmark, and they mix different scaffolds, so the numbers are not comparable.
- It has nothing on localization-level metrics, and nothing on whether debate helps once compute is equal.
- Its "three-round debate" wording for SWE-Debate differs from our reading (2 rounds + 1 discriminator). Check A1 before quoting either.
- It is not a formal systematic review (no stated search strings or inclusion counts).

**Why it matters to us:**
- Background and related-work framing: it places SWE-Debate under multi-agent frameworks and graph-based fault localization.
- Phase 1: its "lack of efficiency-aware evaluation" challenge directly motivates our compute-matched 2x2.
- Phase 3: its contamination challenge supports using SWE-bench-Live with post-cutoff issues.

**Numbers worth quoting in the report:**
- 175 papers and resources surveyed (§1, §8).
- SWE-bench-Live: 1,565 instances, 164 repos. SWE-bench Verified: 500. Loc-Bench: 560 (Table 1).
- Efficiency and contamination are both listed as open challenges (§7).

---

### B11 — Inside the Scaffold: A Source-Code Taxonomy of Coding Agent Architectures (arXiv preprint 2604.03515v2, Apr 2026; single author, B. Rombaut)

**In one sentence:** The author read the source code of 13 open-source coding agents and built a 12-dimension taxonomy of their "scaffolds". A scaffold is the non-LLM code around the model: the control loop, tools, state and context handling.

**The problem:** Existing surveys label agents by abstract abilities ("tool-using", "planning"). Almost every agent fits every label, so the labels can't tell systems apart. Trajectory studies (analyses of agent run logs) watch what agents do but not why, and often use a different LLM for each agent. That mixes up scaffold effects with model effects (§1, §2.2).

**How it works / what they did:**
1. Pick agents: 22 candidates. Keep those that are coding-specific, have readable open source, and are not near-duplicates. That leaves 13, e.g. OpenHands, SWE-agent, Agentless, AutoCodeRover, Aider, Codex CLI, Moatless Tools, Prometheus (§3.1, App. A).
2. Pin each repo to a commit hash (App. B).
3. Derive dimensions by open coding (letting categories emerge from the data) on two pilot agents, Aider and OpenHands: 9 analysis dimensions, which became 12 taxonomy dimensions in 3 layers (§3.2):
   - control architecture (loop type, loop driver, control-flow code)
   - tool/environment interface (tool set, edit format, tool discovery, context retrieval, execution isolation)
   - resource management (state, context compaction, multi-model routing, persistent memory)
4. For each agent, record observation → classification → file:line evidence (§3.4). LLM coding assistants helped navigate the code; their output was checked against the source.

**How they tested it:** No benchmarks, on purpose. Benchmark scores confound scaffold, model and configuration, and SWE-bench issue text leaks solutions (§3.5). The only check was a self-verification of 296 extracted claims (§6.1).

**What they found:**
- Agents sit on continuous spectra, not in discrete types. Control ranges from a fixed pipeline (Agentless) to full MCTS (Moatless). Tool counts range from 0 to 37. Context compaction has 7 strategies (§4, §5.1).
- 11 of 13 agents combine several "loop primitives": ReAct, generate-test-repair, plan-execute, retry, tree search. 7 of 13 use a sequential ReAct loop as the main loop (§4.1.1).
- **Loop driver** (who decides the next step: user, scaffold or LLM) is "arguably the most fundamental" dimension. LLM-driven agents must solve localization themselves, so retrieval design becomes critical (§4.1.2, §5.3).
- Retrieval splits two ways. 8 agents make the LLM navigate with grep/find. Others build scaffold-side structure: Aider's PageRank dependency graph, AST indexes, Prometheus's Neo4j knowledge graph, Agentless's file→function→line narrowing. Only AutoCodeRover uses SBFL (spectrum-based fault localization, which ranks code by how often failing tests run it) (Table 8).
- **Sampling vs iteration** (§4.4.1): Agentless samples many patches and majority-votes. Most ReAct agents refine one attempt. Prometheus votes 10 times to *select* a patch. Benchmarks mix single-attempt quality with multi-attempt strategy (§5.5).
- DARS-Agent's critic uses the same model as its generator, so it "shares the generator's biases" (§4.3.3).
- Agents agree on tool categories, string-replace edits and Docker isolation. They differ on compaction, state and routing, which remain open questions (§5.2).

**Limitations and threats to validity (the authors' own):** (§3.5, §6)
- *Construct:*
  - Single-author bias. The 296-claim check (267 confirmed, 19 corrected, 10 accepted as simplifications) was done by the same person.
  - The pilot agents may have missed some dimensions. Prompt-engineering strategy was deliberately excluded.
- *Internal:*
  - The results are a snapshot at pinned commits, and agents keep changing.
  - The dimensions are not truly independent (e.g. loop driver correlates with retrieval). Interactions were not analysed.
- *External:*
  - Open-source only, a survivorship bias: proprietary agents and Claude Code are excluded.
  - 13 agents is not exhaustive. The paper claims analytical, not statistical, generality.
  - Python/SWE-bench-dominated corpus.
- *Reliability:*
  - A second analyst might place agents differently on a spectrum.
  - Static code reading misses runtime behaviour.
  - 10 of 13 agents are Python, so TypeScript idioms may be under-noticed.
  - The CLI vs SWE-bench category split is a simplification.
- *Scope (§3.5):* no performance data. No link between design and success rate is claimed.

**Future work they suggest:** (§7)
- Controlled experiments: vary one dimension (e.g. loop strategy) while holding tools and model fixed.
- Longitudinal re-analysis at later commits.
- Extend to proprietary agents and non-Python targets.
- Architecture-aware metrics that link dimensions to success, token cost and trajectory length.

**Our own caveats:**
- It is purely descriptive, with zero outcome evidence.
- It is LLM-assisted and single-author.
- There are small internal inconsistencies: "8 of 13" vs "Seven agents" using while loops (§4.1.3), and OpenHands at 70k stars (Table 1) vs 53k (§4.3.4).
- SWE-Debate and other debate systems are not in the corpus.

**Why it matters to us:**
- Phase 1: it backs our core design argument. Comparisons must hold the model fixed and vary one scaffold dimension, and multi-attempt strategies must be separated from single-attempt quality. Our compute-matched 2x2 does exactly this.
- It supports treating SWE-Debate as "scaffold-side graph retrieval + LLM selection by voting". That matches our retrieval vs selection split.
- Phase 2: the same-model-critic bias point supports the ColMAD fallback with different backbones.

**Numbers worth quoting in the report:**
- 13 agents, 12 dimensions, 3 layers (Abstract).
- 11/13 agents compose multiple loop primitives (§4.1.1, §5.4).
- Tool counts 0–37; 7 compaction strategies (§5.1).
- 296 claims checked: 267 confirmed, 19 corrected, 10 simplifications (§6.1).

---

### B12 — SWE-Effi: Re-Evaluating Software AI Agent System Effectiveness Under Resource Constraints (arXiv preprint 2509.09853v2, Sep 2025)

**In one sentence:** The paper re-scores 15 scaffold+LLM pairs on 50 SWE-bench Verified issues. The scores measure how many issues get solved *per unit of tokens, dollars, CPU time and inference time*, not just resolve rate.

**The problem:** Leaderboards report only resolve rate and quietly assume unlimited compute. Is +1% resolve rate worth 5x the cost? Slow, expensive scaffolds also make RL (reinforcement learning) rollouts impractical (§1).

**How it works / what they did:**
1. **Core metrics** per issue (§3.1): resolve rate, CPU time (scaffold's local work, e.g. running tests), LLM calls, input/output tokens.
2. **Normalized inference time** (§3.1.1). They fit a linear regression on 515,041 API-call logs, using GPT-4o-mini as the reference: time = 1.457 s + 4.266e-5 × input tokens + 4.999e-3 × output tokens (validation R² = 0.79). This replaces noisy wall-clock time.
3. **Effectiveness scores** (§3.2). Plot cumulative resolved issues against resources used, take the area under the curve (AUC), and normalise to 0–1:
   - **EuTB**: tokens, cap 2M
   - **EuCB**: dollars, cap $1
   - **EuCTB**: CPU time, cap 30 min
   - **EuITB**: inference time, cap 30 min

   A high score means the system solves issues cheaply.

**How they tested it:** (§4)
- Scaffolds: AutoCodeRover, OpenHands, SWE-agent (agentic), Agentless, Agentless-Mini.
- Models: GPT-4o-mini, Llama-3.3-70B (FP8), Qwen3-32B.
- Data: 50 SWE-bench Verified issues, stratified by project.
- Setup: default settings, except SWE-agent was capped at $1/issue. Parallelism was disabled. Prices come from OpenRouter (§7.1).

**What they found:**
- **The model matters more than the scaffold** (§5.1, Table 1). SWE-agent: EuTB 21.8% with Qwen3-32B but 5.1% with GPT-4o-mini. With GPT-4o-mini it resolves 10% while using 181 calls and 8.1M input tokens (Table 2).
- The best resolve rate is Agentless+Qwen3-32B at 48%, but it is costly: 83.1 calls and 727.9 s CPU on average (§5.1).
- AutoCodeRover+Qwen3-32B reaches 38% with only 14.7 calls and 55.5k input tokens.
- **The number of calls drives cost more than the size of each call** (§5.2). The reasoning model Qwen3-32B needs ~15 calls vs ~38 for Llama-3.3-70B on AutoCodeRover, so it uses fewer tokens overall.
- **Token snowball** (§5.3, Fig. 1): each call re-sends the growing history, so input tokens grow roughly linearly with the number of calls, even when no progress is made.
- **Expensive failures** (§5.4, Table 3): unresolved attempts usually cost more than resolved ones. SWE-agent+GPT-4o-mini: 8,867k vs 1,865k tokens and 658 s vs 167 s total time.
- They report a trade-off between token-budget and time-budget effectiveness, which matters for RL (Abstract, §6).

**Limitations and threats to validity (the authors' own):** (no dedicated section; taken from §1 and §6)
- The work is an introduction and initial insight, "in no way exhaustive". The results are not a "final, definitive verdict" on the five scaffolds.
- Only 15 scaffold-model pairs, cut down from a larger pool because of cost and time.
- Only 50 of the 500 Verified issues. Early full runs took up to two weeks and several hundred dollars.

**Future work they suggest:**
- Evaluate more systems with the community, through the released code, data and public leaderboard (§6).
- Better budget management that stops a run once the snowball grows too large, and better memory abstraction to slow its growth (§5.3).
- "Progress-aware" scaffolds that detect stagnation (futility detection) and abort or redirect (§5.4).
- Lightweight scaffolds as better foundations for RL (§6).

**Our own caveats:**
- **Small sample and single run.** 50 issues means 1 issue = 2 pp. There are no repeats, variance or significance tests.
- **Some numbers don't match their text.** They claim >4x more "inference time" for failures, but Table 3 shows SWE-agent+GPT-4o-mini inference time of 51.1 s (fail) vs 107.3 s (success). The 4x is really *total* time. Also, Agentless+GPT-4o-mini successes take longer than its failures.
- Settings are not uniform (only SWE-agent has the $1 cap). Models were served by different providers. The time model is calibrated to GPT-4o-mini, not to self-hosted serving. The Llama price lists output as cheaper than input ($0.38 in, $0.12 out), which looks like a typo.
- The claimed token/time trade-off has no dedicated analysis section.
- It measures end-to-end resolve rate only, with no localization metrics.

**Why it matters to us:**
- Phase 1: it gives a ready vocabulary and method for our compute-matched 2x2. We can report tokens, calls and time per arm, and even EuTB-style AUCs.
- Debate multiplies calls (5 agents × rounds). Their finding that "number of interactions is the primary cost driver" is exactly why SWE-Debate's −4.2 comparison needs token matching.
- Qwen3-32B performed strongly here, which is useful evidence for choosing our open-weights vLLM backbone.
- The snowball and expensive-failure findings suggest logging per-issue cost split by success and failure.

**Numbers worth quoting in the report:**
- SWE-agent EuTB 21.8% (Qwen3-32B) vs 5.1% (GPT-4o-mini) (Table 1).
- Agentless+Qwen3-32B: 48% resolve, 83.1 calls, 727.9 s CPU (Tables 1–2).
- Failed vs resolved, SWE-agent+GPT-4o-mini: 8,867k vs 1,865k tokens (Table 3).
- Normalized-time regression: R² = 0.79 on 515,041 calls (§3.1.1).

---

## 6. C — Skim and cite (background, surveys, older methods)

### C1 — Large Language Model-Based Agents for Software Engineering: A Survey (ACM TOSEM, 2026; DOI 10.1145/3796507)

**In one sentence:** A systematic survey of 124 papers on LLM-based agents (an LLM plus tools, memory and planning, sometimes several LLMs working together) for software engineering (SE), sorted by SE task and by agent design.

**What it is / what they did:** Papers were collected up to 11 Sept 2024 via DBLP keyword search, snowballing (following references) and emails to 321 authors (§3). §4 goes task by task. The parts most relevant to us are debugging/fault localization (§4.5) and end-to-end issue resolution on SWE-bench (§4.8). §5 looks at agent design: planning, memory, tools, and multi-agent roles, structures and information flow (§5.2).

**Key findings:**
- Only two LLM agents do fault localization (FL, finding the buggy code): AgentFL (multi-agent, Java) and AutoFL (single agent with tools) (Table 9, §4.5.1). Common FL failures are getting lost in project context, incoherent multi-step reasoning, and methods too long for the context window (§4.5.4). Multi-agent debugging adds complexity: AutoSD takes about 5× longer than a standalone LLM (§4.5.5).
- Issue localization (from a plain-text issue, with no failing test) uses four strategies: retrieval (BM25), navigation, spectrum-based and simulation/MCTS over a repo knowledge graph (§4.8.3). Fully autonomous localization (SWE-agent) did worst on SWE-bench Lite, and simple Agentless-style pipelines beat many complex agents (§4.8.8). The authors say this "place[s] higher demands on evaluating the effectiveness of complex agent designs."
- Multi-agent structures: layered, circular, star, tree and mesh. Performance saturates as more agents are added, whatever the structure (§5.2.2).
- Open challenges (§6): (1) finer-grained metrics for intermediate steps instead of success rate only, plus cost reporting (only 46.7% of papers report efficiency); (2) better, more realistic benchmarks, since SWE-bench has vague issues; (3) human-agent collaboration; (4) perception modalities beyond text; (5) under-covered SE tasks (design, verification); (6) software-specific training data; (7) building SE expertise into agents; (8) trustworthiness. They rank benchmarks and metrics as the top priority.

**Limitations / future work (authors'):** (§7.2 Threats to Validity) Papers were screened by hand, so relevant ones may be missing. Several conclusions rest mostly on preprints: multi-agent requirements engineering, knowledge-enhanced bug detection, coverage-driven unit testing, visual input and memory formats.

**Why it matters to us:** This is the main background reference for Phase 1. It explicitly calls for step-level metrics (our retrieval-vs-selection split) and for reporting cost (our compute matching). It also notes that simple pipelines beat complex agents, which is the question our 2x2 tests.

---

### C2 — Large Language Models for Software Engineering: A Systematic Literature Review (ACM TOSEM 33(8), Dec 2024)

**In one sentence:** A systematic literature review (SLR: a survey that follows a fixed, documented search-and-filter procedure) of 395 papers from Jan 2017 to Jan 2024. It covers which LLMs are used in SE, what data they use, how they are tuned and evaluated, and which SE tasks they handle.

**What it is / what they did:** The survey answers four research questions (RQs): RQ1 LLM types (encoder-only, encoder-decoder, decoder-only), RQ2 datasets, RQ3 tuning, prompting and evaluation, RQ4 SE tasks. It uses manual plus automated search on 7 publisher platforms, snowballing (following references) and quality criteria (§2). The paper predates the "agents" wave and is about standalone LLMs.

**Key findings:**
- The field moved to decoder-only (GPT-style) models. In 2022, 51.41% of papers used decoder-only models (§3.2).
- Task spread (§6.1, Table 10): software development 56.65%, maintenance 22.71%, quality assurance 15.14%, requirements 3.9%, design 0.92%, management 0.69%. Fault localization is tiny: 3 papers, plus 5 on bug localization.
- Most studies are generation tasks (70.97%), then classification (21.61%) (§6.1).
- Challenges (§8.1):
  - model size and deployment cost;
  - dependence on data, including **benchmark contamination** (overlap between training and test data inflates scores);
  - ambiguity in code generation;
  - poor generalization, e.g. renaming variables hurts CodeBERT;
  - standard metrics (accuracy/F1) miss robustness and interpretability;
  - interpretability, trust and ethics.
- Opportunities (§8.2–8.3): code-specialized LLMs, "Collaborative LLMs" (several LLMs, or LLMs plus other ML models), **graph-based inputs** (these are scarce, yet graphs "capture the structural relationships and dependencies in code"), a unified evaluation framework, combining LLMs with static/dynamic analysis, security, and SE4LLM (SE practices for building LLMs).

**Limitations / future work (authors'):** §7 Threats to Validity lists three threats: relevant articles may have been missed by the search; study selection bias (handled by a second review from two outside reviewers); and subjective "empirical knowledge bias" in classifying papers.

**Why it matters to us:** Only background. It gives citable support for three points: contamination is a known risk (Phase 3, SWE-bench-Live), graph/structure inputs are under-used, and collaborative multi-LLM setups are an open direction (Phase 2 fallback).

---

### C3 — A Quantitative and Qualitative Evaluation of LLM-Based Explainable Fault Localization ("AutoFL") (FSE 2024; arXiv 2308.05487v3)

**In one sentence:** AutoFL lets one LLM (GPT-3.5/GPT-4) explore a repository through four tool calls, write an explanation of the bug, then name the buggy method; it matches or beats classic fault-localization (FL) methods while needing only one failing test.

**What it is / what they did:** Stage 1: the LLM gets the failing test and stack trace and may make up to N=10 function calls (covered classes, covered methods, code snippet, comments) before explaining the root cause. Stage 2: it must name the culprit methods with no more tool calls (§3). They run it R=5 times and vote: each run splits 1 point among the methods it names; the top score is used as a "confidence" (§3.3, Eq. 1–2). Tested on 798 bugs: Defects4J v1.0 (353 Java) and BugsInPy (445 Python), plus a manual check of 300 explanations and interviews with 16 professional developers (§4). Metric acc@k = number of bugs whose buggy method is in the top k.

**Key findings:**
- acc@1 beats Ochiai (a spectrum-based FL method, SBFL: ranks code by how often failing vs passing tests run it) by 19.7% on Defects4J and 166.7% on BugsInPy with GPT-3.5, and 233.3% on BugsInPy with GPT-4 (§1, §5.1, Fig. 3). But GPT-3.5 lags SBFL at acc@3/acc@5 on Defects4J; GPT-4 fixes this. It always beats Test-GPT3.5 (same LLM, no tool calls).
- Merging more runs helps a lot (Fig. 4); one GPT-4 run beats five merged GPT-3.5 runs. Cost: 87.24 s per bug for 5 GPT-3.5 runs on Defects4J (Table 3); 5.37 tool calls per run on average.
- The voting confidence correlates with correctness: Spearman 0.57 (Defects4J) / 0.52 (BugsInPy) with Precision@1 (Table 4).
- Only 20% of single explanations are accurate, but 56.7% of bugs get at least one accurate one (Table 5). 11 of 16 developers found 10 explanations per bug too many and wanted a summary (§5.4).

**Limitations / future work (authors'):** (§7 Threats to Validity)
- Internal: run time depends on OpenAI servers and LLM randomness (averaged over runs); human error in rating explanations (two raters, Cohen's κ 0.55); data leakage (bug fixes may be in training data), argued against only by the gap to the Test-GPT3.5 baseline.
- Construct: developers tested on pandas, not their own code, for security reasons, so impressions may not match real work.
- External: only Java/Python unit tests; developers from just three companies; results depend on the LLM chosen.
- Failure analysis (§5.3): custom test helpers (14 of 26 failed bugs), too many classes for the 10-call budget (6), over-long methods hitting the context limit (3), logic errors (3).
- Future work (§6, §8): rank explanations automatically, e.g. with LLM-generated tests or patches. These "dynamic scores" correlate only weakly with quality, but they raise the precision-recall AUC for predicting Precision@1 by up to 5.4%. Asking GPT-3.5 to rate explanations mostly rewards length.

**Why it matters to us:** This is background for a single-agent, tool-using LLM baseline, like our single-agent arms. Two ideas are useful: voting across repeated runs as a confidence signal, and "more runs = better" (Fig. 4). The second is why our 2x2 must match compute. Its setting (a failing test, method level) is not ours (an issue text, file/function level on SWE-bench).

*Our note:* Table 5 lists 'Bland' as 43.0% of single explanations, but the text says 46.7%.

---

### C4 — Large Language Models for Test-Free Fault Localization ("LLMAO") (ICSE 2024; arXiv 2310.01726)

**In one sentence:** LLMAO adds a small trainable "bidirectional adapter" on top of a frozen code LLM (CodeGen) to score every line of a file as buggy or not. It needs no tests at all.

**What it is / what they did:** CodeGen reads code only left-to-right, so each line's representation "sees" only the code above it. LLMAO takes CodeGen's hidden state at each newline and adds 2 new Transformer layers that can see both directions. A sigmoid layer then gives each line a bug probability (§3). Only the adapter is trained, with 10-fold cross-validation and labels taken from the lines changed in the fix commit (§4.1). Datasets: Defects4J v1.2.0 (395 Java bugs), 226 unseen-project bugs from Defects4J v2.0.0, BugsInPy (493 Python bugs), and Devign (5,260 C security vulnerabilities). Metric: Top-N = number of bugs with at least one truly faulty line in the top N.

**Key findings:**
- With CodeGen-16B on Defects4J: Top-1/3/5 = 88/149/183 (22.3%/37.7%/46.3%). The best test-based ML baseline, TRANSFER-FL, gets 86/135/160; Ochiai (a test-coverage formula) gets 19/65/99 (Table 2). So the Top-1 gain over TRANSFER-FL is only 2 bugs.
- Bigger base model = better: AUC 0.539 (no pretraining) → 0.573 (350M) → 0.638 (6B) → 0.677 (16B) on Defects4J (§4.2, Fig. 6).
- Ablations (Table 2): no pretraining → Top-5 only 30; no adapter (CodeGen-16B plus a linear layer) → Top-5 85. The adapter matters.
- Unseen projects: 72/93/123 of 226 (Table 2). Harder transfer to BugsInPy: Top-1 only 10.3% (Table 3).

**Limitations / future work (authors'):** (§6 "Threats to validity")
- Internal: the fix-commit diff is a noisy stand-in for the "true" faulty lines, and annotators can disagree. They reduce this with curated datasets and a public replication package.
- External: results may not carry over to real-world use; Defects4J is so widely used that methods may overfit to it (hence two more datasets); CodeGen's training data (GitHub up to 2021) may include these repositories. The authors argue the risk is small because the bug labels were not in that data.
- Construct: they rely on standard metrics, 10-fold cross-validation and three datasets.
- No future-work section.

**Why it matters to us:** Background only. It is a trained, line-level localizer that uses no issue text, so it is very different from our issue-to-file/function setting and from agentic or debate methods. Useful as an example of test-free fault localization, and its §6 admits training-data contamination (the model may have seen the answers) is possible. Our note: the abstract's "Top-1 improved by 2.3%–54.4%" does not match Table 2 (54.4% is the unseen-project Top-5 rate). Also, the conclusion's "23/155" does not match the table.

---

### C5 — Where Should the Bugs Be Fixed? More Accurate Information Retrieval-Based Bug Localization Based on Bug Reports ("BugLocator") (ICSE 2012)

**In one sentence:** BugLocator is a classic, pre-LLM method: it treats a bug report as a search query, ranks source files by text similarity, and boosts files that were changed to fix similar past bugs.

**What it is / what they did:** This is IR-based bug localization (IR = information retrieval, i.e. search-engine-style text matching; no tests or execution needed). Step 1: a revised Vector Space Model (rVSM) scores each file by TF-IDF cosine similarity to the report. TF-IDF weights a word by how often it appears in this file and how rare it is elsewhere. rVSM uses log term frequency and multiplies by a logistic "file length" factor, because larger files are more often buggy (§III.C, Eq. 7). Step 2: SimiScore spreads credit to files fixed for previously fixed bugs whose reports look similar (§III.D, Eq. 8). Step 3: final score = (1−α)·rVSM + α·SimiScore, best at α ≈ 0.2–0.3 (Eq. 9). Evaluated on 3,479 fixed bugs from Eclipse 3.1 (12,863 files), AspectJ, SWT and ZXing, using Top-N, MRR (mean of 1/rank of the first correct file) and MAP (mean average precision over all correct files) (§IV).

**Key findings:**
- Eclipse: 29.14% of bugs have a correct file at rank 1, 53.76% in the top 5, 62.60% in the top 10; MRR 0.41, MAP 0.30 (Table II).
- rVSM alone vs classic VSM on Eclipse, Top-1: 24.36% vs 6.86% (Table III). Similar-bug information raises it further to 29.14% (Table IV vs II).
- Beats the VSM, LDA, SUM and LSI text models; e.g. Eclipse Top-1 is 6.86%, 0.32%, 1.72% and 4.23% for those (§V.A, Fig. 6).

**Limitations / future work (authors'):** (§VI Threats to Validity, §VIII)
- Only open-source projects; may differ from commercial ones (evaluating these is left as future work).
- Relies on meaningful variable/method/class names.
- Relies on bug-report quality; vague or misleading reports hurt results.
- Future work: add program execution information; try it on industrial projects.

**Why it matters to us:** Background and history. It is the classic "issue text → file" baseline family (IR-based bug localization). It shows two ideas that still work in LLM-era localizers: matching words between the report and the code, and using past fix history. Our note: the file-size prior (bigger files ranked higher) is a reminder to check whether our candidate chains simply favour large files.

---

### C6 — Improving Bug Localization using Structured Information Retrieval ("BLUiR") (ASE 2013)

**In one sentence:** BLUiR improves on BugLocator (C5) by treating each source file as a structured document with separate class, method, variable and comment fields, and matching them separately against the bug report's summary and description.

**What it is / what they did:** They parse each Java file's AST (abstract syntax tree, i.e. the parsed structure of the code) to pull out class names, method names, variable names and comments. Identifiers are indexed both whole (e.g. `ConsoleView`) and camel-case split (`console`, `view`) (§IV.B). They use the off-the-shelf Indri search engine with BM25-style TF-IDF (a standard, well-tuned text-ranking formula that already corrects for document length). They run 8 searches (2 report fields × 4 code fields) and add up the scores (§IV.D, Eq. 8). Parameters were tuned only on AspectJ; SWT, Eclipse and ZXing were kept for blind testing. It uses the same benchmark as BugLocator (§V).

**Key findings:**
- Indexing full identifiers as well as split tokens helps: Eclipse Top-1 rises from 529 to 746 bugs (Table IV).
- Structure (separate fields) helps further: Eclipse Top-1 rises from 746 to 952, MAP from 0.26 to 0.32 (Table V). Cost goes up about 3–12× but stays under 6 s per query.
- Without past-bug data, BLUiR beats BugLocator *with* past-bug data on 3 of 4 projects; e.g. Eclipse Top-1 952 vs 896 (Table VI). Adding past-bug data to BLUiR gives 1,013 (Table VI).
- A plain, well-tuned IR toolkit with no changes already beats BugLocator, so part of BugLocator's reported gain comes from a weak baseline (§I, §X).

**Limitations / future work (authors'):** (§VIII Threats to Validity, §X)
- Construct: they argue it is strong, since they use a shared benchmark and standard metrics.
- Internal: tied to Java/object-oriented constructs (other OO languages are future work); assumes meaningful names and comments; depends on bug-report quality; reports written by developers probably help, while end-user reports would help less; possible errors in the borrowed dataset; system-domain projects may have their own biases.
- External: only 4 open-source projects; may not generalize to other or industrial projects. Future work: more subject systems.
- ZXing has only 20 bugs, so no conclusions can be drawn there. The per-query analysis covers SWT only, because BugLocator crashed on the other three projects (§VI).
- Future work: bug-report summarization; learning-to-rank for parameters (k1, b) instead of tuning on one project; weighted field combination; other datasets (moreBugs); method-level localization.

**Why it matters to us:** Mostly background. Two transferable lessons. First, code structure from the AST (class and method names) is a strong localization signal, which supports our choice of AST-based graphs. Second, a "new method beats weak baseline" result can disappear against a well-tuned baseline, which supports our compute-matched single-agent arms. Our note: the text says 3,379 reports, but Table II sums to 3,479; the AspectJ count is 286 in the table but "298" in §V.A.

---

### C7 — Scaling Large Language Model-based Multi-Agent Collaboration ("MacNet") (ICLR 2025; arXiv 2406.07155v3)

**In one sentence:** MacNet arranges LLM agents on a directed acyclic graph (DAG: arrows, no loops) of up to 64 nodes (over 1,000 agents in the densest layout). The authors report a "collaborative scaling law": quality rises in an S-shape as agents are added.

**What it is / what they did:** Each node is an "actor" that produces an artifact (an answer, code or text). Each edge is a "critic" that reviews it and tells the next actor how to improve it (§2.1). Agents act in topological order: each node runs only after every node that feeds into it. Only the refined artifact is passed on, not the whole chat history. The authors argue this keeps context growth linear instead of quadratic (§2.3, Eq. 5). They test chain, star, tree, mesh, layer and random layouts with GPT-3.5 on MMLU, HumanEval, SRDD (software requirements) and CommonGen-Hard. Baselines: CoT, AutoGPT, GPTSwarm, AgentVerse (§3). The default network has about 4 nodes; for scaling, they grow it from 2^0 to 2^6 nodes.

**Key findings:**
- Average quality: MacNet-Random 0.6522 and Mesh 0.6316 vs CoT 0.5757 and AgentVerse 0.5805 (Table 1). No topology wins on every task. On HumanEval, MacNet-Chain scores 0.3720, far below CoT's 0.6098 (Table 1).
- Irregular (random) layouts beat regular ones and take about 51.92% less time than mesh (§3.2). Divergent layouts (one agent fanning out to many) beat their reversed, convergent versions (Fig. 6).
- Quality follows a logistic (S-shaped) curve in log(number of nodes) and saturates around 2^4 nodes to ~100 agents (§3.3, Eq. 6, Fig. 7).
- Baselines given the same number of LLM calls via majority voting or best-of-N gain only 0.9% and plateau at about 8 agents (§3.3). Artifact length grows 7.51× from 2^0 to 2^4 nodes (§3.4).

**Limitations / future work (authors'):** The paper has no limitations section. Scattered remarks:
- There are limits to how far scaling helps (§5).
- Deep topologies can "lose track" of distant agents, causing the artifact to roll back to an older version (§3.2).
- Convergent nodes (where several artifacts must be merged) are hard (§3.2).
- The scaling fit uses network size only; future work should add profiles, tools, communication protocols and social routing (footnote 9).

**Why it matters to us:** Relevant to the "does debate/collaboration help at equal compute?" question. They claim a compute-equalised check (majority voting with the same LLM calls), but it gets only one sentence and no table. Our note: longer artifacts help "length-sensitive metrics" by the authors' own admission (§3.2), so part of the gain may come from length, not reasoning. It uses one model (GPT-3.5) with ~4 nodes by default and no fault-localization task. Use it as motivation for scaling agents, not as evidence that debate helps localization.

---

### C8 — Graph Retrieval-Augmented Generation: A Survey (arXiv 2408.08921v2, Sept 2024)

**In one sentence:** This survey claims to be the first overview of GraphRAG (retrieval-augmented generation, RAG, that retrieves nodes, triples, paths or subgraphs from a graph instead of plain text chunks). It splits GraphRAG into three stages: G-Indexing, G-Retrieval and G-Generation.

**What it is / what they did:** They formalize GraphRAG as retrieving an optimal subgraph G* and then generating from it (§4, Eq. 4–6). Then they sort methods by:
- graph source and indexing (§5);
- retriever type: non-parametric (rules or graph search), LM-based, or GNN-based (GNN = graph neural network) (§6.1);
- retrieval paradigm: once, iterative, or multi-stage (§6.2);
- granularity: node, triple, path, subgraph or hybrid (§6.3);
- how the graph is turned into LLM input: edge tables, natural language, code-like forms, syntax trees, node sequences (§7.2).

Almost all examples are knowledge-graph question answering, not code.

**Key findings:**
- Plain RAG ignores relationships, returns redundant text ("lost in the middle") and misses global information. GraphRAG targets all three (§1).
- There is a trade-off: non-parametric retrievers are fast but less accurate, while LM/GNN retrievers are more accurate but costly. Iterative retrieval, including LLM agents walking the graph, is more accurate but slower (§6.1.4, §6.2.4).
- Evaluation is mostly by downstream answer quality (EM, F1, accuracy). Measuring retrieval quality directly is hard. One proposal is the ratio of answer coverage to retrieved-subgraph size (§9.3.2).
- A software use exists: a chatbot that answers questions over a package's dependency graph (§9.2.6).

**Limitations / future work (authors'):** The paper has no limitations section. §10 lists open problems: dynamic/updatable graphs; multi-modal graphs; scalable retrieval (most methods only handle graphs with thousands of entities); combining with graph foundation models; lossless compression of long retrieved context; standard benchmarks (none exist); broader applications.

**Why it matters to us:** It gives the vocabulary for describing SWE-Debate's pipeline: its graph is a non-parametric index, its chain-building is iterative path retrieval, and its chains are "path"-granularity. It also supports our split of "retrieval" (is the right file in any chain) from generation/selection, which the survey says the field rarely measures directly.

---

### C9 — From Local to Global: A GraphRAG Approach to Query-Focused Summarization ("GraphRAG") (arXiv preprint 2404.16130v2, Feb 2025; marked "under review"; Microsoft Research)

**In one sentence:** GraphRAG uses an LLM to build a knowledge graph from a document collection, groups the graph into communities and summarises each one. It then answers "big picture" questions by map-reducing over those summaries. It beats ordinary vector RAG on comprehensiveness and diversity.

**What it is / what they did:** Pipeline (§3.1): (1) split the text into 600-token chunks; (2) an LLM (GPT-4-turbo) extracts entities, relationships and claims from each chunk, and re-asks itself to "glean" missed entities (self-reflection, App. A.2); (3) merge these into a graph (entities matched by exact name); (4) run Leiden community detection (an algorithm that finds densely connected groups) as a hierarchy, levels C0 (root) to C3 (leaf); (5) the LLM writes a summary for each community. To answer a query: each summary gives a partial answer with a 0–100 helpfulness score (map), then the top ones are merged into one final answer (reduce) (§3.1.6). Tested on a ~1M-token podcast corpus and ~1.7M tokens of news, with 125 LLM-generated "global sensemaking" questions each (§3.2, §4.1). Baselines: vector RAG ("SS": fetch the chunks closest to the question by embedding similarity) and map-reduce over raw text ("TS"). An LLM judge compares answers pairwise on comprehensiveness, diversity, empowerment and directness (a control) (§3.3). Experiment 2 re-checks with claim counts and claim clusters (§4.2).

**Key findings:**
- Against vector RAG, GraphRAG's comprehensiveness win rate is 72–83% (podcast) and 72–80% (news); diversity 75–82% and 62–71% (§5.1, Fig. 2). Vector RAG wins on directness, as expected.
- Empowerment is mixed; the win comes mostly from coverage, not usefulness (§5.1, Table 6).
- Root-level (C0) summaries need 9–43× fewer tokens per query than TS while still beating vector RAG (72% comprehensiveness, 62% diversity) (Table 2, §5.1).
- Claim-based check: every global method produces more claims than vector RAG (e.g. news C0 34.18 vs SS 25.23), but there are no significant differences among the global methods or vs TS (Table 3, §5.2). The LLM judge agrees with the claim metrics 78% of the time (comprehensiveness) and 69–70% (diversity), counting only non-tie cases.

**Limitations / future work (authors'):** (§6.1, §6.2)
- Only two corpora of ~1M tokens each; generalisation to other domains and use cases is untested.
- No comparison of fabrication (hallucination) rates, e.g. with SelfCheckGPT.
- Keeping specific examples, quotes and citations matters for empowerment; better extraction prompts may help (§5.1).
- Future work: more local, embedding-based matching of queries to graph annotations; hybrid schemes with just-in-time community reports; "roll-up" across levels and "drill-down" exploration.
- Broader impact: wrong answers can mislead decisions, so AI use and possible errors should be disclosed.

**Why it matters to us:** Background for the "graph + LLM" idea in our project's framing (the project is titled "Multi-Agent Deep Research GraphRAG"). It is not a code or fault-localization paper. Its graph is LLM-extracted from prose, while ours is a static `ast` code graph. It is also judged by an LLM with no ground truth, while we have gold files. Our note: it is a preprint, the questions and the judging both come from LLMs, and indexing cost (281 min for the podcast set, §4.1.3) is not counted against the baselines.

---

### C10 — Evaluation and Benchmarking of LLM Agents: A Survey (KDD 2025; arXiv 2507.21504)

**In one sentence:** A short survey from SAP Labs that sorts LLM-agent evaluation along two axes: *what* to evaluate (behaviour, capabilities, reliability, safety) and *how* to evaluate (interaction mode, datasets, metric computation, tooling, environment).

**What it is / what they did:** The survey builds a taxonomy tree (§2) and lists example metrics and benchmarks for each branch. It adds a section on enterprise-specific challenges (§5). It is general, not code-specific. There is no systematic paper-collection method.

**Key findings:**
- **Behaviour metrics (§3.1):** task success rate, output quality, and latency and cost (e.g. token usage).
- **Process-level metrics (§3.2):** Node/Edge F1 for tool plans, and AgentBoard's Progress Rate, which compares the actual trajectory to the expected one.
- **Reliability (§3.3.1):** pass@k means the agent succeeds at least once in k runs. pass^k (from τ-bench) is stricter: the agent must succeed in *all* k runs. Agents are non-deterministic, so consistency needs repeated runs, which is expensive (§5.2).
- **Multi-agent evaluation (§3.2.4):** LLM agents coordinate in natural language, so the reward-based methods from classic multi-agent RL do not fit. There are few metrics beyond "collaborative efficiency".
- **How metrics are computed (§4.3):** code-based checks (reproducible but rigid); LLM-as-a-Judge and Agent-as-a-Judge (scalable); human evaluation (the gold standard, but expensive).

**Limitations / future work (authors'):** No limitations section. Future directions (§6):
- holistic frameworks that cover several dimensions at once;
- more realistic settings (multi-user, access control);
- automated, scalable evaluation (synthetic data, simulators, LLM judges);
- time- and cost-bounded evaluation protocols.

Enterprise gaps (§5): role-based access, reliability guarantees, long-horizon interaction, compliance.

**Why it matters to us:** It supports Phase 1 method choices: report cost/tokens next to accuracy, run several seeds, and consider pass^k-style consistency for the debate vs single-agent arms. It also backs measuring intermediate steps (retrieval, then selection) and not only the final outcome.

---

### C11 — A Comprehensive Survey on Benchmarks and Solutions in Software Engineering of LLM-Empowered Agentic System (arXiv 2510.09721v3, Oct 2025)

**In one sentence:** An NTU-led survey of 150+ papers and 50+ benchmarks. It links SE benchmarks (code generation, translation, repair, etc.) to three kinds of solution: prompt-based, fine-tuning-based and agent-based.

**What it is / what they did:**
- A two-part taxonomy: Solutions × Benchmarks (§III), with a pipeline "from task specification to deliverables."
- Agent-based solutions are split into four parts (§IV):
  - planning (e.g. MAGIS/MASAI role pipelines, LingmaAgent's MCTS over a repo knowledge graph, Agentless's fixed localize-repair-validate flow);
  - reasoning and self-refinement (generate-test-revise loops; majority voting in Nemotron-CORTEXA and Co-PatcheR);
  - memory (repo knowledge graphs, code graphs such as CGM);
  - tools (SWE-agent's interface, SBFL (spectrum-based fault localization) in AutoCodeRover).
- Benchmark tables list sizes, e.g. SWE-bench has 2,294 instances (Table II).

**Key findings:**
- The field has moved from prompting to agents that combine planning, memory and tools. Simple fixed pipelines (Agentless) are presented as a strong counterpoint to complex planning (§IV).
- It notes a finding that many "solved" SWE-bench issues are actually incorrect, which is a validation problem (§IV, citing Wang et al.).
- Challenges and future directions (§VIII):
  - **(A) Scalability:** "project amnesia"; they propose reasoning over ASTs/CFGs/CPGs (code graphs) with tiered memory.
  - **(B) Evaluation:** too much reliance on pass@k and static tests that can be memorized; they call for production-readiness and cost metrics.
  - **(C) Domain adaptation.**
  - **(D) Multi-agent coordination:** current frameworks use simple sequential or central orchestration. They call for decentralized protocols, conflict resolution, complementary roles such as generator + verifier, and benchmarks that measure coordination efficiency and communication overhead.
  - **(E) Continuous learning.**
  - **(F) Responsible deployment** (IP, cost, deskilling).

**Limitations / future work (authors'):** No limitations or threats section for the survey itself. Future work = the §VIII items above.

**Why it matters to us:** Challenge D, which calls for measuring coordination efficiency and communication overhead, supports our compute-matched 2x2. Challenge A (reasoning over code graphs) supports graph-grounded debate (Phase 2). Otherwise this is background.

*Our note:* The extracted text contains a shorter duplicate draft of §VIII A–C before the full version. Also, a few references look unreliable: e.g. [2] credits "OpenDevin" to authors who did not write it. Double-check any citation taken from this survey.

---

### C12 — Software Testing With Large Language Models: Survey, Landscape, and Vision (IEEE TSE 50(4), Apr 2024)

**In one sentence:** A survey of 102 studies that used LLMs for software testing, organized from the testing side (which task) and the LLM side (which model, prompt style and extra techniques).

**What it is / what they did:**
- §IV covers testing tasks: unit test generation, test oracles, system test input generation, bug analysis, debugging and program repair.
- §V covers the LLM side: which models, fine-tuning vs prompting, and combination with traditional techniques.
- Debugging (§IV-E) includes fault localization:
  - ChatGPT/GPT-4 compared with classic FL, including how consistent the LLMs are;
  - AutoFL, which works from a single failing test;
  - LLMAO, which finds buggy lines without test coverage;
  - LLM4CBI.
- These are standalone LLMs, not multi-agent systems.

**Key findings (§VI-A Challenges):**
- **Coverage:** LLMs struggle to produce diverse tests. For example, unit tests on SF110 reach 2% line and 1% branch coverage.
- **Test oracle problem:** knowing what the correct output should be is still hard.
- **Rigorous evaluation:**
  - Few benchmarks exist; repair relies mainly on Defects4J and QuixBugs.
  - **Data leakage:** the whole Defects4J repository is in BigQuery, a common LLM training source, so reported results may be optimistic.
  - Codex fixes 39/40 QuixBugs Python bugs but only 16/72 real Stack Overflow DL bugs.
- **Real-world use:** companies prefer smaller open-source models for privacy and cost, and these are unlikely to match the reported numbers.

**Limitations / future work (authors'):** No limitations or threats section. Opportunities (§VI-B):
1. LLMs in early testing stages;
2. integration and acceptance testing;
3. more software types;
4. non-functional testing;
5. advanced prompting (only 5 of 11 common techniques are used; role-playing is suggested, and so is graph prompting over dependency and control-flow structure);
6. combining LLMs with traditional tools and analysis.

**Why it matters to us:** Background only. It is a citable, peer-reviewed source for data leakage in bug benchmarks (the reason for Phase 3's SWE-bench-Live) and for the gap when a smaller self-hosted model is used, as with our vLLM backbone.

---

### C13 — Large Language Model-Based Agents for Software Engineering: A Survey (arXiv 2409.02977v2, Dec 2025)

**In one sentence:** This is the arXiv preprint of **C1** (same authors, same 124 papers, same structure). Cite C1, the ACM TOSEM version, instead.

**What it is / what they did:** A two-column arXiv version of the same survey. A spot check found the same sections as C1: the fault-localization table (AgentFL, AutoFL), "Common Failure Causes" in debugging, the 46.7% efficiency-reporting figure, Research Opportunities and Threats to Validity (§7.2).

**Key findings:** Same as C1. See C1.md.

**Limitations / future work (authors'):** Same as C1 (§6, §7.2).

**Why it matters to us:** None beyond C1. Use it only if the arXiv link is needed. Cite the journal version (C1) in the report.

---

### C14 — Towards a Science of Scaling Agent Systems (arXiv preprint 2512.08296v3, 8 Apr 2026; Google Research / Google DeepMind / MIT)

**This is the arXiv preprint of A2.** A2 was published in *Nature Machine Intelligence* (24 July 2026) under a new title, "Capable language models can outgrow the benefits of collaboration". Same authors, same 260-configuration study. **Cite A2, not this.** Use C14 only to see how the claims changed.

**In one sentence:** Same study as A2: 5 architectures (single agent, and four multi-agent types: Independent, Centralized, Decentralized/debate, Hybrid) × 9 models × 6 agentic benchmarks, with prompts, tools and token budget held fixed. It concludes that coordination stops helping once a single agent is above ~45%.

**What changed between preprint and published version (our comparison with A2):**
- **Framing got weaker.** The preprint title and text promise "quantitative scaling principles" and "the first quantitative criterion" (§4.3). The published abstract calls the ~45% threshold a "practical selection rule rather than a universal scaling principle".
- **The ~45% threshold was overclaimed in the preprint.** The threshold comes from the baseline × agent-count interaction (β = −0.236, p = 0.004, Table 4). But the preprint's own Table 14 shows this term is **not** significant under cluster-robust inference (robust p = 0.105), nor after Holm correction (p = 0.084, Table 15). Cluster-robust inference accounts for results within the same benchmark being correlated. The term that does survive is the single-agent baseline main effect (robust p = 0.004). Even so, the preprint conclusion (§6) says the threshold is "confirmed" at p = 0.004. A2 separates the two.
- **SWE-bench numbers differ.** Preprint: single agent 0.522; hybrid −2.1%, centralized −3.1%, decentralized/debate −5.4% (0.494), independent −14.9% (§4.2). A2: 0.488; −1.3%, −2.6%, −6.4% (0.456), −12.8%. The cause, from our own arithmetic: the preprint's Table 16 includes **Gemini-3 Flash** (a held-out model) among the SWE-bench rows, even though the text says 8 models. Averaging Table 16 with it gives exactly 0.522 / 0.494; without it, 0.4875 / 0.456, which matches A2.
- The overall mean multi-agent gain is −0.3% in the preprint vs 0.0% in A2 (same CI, −58.7% to +77.2%). Terminal-Bench is described as 86 tasks here and 89 in A2.
- The tool-coordination effect (β = −0.096) is highlighted in the preprint's abstract and introduction, but it also fails cluster-robust testing (robust p = 0.205, Table 14).

**Limitations / future work (authors', §5):** The same seven items as A2: at most 9 agents; limited mixing of different models (13 BrowseComp-Plus configurations); prompts not tuned per model; only six benchmarks; n = 20 for SWE-bench and Terminal-Bench, with about ±20-point confidence intervals; cost of token-based communication; only 6 benchmark clusters for the statistics. Future work also matches A2.

**Why it matters to us:** Only to cite A2 correctly and avoid quoting preprint numbers. Use A2's SWE-bench figures (0.488 vs 0.456). Describe the 45% rule as a heuristic, not a statistically confirmed law. Table 16 (per-model SWE-bench results with CIs) is still a handy look-up for the noise level at n = 20.

---

## 7. D — Cross-domain examples (for one point only)

### D1 — A Multi-Agent and synergistic Knowledge Graph retrieval-augmented generation framework for intelligent maintenance (MAKG) (Journal of Manufacturing Systems, 2026)
**In one sentence:** A pipeline of four LLM "agents" (split the query, retrieve KG subgraphs + text, filter, self-reflect) plus a fine-tuned embedding model answers industrial-robot fault questions with 90.1% "reasoning accuracy".

**What it is / what they did:** They build fault knowledge graphs from company records (KACKG: 6,217 triples, Table A.2) and fine-tune a small embedding model (12M parameters) on ~4,000 LLM-generated QA pairs (§4.2). The "agents" are fixed pipeline stages, not debaters. The backbone is DeepSeek-v2 16B. Test set: their own IFD-QA, **210 questions** (Table A.1).

**Key findings:**
- Fine-tuned embeddings raise Hit Rate@10 from 0.7834 to 0.9268 (Table 1).
- Removing the KACKG graph drops accuracy from 90.1% to 80.08%, the largest drop in the ablation (§5.1).
- The reflection agent adds +5.9% diagnosis accuracy (§4.4.2). The average answer takes 9.3 s.
- Beats Naive RAG, HyDE, GraphRAG, LightRAG and GPT-4o (Figs. 6–8, charts only).

**Limitations / future work (authors', §5.2):**
- It is slow because agents run one after another. Plan: run them in parallel and cache subgraphs (target 5–6 s).
- It handles text only. Plan: add images, vibration data and video.
- Grounding may miss fault types never seen before. Plan: balance grounding with new hypotheses.
- Deployment is hard. Plan: edge computing, incremental KG updates, temporal GNNs, and confidence scores that route doubtful cases to humans.
- An LLM judge may hallucinate and skew the scores.

**Our own caveats:** The test set is small and private, and most results are shown only as charts. No compute matching. The GPT-4o baselines use a different model. The abstract mentions a public dataset, but it has no results.

**Why it matters to us:** Background only. The graph mattered more than any single agent, which supports measuring the graph's reachability ceiling in Phase 1.

---

### D2 — Agentic Graph-RAG: A Multi-Agent Framework for Robust, Decomposed Multi-Hop Reasoning (ICCC 2025, IEEE)
**In one sentence:** A Planner, a Graph Navigator, a Corpus Retriever and a Synthesizer-Verifier work through a shared "blackboard" (a shared state that all agents read and write) instead of chatting, to answer multi-hop questions over Wikidata + Wikipedia.

**What it is / what they did:** The Planner splits the question into sub-questions. For each one, the Graph Navigator queries the KG and the Corpus Retriever searches the text. The Verifier turns the text into triples and compares them with the KG triples. It sorts facts into supporting, contradictory and novel, and it trusts the KG by default when the two disagree (§II-C). Agents may only READ and WRITE the blackboard. They never talk to each other directly (Algorithm 2).

**Key findings:**
- 66.5 EM (exact match) on HotpotQA and 75.8% accuracy on PopQA long-tail (§III-B). They report 94.2% faithfulness in a manual check of 500 samples (abstract).
- Ablation (Fig. 3): text-only drops 10.6 points on PopQA, KG-only drops 7.2 on HotpotQA, and a single-agent version drops the most on all datasets.

**Limitations / future work (authors'):** None stated. The paper has no limitations or future-work section.

**Our own caveats:** The backbone LLM is never named, and test-set sizes are not given. Most numbers exist only in bar charts. The baselines are "CoRAG-like" and "RefKG-like" re-implementations, and their compute is not reported. The single-agent ablation also removes planning and verification, so it cannot show that "multi-agent" is the cause. There are no variance or significance tests.

**Why it matters to us:** The blackboard idea (write checkable facts to shared state and settle KG-vs-text conflicts against the KG) is a design reference for Phase 2 graph-grounded debate. Its evidence is weak, though, so cite it for the idea, not the numbers.

---

### D3 — Agentic RAG for Software Testing with Hybrid Vector-Graph and Multi-Agent Orchestration (ICoDSE 2025, IEEE; Apple authors)
**In one sentence:** An industry report: five specialised agents plus a vector database and a TigerGraph graph (15+ edge types such as Validates, Depends-on, Impacts) generate test plans and test cases for an SAP S/4HANA migration.

**What it is / what they did:** They add components in four stages: basic RAG → vector search → hybrid vector-graph → full multi-agent (§II-D). Mistral 7B handles simple cases and Gemini Pro handles complex logic (§III-C). They evaluate on 5,000 synthetic test scenarios and an enterprise SAP set (§IV-A). The enterprise set is given as 1,000 cases there but 25,000 cases in §III-G.

**Key findings:**
- "Accuracy" rises 65.2% → 78.4% → 87.1% → 94.8% across the four stages (§IV-B, Fig. 3).
- Test plans: 94.8% vs 78% for the manual baseline. Test cases: 92.3% accuracy, 97% traceability coverage.
- Business claims: 85% less authoring time (240 → 36 h per phase), 35% cost savings, go-live 6 months earlier, 92% fewer production defects (§IV-C).
- Ablation (Table II): removing multi-agent orchestration costs 12.3%, hybrid vector-graph 15.7%, contextualisation 18.2%, traceability 8.9%.

**Limitations / future work (authors', §V-B/C):**
- Only covers Employee Systems, Finance and SAP. Other domains need more data.
- The knowledge base needs ongoing upkeep.
- Enterprise integration needs specialist expertise.
- Future: automatic KB maintenance, reinforcement learning from test-execution feedback, and multimodal inputs (UI mockups, audio/video, code repositories).

**Our own caveats:** "Accuracy" is never defined, and neither is who judged it. There is no public data, no named baseline systems and no variance. The dataset sizes are inconsistent. Mixed models (Mistral/Gemini) mean nothing is compute-matched. Treat the numbers as anecdotal.

**Why it matters to us:** Background only. It shows graph + agents used in software engineering, but it gives no evidence we can rely on.

---

### D4 — MedRAG-Agent: Medical Query Resolution By Employing A Multi-Agent, Knowledge Graph-Enhanced RAG-Based AI Framework (GCAT 2025, IEEE)
**In one sentence:** Four sequential agents (Query Decomposer, KG Navigator, Document Retriever, Synthesizer-Verifier) answer medical questions over a MedlinePlus + PubMed knowledge base, and the authors claim 78.5% accuracy on MedQA.

**What it is / what they did:** They build a biomedical KG by running NER (named-entity recognition) on text chunks and checking relations against UMLS. The KG Navigator narrows the dense-vector search, and the Verifier adds citations and flags unsupported claims (§III). The agents are built in LangChain on "GPT-4o or Claude 3.5 Sonnet" (§III-C). They compare with Vanilla RAG, i-MedRAG and KG-RAG on MedQA via MIRAGE.

**Key findings:**
- Accuracy 4.30/5 vs 3.70 for Vanilla RAG, and faithfulness 95.2% vs 82.5% (Table I).
- Ablation (Table II): removing the KG Navigator gives the biggest accuracy drop (4.30 → 3.85). Removing the Verifier drops faithfulness 95.2 → 85.9.

**Limitations / future work (authors'):** There is no limitations section. Future work (§VI): multimodal inputs (images, lab results, genomics), real-time KG updates, EHR integration, and clinical studies with physicians.

**Our own caveats:** The numbers do not add up. MedQA is multiple choice, yet accuracy is on a 1–5 scale. 4.30/5 is 86%, not the 78.5% claimed. 4.30 vs 3.70 is a 16% relative gain, not "12%". The backbone ("GPT-4o or Claude") and the test-set size are unclear. The retrieval model is also called "MedRAG-Agent". There is no variance, no compute matching and no limitations. We would not cite it for evidence.

**Why it matters to us:** Background only: another "KG navigator + verifier" agent pipeline. Its weak evaluation is a useful counter-example for why Phase 1 needs matched compute.

---

### D5 — Multi-Agent OSINT Architecture with Graph RAG Integration and Hierarchical Bloom-Filter Deduplication (INISTA 2025, IEEE)
**In one sentence:** A software-architecture paper that redesigns an OSINT (open-source intelligence) pipeline. One "mega-agent" becomes several micro-agents, a single graph database holds both the KG and the vectors (GraphRAG), and a Bloom filter checks for duplicate URLs.

**What it is / what they did:** This is a fourth design iteration using ADD/ATAM (formal methods for making and reviewing architecture decisions). A supervisor agent calls stance-detection, NER, contradiction-detection, ontology and report agents. These agents write to Neo4j, which stores both triples and HNSW vector indexes (§III-B). The only experiment tests URL lookups on 1M, 2M and 3M URLs against 5M indexed records (§IV-A).

**Key findings:**
- For 3M URLs, lookups took 3,477 s with RediSearch vs 0.305 s with the Bloom filter (Table I). That is about 10,000× faster. The abstract says "10000%", which would be only 100×.
- ATAM reviewers reclassified all three earlier risk scenarios (accuracy, latency, memory) as "non-risk" (§IV-B).

**Limitations / future work (authors'):** There is no limitations section. Future work (§V): report throughput, run LLM experiments, and compare RAG vs GraphRAG.

**Our own caveats:** The multi-agent and GraphRAG parts are **never measured**. The "non-risk" verdicts rest on reviewers' judgement and on citations to other papers. Only the Bloom-filter lookup has numbers, and that is a standard data-structure result. There are no baselines, no LLM results and no repeated runs.

**Why it matters to us:** Almost none. It is an example of "multi-agent GraphRAG" claims made without any accuracy evaluation. Background only.

---

### D6 — Improved multi-agent knowledge sharing system using knowledge graphs for news bias detection and fact-checking (Neural Computing and Applications, 2026)
**In one sentence:** Fact-checker and bias-detector agents share a Neo4j news KG as memory. With Claude 3.5 Sonnet, this beats LLM-only and RAG baselines on political bias detection and fact-checking.

**What it is / what they did:** The KG is built from NewsAPI articles from 20 outlets. The bias agent finds the most structurally similar KG article and passes that article's bias label to the LLM as a clue (§3.3). They test on 214 MBFC claims (170 False / 40 True / 4 Misleading) and **45** held-out articles labelled by their outlet's AllSides rating (§4.3.1). They test significance with McNemar tests and bootstrap CIs.

**Key findings (Tables 3–5):**
- Bias weighted F1: RAG 0.287, LLM-only 0.713, LLM+KG 0.901 (p<0.01 vs LLM-only).
- Fact-check weighted F1: 0.660 / 0.721 / 0.794. Recall on True claims is only 0.25 even for the best system.

**Limitations / future work (authors', §3.8, §6.3, §8):**
- Graph extraction is noisy when too loose and loses context when too tight. Long articles overflow the context window (no chunking).
- They lost AWS access, so the RAG baseline uses Mistral-7B while the others use Claude. Future work should use one model.
- Minority classes are weak (try SMOTE). New stories are poorly covered. Test sets are small (they want 1,000+ per task).
- The KG is costly to maintain.
- Future: more agents that write to the KG, embeddings in the KG, time-aware weighting, new specialist agents, and deployment and ethics work.

**Our own caveats:** The bias labels are *outlet* labels, and the KG uses the same outlets, so passing the neighbour's bias label may partly leak the answer. There is no single-agent + KG arm, so "multi-agent" is never isolated. The RAG gap is confounded by the different model.

**Why it matters to us:** It is a clear example of a model-mismatch confound. That is what our Phase 1 same-model, compute-matched 2×2 is designed to avoid.

## 8. Not yet reviewed

- **The SWE-Bench Illusion** (2025) — evidence that models memorise SWE-bench. Pairs with A8.
- **Debate or Vote** (arXiv 2508.17536) — whether debate beats plain voting.
- **CoSIL** (arXiv 2503.22424) — a second fallback platform.
- Lower priority: OrcaLoca, KGCompass, Prometheus (competing systems); Multi-SWE-bench (only if
  Phase 3 goes beyond Python).

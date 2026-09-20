# Literature summary — the gist of each paper

Plain-language summaries of all 41 papers, in reading order (A1, A2 … match the PDF names in
`papers/`). Each paper gets three lines: what it is, what they found, and why it matters to us.
For the detailed technical notes used when writing the report, see `notes/literature.md`.

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

## 3. A — Read fully

### A1 · SWE-Debate (ICSE 2026)
**What it is:** The system we study. It builds a map of the code, follows it to make about 20
candidate "trails" from the bug report to possibly-buggy code, then five copies of the same AI
vote on the best trail and argue over a fix plan before a separate search step writes the fix.
**What they found:** Best open-source results at the time: 41.4% of bugs fixed on SWE-bench
Verified, and 81.67% right file on first guess on SWE-bench Lite. Switching debate off dropped
fixes to 37.2%; switching off the multiple trails dropped them to 31.4%.
**Why it matters to us:** Every number is a single run with no cost reported, and removing
debate also removed a lot of thinking. The "three-round debate" is really two rounds plus one
judge. The released code doesn't run as-is.

### A2 · Capable language models can outgrow the benefits of collaboration (Nature Machine Intelligence 2026)
**What it is:** A large controlled experiment — 260 setups, 6 benchmarks, 3 model families —
comparing one agent with several team designs, all with the same budget, prompts and tools.
**What they found:** Whether teamwork helps depends on how good a single agent already is.
Above about 45% success, adding agents rarely helps. Teams cost 58% to 515% more tokens. On
SWE-bench every team did slightly worse than one agent, but that test used only 20 bugs.
**Why it matters to us:** The main prediction we test: at file-finding (~80% accuracy), debate
should add little. C14 is the same study's preprint.

### A3 · When and Why Does Multi-Agent Debate Fail and Does It Really Underperform? (arXiv 2025)
**What it is:** Explains, with game theory, why debate often loses to one AI. Splits debate into
*competitive* (agents try to win) and *consensus-seeking* (agents try to agree).
**What they found:** Both fail through "debate hacking": competitive agents mislead to win;
consensus agents agree too early. Their fix, ColMAD, rewards agents for adding useful
information. It beats a single AI on the same budget — but only when the debaters are
*different* models. With the same model on both sides, it loses.
**Why it matters to us:** SWE-Debate is competitive *and* uses one model: both failure
conditions. This is the basis for Phase 2's backup option.

### A4 · Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets (Stanford, arXiv 2026)
**What it is:** Theory plus experiments on whether one AI beats a team when both get the same
thinking budget, on questions that need several reasoning steps.
**What they found:** One AI matched or beat every team design at almost every budget. The
reason: passing messages between agents loses information, while a single agent keeps
everything in view. Teams only caught up when the single AI's input was badly corrupted —
adding plain distracting material wasn't enough.
**Why it matters to us:** Our template for a fair, same-budget comparison. Its one exception is
why bug-finding is an interesting test: a repository is full of similar-looking files.

### A5 · A Multi-Agent Approach to Fault Localization via Graph-Based Retrieval and Reflexion — LLM4FL (arXiv 2025)
**What it is:** Three AI agents find buggy methods in Java projects: one reads the test
results, one navigates a call graph, one re-checks and re-ranks the answer.
**What they found:** Beats earlier AI bug-finders on 675 real Java bugs at about $0.05 per bug.
Removing graph navigation cuts top-1 accuracy by about 16%. But simply changing the order the
candidates were shown in swung accuracy by up to 22 points — more than any component.
**Why it matters to us:** Our closest cousin. Warning: we must show candidates in the same order
in every test, or ordering effects will look like map effects.

### A6 · LocAgent — Graph-Guided LLM Agents for Code Localization (arXiv 2025)
**What it is:** One AI agent finds bug locations by exploring a code map with three tools:
search for a name, walk the map, open the code.
**What they found:** 77.74% right file on first guess on SWE-bench Lite. A fine-tuned open 32B
model got similar accuracy at about 86% lower cost. Better bug-finding led to more bugs fixed.
**Why it matters to us:** Shows a map plus a single agent, with no debate, already works well.
Our fallback platform if SWE-Debate won't run, and a model for letting agents query the map.

### A7 · SWE-bench — Can Language Models Resolve Real-World GitHub Issues? (ICLR 2024)
**What it is:** The standard benchmark: 2,294 real bugs from 12 Python projects. A fix counts
only if the project's own tests pass.
**What they found:** At launch the best model fixed under 2% of bugs. Performance fell as more
code was stuffed into the AI's context.
**Why it matters to us:** Our dataset. It doesn't score file-finding itself, so we check the AI's
guess against the files the real fix changed. Our 75-bug set comes from its Verified subset.

### A8 · SWE-bench Goes Live! (Microsoft, arXiv 2025)
**What it is:** A fresh, automatically updated version: 1,319 bugs from GitHub issues opened
between Jan 2024 and Apr 2025, across 93 Python projects.
**What they found:** The best agent fixed 19.25% of these fresh bugs, versus 43.2% on the old
SWE-bench with identical settings — a sign agents are tuned to, or have memorised, the old
benchmark. Small single-file fixes succeed about half the time; fixes touching 7+ files never.
**Why it matters to us:** Our Phase 3 dataset. Use only bugs opened after our model's training
cutoff. The single-file vs multi-file split could measure "how many look-alike candidates"
for H4.

### A9 · Rethinking the Value of Multi-Agent Workflow — A Strong Single Agent Baseline (OneFlow, arXiv 2026)
**What it is:** Tests whether a "team" whose agents all use the same model is really a team, or
just one model talking to itself.
**What they found:** One model playing every role in a single conversation matched the team's
accuracy, at lower cost.
**Why it matters to us:** SWE-Debate's five agents are one model with different instructions, so
one agent may do the same job. Supports trying *different* models in Phase 2.

---

## 4. B — Method and results

### B1 · Improving Factuality and Reasoning in Language Models through Multiagent Debate (ICML 2024)
**What it is:** The original multi-agent debate paper: several copies of ChatGPT answer, read
each other's answers and update over a few rounds.
**What they found:** Big gains on maths and knowledge tests (GSM8K maths: 77% → 85%), growing
with more agents and rounds.
**Why it matters to us:** The ancestor of SWE-Debate's debate — but the single-AI comparison
never got the same budget. That's the gap later papers attack.

### B2 · When Does Multi-Agent Collaboration Help? An Entropy Perspective (arXiv 2026)
**What it is:** Tracks how uncertain each agent is during teamwork to predict when teams help.
**What they found:** A single agent beat the team in about 43% of cases. Success is mostly
decided in round one; extra rounds rarely help. Only about 6% of cases showed real improvement
from interaction; about 83% looked like agents copying each other.
**Why it matters to us:** Basis for "stop early if agents already agree", and for checking
whether SWE-Debate's agents actually disagree.

### B3 · Multi-Agent Systems are Mixtures of Experts: Who Becomes an Influencer? (arXiv 2026)
**What it is:** Models how agents change each other's minds during discussion.
**What they found:** Teams beat single agents when the most *competent* agent gets the most
influence. In practice the most *confident* agent does, and confidence isn't competence — then
the advantage disappears.
**Why it matters to us:** A reason to weight agents by checkable evidence from the map, not by
how sure they sound.

### B4 · Why Do Multi-Agent LLM Systems Fail? — MAST (NeurIPS 2025)
**What it is:** Studied 1,600+ logs from 7 multi-agent frameworks and classified what went wrong.
**What they found:** 14 failure types in 3 groups: poor system design (44%), agents out of sync
with each other (32%), weak checking of results (24%). Gains over single agents were often small.
**Why it matters to us:** A ready-made checklist for labelling why our debate runs fail.

### B5 · Reasoning in Token Economies — Budget-Aware Evaluation of LLM Reasoning Strategies (EMNLP 2024)
**What it is:** Re-tests fancy reasoning methods (debate, self-reflection, tree search) with
every method given the same budget.
**What they found:** Plain majority voting matched or beat the fancy methods almost everywhere.
Debate can even get worse with more budget, because the agents' answers grow too similar.
**Why it matters to us:** The template for what we do — a fair, same-budget re-test — applied to
general reasoning instead of bug-finding.

### B6 · More Agents Is All You Need (TMLR 2024)
**What it is:** Simply sample many answers from the same model and take a vote.
**What they found:** Accuracy keeps rising with more samples. Adding debate on top sometimes
made things worse.
**Why it matters to us:** Justifies our cheap majority-vote comparison: much of debate's gain may
just be voting.

### B7 · Agentless — Demystifying LLM-based Software Engineering Agents (arXiv 2024)
**What it is:** No agent at all — a fixed three-step pipeline: narrow down files, then
functions, then lines; generate fixes; test them.
**What they found:** Fixed 32% of SWE-bench Lite bugs at $0.70 each, better and cheaper than
most agents at the time. Reports the cost of every step.
**Why it matters to us:** Evidence that simple can beat complex, and a model for reporting cost
step by step.

### B8 · SWE-Search — Enhancing Software Agents with Monte Carlo Tree Search (ICLR 2025)
**What it is:** Adds a game-style search tree to a coding agent to explore possible fixes, with
a debate among agents to pick the final patch.
**What they found:** About 23% relative improvement over the same agent without search — at 5 to
14 times the cost.
**Why it matters to us:** SWE-Debate is built on this code. Its fixing stage is the part we leave
out: it's the expensive bit and needs test infrastructure.

### B9 · Large Language Models Cannot Self-Correct Reasoning Yet (ICLR 2024)
**What it is:** Tests whether AIs improve answers by criticising themselves without outside
feedback, and re-runs the original debate on a fair budget.
**What they found:** Self-correction usually made answers *worse*. Debate lost to plain majority
voting at the same number of answers (83.0% vs 88.2% with 9 answers on GSM8K).
**Why it matters to us:** The earliest fair test of debate. And its lesson — AIs need an outside
check to fix mistakes — is the idea behind graph-grounded debate: the code map is that check.

### B10 · Advances and Frontiers of LLM-based Issue Resolution in Software Engineering (survey, arXiv 2026)
**What it is:** Survey of 175 papers on AI bug-fixing: datasets, methods, open problems.
**What they found:** Names "ignoring cost" as a top open problem, and groups SWE-Debate with
other map-based bug finders.
**Why it matters to us:** Map of the field, outside support for our cost argument, and a list of
other datasets.

### B11 · Inside the Scaffold — A Source-Code Taxonomy of Coding Agent Architectures (arXiv 2026)
**What it is:** Reads the source code of 13 coding agents and classifies how they're built.
**What they found:** Reports no scores on purpose: benchmark scores mix up the agent's design,
the model and the settings, so they can't say which design is better.
**Why it matters to us:** Close to a direct statement of our premise, and support for treating
"map" and "debate" as separate parts we can test one against the other.

### B12 · SWE-Effi — Re-Evaluating Software AI Agent Effectiveness Under Resource Constraints (arXiv 2025)
**What it is:** Re-ranks 15 agent-plus-model combinations by accuracy per unit of cost (tokens,
money, time).
**What they found:** Efficiency depends on the pairing of agent and model. Failed attempts are
the expensive ones — over 4 times the tokens in one case.
**Why it matters to us:** The closest prior work to our cost plots. The report needs a paragraph
on the difference: they compare whole systems; we test parts inside one system on a fixed budget.

---

## 5. C — Skim and cite

- **C1 · LLM-Based Agents for Software Engineering: A Survey (TOSEM 2026)** — Survey of 124
  papers on AI agents for software tasks. Only 46.7% report any cost or efficiency data.
  *For us:* the statistic that shows missing cost reporting is field-wide.
- **C2 · LLMs for Software Engineering: A Systematic Literature Review (TOSEM 2024)** — Review of
  395 papers up to Jan 2024. Bug localization is a tiny slice, treated as simple classification.
  *For us:* general background only.
- **C3 · AutoFL — LLM-Based Explainable Fault Localization (FSE 2024)** — One AI with a few
  repository tools names the buggy method from one failing test and explains why; reports time
  per bug. *For us:* a cost-aware single-agent bug-finding baseline.
- **C4 · LLMAO — LLMs for Test-Free Fault Localization (ICSE 2024)** — Trains a small add-on on a
  frozen code model to flag buggy lines without running tests. *For us:* a lightweight contrast;
  background only.
- **C5 · BugLocator — Where Should the Bugs Be Fixed? (ICSE 2012)** — Pre-AI method: match the bug
  report's words to source files, boosted by similar past bugs. *For us:* where the history of
  bug localization starts.
- **C6 · BLUiR — Improving Bug Localization using Structured Information Retrieval (ASE 2013)** —
  Like BugLocator, but searches class names, method names and comments separately. Top-1 file
  accuracy of about 24–55% depending on the project. *For us:* a pre-AI baseline number and the
  "text → structure → map → AI agents" storyline.
- **C7 · MacNet — Scaling LLM-based Multi-Agent Collaboration (ICLR 2025)** — Arranges up to 1,000+
  agents in networks and studies scaling; giving one agent more calls instead helped little.
  *For us:* background on team structure.
- **C8 · Graph Retrieval-Augmented Generation: A Survey (ACM TOIS)** — The main GraphRAG survey.
  Almost all its graphs are built by an AI reading text, which costs a lot. *For us:* cite for
  GraphRAG background, and to point out our map comes from code analysis and costs nothing.
- **C9 · From Local to Global — Microsoft GraphRAG (arXiv 2024)** — An AI reads a document
  collection, builds a graph of people, things and relations, then summarises clusters to answer
  broad questions. *For us:* the "other" GraphRAG, to distinguish from ours.
- **C10 · Evaluation and Benchmarking of LLM Agents: A Survey (KDD 2025)** — A framework for
  evaluating AI agents; calls for cost-limited evaluation but doesn't do it. *For us:* weak
  general support.
- **C11 · A Comprehensive Survey on Benchmarks and Solutions in SE of LLM-Empowered Agentic
  Systems (arXiv 2025)** — Links 150+ papers to their benchmarks; says the field ignores the cost
  of agents coordinating. *For us:* background.
- **C12 · Software Testing With Large Language Models (IEEE TSE 2024)** — Review of 102 papers on
  AI for testing; none use debate or maps. *For us:* peripheral, one citation at most.
- **C13** — Earlier arXiv version of C1. Read C1.
- **C14** — Preprint of A2 (same study, same authors). Read A2.

---

## 6. D — Cross-domain (for one point only)

Six multi-agent + knowledge-graph systems from other fields. None uses debate. All of them test
parts one at a time, in a single run, with little or no cost reporting — useful only to show
that weak evaluation is common. Most come from smaller venues, so they support the point but
shouldn't carry it.

- **D1 · Industrial maintenance (J Manuf Syst 2026)** — Four agents plus two equipment knowledge
  graphs answer robot-fault questions; 90.1% on a private 210-question set.
- **D2 · Agentic Graph-RAG (IEEE ICCC 2025)** — Planner, graph and text agents for multi-step
  question answering; claims best scores on HotpotQA and similar sets.
- **D3 · Agentic RAG for software testing (IEEE ICoDSE 2025)** — Five agents write test plans for
  an SAP migration; claims 94.8% on private data, with "accuracy" never defined.
- **D4 · MedRAG-Agent (IEEE GCAT 2025)** — Four agents plus a medical knowledge graph for medical
  exam questions; 78.5% on MedQA.
- **D5 · Multi-agent OSINT (IEEE INISTA 2025)** — An intelligence-gathering pipeline; the only
  measured result is a faster duplicate filter, not the AI part.
- **D6 · News bias and fact-checking (Neural Comput Appl 2026)** — Agents share a news knowledge
  graph; strong scores, but the comparison system used a much smaller model.

---

## 7. Not yet reviewed

- **The SWE-Bench Illusion** (2025) — evidence that models memorise SWE-bench. Pairs with A8.
- **Debate or Vote** (arXiv 2508.17536) — whether debate beats plain voting.
- **CoSIL** (arXiv 2503.22424) — a second fallback platform.
- Lower priority: OrcaLoca, KGCompass, Prometheus (competing systems); Multi-SWE-bench (only if
  Phase 3 goes beyond Python).

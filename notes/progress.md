# Progress Log — FYP A3062

One entry per work session, newest at the top. Format:

## YYYY-MM-DD
Did:
Broke:
Next:

## 2026-09-19
Did: Project plan submitted 14 Sep. Plan discussion with A/P Chen: she read it as a
reproduction and suggested testing other datasets and modifying the debate, so the plan is now
three phases (diagnose, modify, validate) — see decisions.md and FYP_A3062_Project_Plan.md.
Renamed the 41 PDFs in papers/ to their titles with A/B/C/D reading-order labels
(notes/reading-order.md). Added a SWE-bench-Live entry to literature.md and wrote
notes/literature-summary.md. Found that "Agent Scaling Science" is the preprint of the Nature
MI paper (one study, not two), and that SWE-Debate's -4.2 debate effect is end-to-end Pass@1,
not localization — gap statement corrected in decisions.md. Updated CLAUDE.md.
Broke: No SWE-Debate run recorded yet. DeepSeek-V3-0324 is no longer served by DeepSeek, so
the backbone moves to a self-hosted open model (deviations.md). GPU access pending: MLDA
application first, at the supervisor's request.
Next: Get one SWE-Debate instance running end to end by 30 Sep, or switch to LocAgent/CoSIL.
Start the reachability measurement (no GPU needed). Confirm localization-only scope with
A/P Chen. Pick the backbone once GPU memory is known. Read A1-A9.

## 2026-09-13 (3)
Did: Reviewed the big 29-paper batch dropped in papers/, added a literature.md entry for
every one. This was the real haul — most of the project's actual reference list, not just
cross-domain flavor:
- SWE-Debate itself (arXiv:2507.23348), read in full against the earlier repo inspection.
  Confirmed exact ablation numbers (chains -10.0, edit plan -6.0, debate -4.2), confirmed the
  "3-round debate" is actually 2 agent rounds + 1 discriminator round, confirmed the 5 agents
  are one DeepSeek-V3-0324 model under different system prompts (paper's own words, Sec 6.2),
  confirmed zero cost reporting anywhere, confirmed the 75-instance subset is django+sympy+
  sphinx-doc (three repos, not two as previously assumed). Full discrepancy list written to
  deviations.md.
- Core comparators: LocAgent, Agentless, SWE-bench (the benchmark itself), SWE-Search (origin
  of the excluded MCTS repair stage), SWE-Effi (closest existing precedent to our own cost-
  accuracy-frontier deliverable — needs an explicit "how we differ" paragraph in the report).
- Multi-agent debate lineage: Du et al. (the original debate paper SWE-Debate's mechanism
  descends from), Huang et al. (earliest compute-matched critique of that exact mechanism),
  Cemri et al. MAST (14-failure-mode taxonomy, usable as an analysis tool for our own results).
- The three most load-bearing methodology papers: Tran & Kiela (DPI-based proof + the
  boundary-condition H4 is built on — important caveat: their distractor-injection condition,
  closest analogue to "candidate density," was their WEAKEST crossover lever, so H4 may need a
  stronger operationalization than plain additive distractors), "Inside the Scaffold" (near-
  verbatim precedent for our confounded-comparisons premise), ColMAD (shows debate CAN beat
  compute-matched single-agent under incentive redesign, but only with heterogeneous backbones
  — flagged as a threat to validity against our single-backbone decision, logged in
  decisions.md).
- GraphRAG terminology: Peng et al.'s survey and Microsoft's original GraphRAG paper — critical
  finding that "GraphRAG" in the literature usually means LLM-extracted graphs (real inference
  cost to build), NOT our static-analysis AST graph (zero LLM cost to build). Report needs to
  disambiguate this explicitly on first use of the term.
- Closest kin found: LLM4FL (Defects4J fault localization, graph-nav + Reflexion, leave-one-out
  ablation, actually reports cost) and Agent Scaling Science / MAS Capability Saturation
  (Nature MI) — the single most methodologically relevant paper in the whole batch, a large-
  scale compute-matched 5-architecture study whose own SWE-bench-Verified arm shows every
  multi-agent architecture losing to single-agent under matched budget.
- Several SE-agent and issue-resolution surveys (LLM Agents for SE, LLM-Agent-SE, LLM-based
  Issue Resolution) that independently name SWE-Debate and confirm "no efficiency-aware
  evaluation" as a recognized field-wide gap.
- Historical grounding: BugLocator and BLUiR, pre-LLM IR-based bug localization — gives a
  concrete numeric anchor (~24-55% Top-1 depending on project) for what "baseline" localization
  accuracy meant before graphs/agents existed.
- Several more compute-matching-adjacent papers (MacNet, Agent Forest, Reasoning in Token
  Economies, Entropy Perspective on MAS, FJ-MoE, OneFlow) — all converging on the same pattern:
  debate's advantage shrinks or inverts once properly budget-matched, in domains from GSM8K to
  general agentic benchmarks.
Broke: Nothing — investigation only.
Next: See (4) below — the last 5 papers are now done too. Check with supervisor whether CoSIL,
OrcaLoca, KGCompass, and Prometheus (named as fallback/competitor systems in CLAUDE.md but not
yet in papers/) still need dedicated review, or whether the current set already covers what's
needed for the report's Related Work.

## 2026-09-13 (4)
Did: Reviewed the last 5 papers (Software Testing LLM Survey, LLMAO, AutoFL, Agent4SE Survey,
LLM4SE SLR). Literature review is now at 40 unique papers reviewed, 40 entries in
literature.md (41 PDFs in papers/, one is an accidental duplicate of 2601.12307v1). Two
flagged as uncertain/low relevance for student review (Software Testing LLM Survey — no
multi-agent or graph-grounded FL in its 102-paper corpus at all; LLM4SE SLR — corpus cutoff
predates the entire multi-agent-debate-for-FL literature, near-zero overlap). One genuinely
new load-bearing finding: Agent4SE Survey (ACM TOSEM, 124-paper survey of LLM-agents-for-SE)
reports that only 46.7% of surveyed agentic SE papers report ANY cost/efficiency data — the
best available field-scale statistic backing the "no cost reporting" half of A3062's
motivation, better than any single-paper anecdote. AutoFL (arXiv:2308.05487) and LLMAO
(arXiv:2310.01726) add two more single-agent, non-graph fault-localization baselines that
trade compute for accuracy without ever compute-matching against a stronger single model —
useful contrast points for describing SWE-Debate's heavier design.
Broke: Nothing.
Next: Literature review is effectively saturated for now. Good time to pause and discuss
direction in Chat — particularly: (a) whether to chase down CoSIL/OrcaLoca/KGCompass/
Prometheus specifically, (b) how to operationalize "candidate density" for H4 given Tran &
Kiela's own distractor-injection result was their weakest crossover lever (see literature.md),
(c) whether/how to address the single-backbone-debate threat to validity flagged from ColMAD
(see decisions.md). All findings pushed to GitHub once the student confirms.

## 2026-09-13 (2)
Did: Reviewed 6 papers dropped in papers/ (multi-agent + graph-RAG systems in industrial
maintenance, multi-hop QA, software testing, medical QA, OSINT, and news bias/fact-checking)
and added a literature.md entry for each. None are code/SWE-bench-adjacent competitors to
LocAgent/CoSIL/KGCompass/SWE-Debate; all six serve mainly as cross-domain evidence for the
report's Motivation section — every one has an ablation that is one-factor-at-a-time (never
factorial), not compute-matched, single-run with no seeds/CIs, and reports little-to-no real
inference cost (tokens/latency/$), even when they narrate cost/ROI qualitatively. Flagged the
news bias/fact-checking paper (KG-News-Agents) as borderline-relevant given domain mismatch —
worth a supervisor call on whether to keep it in the review at all.
Broke: Nothing.
Next: Decide with supervisor whether KG-News-Agents stays in the lit review. Continue
literature review toward the actual competitor set (LocAgent, CoSIL, OrcaLoca, KGCompass,
Prometheus, the budget-controlled multi-agent-debate papers) once more of those PDFs are on
hand.

## 2026-09-13
Did: Scaffolded repo directories (notes/, papers/, report/, ablation/{configs,harness,results}),
.gitignore, and notes/{literature,deviations,decisions}.md. Recorded the four founding decisions
in decisions.md. Cloned https://github.com/YerbaPage/SWE-Debate into swe-debate/ and read it
read-only (no installs, no runs) to answer task 6's questions. Findings below.
Broke: Nothing run yet — investigation only.
Next: Get supervisor sign-off on the localization-only scope deviation (per decisions.md). Then
set up the environment (Python 3.12 venv, pip install, .env) and fix the two blockers below
before attempting a first instance end to end.

### SWE-Debate repo findings (task 6)

**Python version and dependency constraints**
- README states "Python 3.12+" but nothing in the repo actually enforces this — no
  `python_requires`, no `.python-version`, no `pyproject.toml`.
- Dependencies are pinned as a flat pip freeze in `localization/requirements.txt` (163 packages,
  exact `==` versions — e.g. `openai==1.54.3`, `litellm==1.52.1`, `torch==2.5.1`, `faiss-cpu==1.8.0`,
  `llama-index-core==0.11.22`). Install path per README: `pip install -r localization/requirements.txt`
  then `pip install moatless-tree-search` separately.
- **Contradiction to flag**: a `poetry.lock` sits at repo root (Poetry 1.8.4 format, packages
  pinned to Python `>=3.8`/`>=3.9` per-package) but there is **no `pyproject.toml`** anywhere in
  the repo. The lock file is orphaned — `poetry install` cannot work without its pyproject. Treat
  `localization/requirements.txt` as the only real source of truth for the environment.
- `requirements.txt` also pulls the full CUDA stack (`nvidia-cublas-cu12`, `torch==2.5.1`, etc.)
  even though the vector index uses `faiss-cpu`, not `faiss-gpu`. Worth testing whether a
  CPU-only torch install works instead, given decisions.md already rules out a GPU allocation.

**API keys / external services and what each is for**
From `.env.example`:
- `DEEPSEEK_API_KEY` — the DeepSeek-V3-0324 backbone calls (both the localization pipeline and
  moatless's own completion layer).
- `ANTHROPIC_API_KEY` / `ANTHROPIC_API_BASE` — present but unused in our scope (backbone is fixed
  to DeepSeek per decisions.md).
- `OPENAI_API_BASE`, `CUSTOM_LLM_API_BASE` / `CUSTOM_LLM_API_KEY` — generic OpenAI-format endpoint
  overrides (DeepSeek is called through an OpenAI-compatible client).
- `VOYAGE_API_KEY` — embedding provider for the code index / semantic search (`CodeIndex`,
  `SemanticSearch` action) and for `LocalizationChainEmbedding`'s diverse-chain selection (stage 4
  of the pipeline).
- `INDEX_STORE_DIR`, `REPO_DIR`, `GRAPH_INDEX_DIR` — local paths, not services, but required: code
  index cache, cloned target repos, and dependency-graph cache respectively. No key needed but
  must be set or things default to `/tmp/repos` and `tmp/index_store` (cwd-relative).
- No GitHub token is required to clone target repos — see dataset footprint below.

**Dataset: how obtained, disk footprint**
- `datasets/*.json` in the repo are instance metadata/ID lists only (a few KB to ~800KB each,
  e.g. `resolved_submissions.json` at 784K) — not the actual repositories.
- `moatless/benchmark/swebench_{lite,verified}_all_evaluations.json` (4.7MB and 9.7MB,
  already present in the clone) hold the per-instance SWE-bench metadata (`get_moatless_instance`
  reads these directly — no HuggingFace `datasets.load_dataset` call needed for this path,
  even though the `datasets==3.1.0` package is imported by a separate, unused `load_instances`
  helper in `moatless/benchmark/swebench/utils.py`).
- Actual code: `create_repository()` (`moatless/benchmark/swebench/utils.py:126`) clones each
  target repo from a pre-mirrored GitHub org, `swe-bench/<owner>__<repo>`, at the instance's
  `base_commit`, into `$REPO_DIR/swe-bench_<instance_id>` (default `/tmp/repos`). One shallow
  clone per instance (or reused across instances sharing a repo+commit).
- `utils/verified75.txt` — confirmed exactly 75 instance IDs (74 newline-terminated lines +
  1 unterminated last line; `wc -l` undercounts). This is the SWE-Bench-Verified-S subset
  CLAUDE.md refers to. At ~75 instances across a handful of repos (django, sympy, etc.), the
  ~5GB estimate in CLAUDE.md's Known Unknowns is plausible but not yet verified on disk.

**Where the debate stage is implemented**
Two separate, non-overlapping debate-like mechanisms exist — do not conflate them:
1. `moatless/debate.py` (`MultiAgentDebate`) + `moatless/discriminator.py`
   (`AgentDiscriminator`) — used only by the **MCTS search-tree** node selection
   (`workflow.py`'s patch-generation path). Out of scope per decisions.md (localization only).
2. `localization/entity_localization_pipeline.py`, class `EntityLocalizationPipeline`
   (single class, ~1900 lines) — **this is the debate that matters for the FYP**:
   - Stage 6, `_vote_on_chains` (line 1704) — 5 agents vote independently (threaded,
     `max_workers=3`) on which candidate localization chain to select. This is the
     "chain-level competitive ranking" the project plan refers to.
   - Stage 7, `_generate_modification_plan` (line 1882) → `_conduct_first_round_analysis`
     (line 1960, independent per-agent analysis) → `_conduct_second_round_analysis`
     (labelled "# debate" in source) → `_conduct_final_discrimination` (labelled
     "# discriminator"). This is the "modification-plan refinement" debate.
   - **Round count is hardcoded at exactly 2 debate rounds + 1 final discrimination**, not a
     parameterised 1/2/3 like the project plan's nested round factor assumes. Generalising this
     into a configurable round count is fork work, not a config change.

**Where the dependency graph is constructed**
- `localization/dependency_graph/build_graph.py` — `build_graph(repo_path, ...)` (line 285) is
  the entry point; builds a `networkx` graph via a Python `ast.NodeVisitor` (`CodeAnalyzer`,
  line 120) walking the repo, resolving imports (`find_imports`, `resolve_module`) and call/
  inheritance edges (`analyze_invokes`, `analyze_init`). `batch_build_graph.py` runs this over
  many repos/instances.
- `localization/dependency_graph/traverse_graph.py` — `traverse_graph_structure` (line 242) and
  `RepoEntitySearcher` / `RepoDependencySearcher` (lines 49, 198) do the actual multi-hop
  upstream/downstream traversal from an initial entity, which is what feeds
  `EntityLocalizationPipeline`'s chain generation (stage 3).

**Whether token usage is already logged**
Mixed — this is the most important finding for the "token accounting first" convention in
CLAUDE.md:
- Moatless's own completion layer (`moatless/completion/model.py`, `moatless/node.py`,
  `moatless/benchmark/report.py`, `moatless/benchmark/run_evaluation.py`) has full usage
  tracking already: `Usage` objects with `prompt_tokens`/`completion_tokens`/`cached_tokens`,
  aggregated per node and per run, plus cost via `instance.usage.completion_cost`. This covers
  the MCTS/patch-generation path (out of scope) and `moatless/debate.py`'s own
  `MultiAgentDebate.__call__`, which separately computes `prompt_tokens`/`completion_tokens`
  via `litellm.token_counter` on the serialized message text (an estimate, not real API-reported
  usage) at debate.py:124-128.
- **`localization/entity_localization_pipeline.py` — the debate/voting stage this project
  actually studies — has no token accounting at all.** `_call_llm_simple` (line 525) calls
  `self.client.chat.completions.create(...)` and returns only
  `response.choices[0].message.content`, discarding `response.usage` entirely. Every one of the
  7 pipeline stages calls through this method. This is the first thing to instrument — it lines
  up exactly with CLAUDE.md's "token accounting goes in before the first factorial pass."

**Blockers found (beyond "install nothing")**
1. **The pipeline will not run out of the box.** `EntityLocalizationPipeline.__init__`
   (line 519) hardcodes `self.client = OpenAI(base_url="", api_key="", timeout=60.0)` — it never
   reads `DEEPSEEK_API_KEY`/`OPENAI_API_BASE` from the environment despite `.env.example`
   defining them. Every `_call_llm_simple` call will fail authentication until this is wired to
   `os.getenv(...)`. This is a required fork change, not an install issue.
2. **`_call_llm_simple` also hardcodes `model="deepseek-v3"`** (line 539), not the
   `model_name` passed to `EntityLocalizationPipeline.__init__` (which defaults to
   `deepseek/deepseek-chat`, a litellm-style route string, and is never referenced inside
   `_call_llm_simple`). The two model-name strings look inconsistent; confirm which one is
   correct for whatever DeepSeek endpoint we point `OPENAI_API_BASE` at before trusting output.
3. **The "ambiguous testbed setup" line in CLAUDE.md's Known Unknowns is resolved**: it refers
   to `moatless/runtime/testbed.py`'s `TestbedEnvironment`, which wraps a separate `testbeds`
   SDK/package (`from testbeds.sdk import TestbedSDK`, not in `localization/requirements.txt`)
   used only for running tests inside Docker during patch **evaluation**
   (`moatless/benchmark/evaluation_runner.py`, `workflow.py`'s `use_testbed` flag). Nothing in
   `localization/` imports it. Confirms this dependency is cleanly excluded by the
   localization-only scope decision — no action needed.
4. Cache directory `self.cache_dir = "/entity_pipeline_cache"` (line 514, absolute path at
   filesystem root) will likely fail to create on a machine without root/write access there —
   check `_ensure_cache_dir_exists()`'s failure handling before a first run on the CPU node.

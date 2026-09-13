# Progress Log — FYP A3062

One entry per work session, newest at the top. Format:

## YYYY-MM-DD
Did:
Broke:
Next:

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

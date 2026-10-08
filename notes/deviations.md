# Deviations from Published SWE-Debate Setup — FYP A3062

Any deviation from the original SWE-Debate paper's setup, logged here as it is
made. These become threats-to-validity entries in the report.

Format:

## YYYY-MM-DD — <short title>
What changed:
Why:
Expected impact:

## 2026-09-13 — Paper-vs-code discrepancies found reading arXiv:2507.23348 against the clone

Found by reading the SWE-Debate paper in full and cross-checking against the earlier repo
inspection (see notes/progress.md 2026-09-13 entry). Not our deviations yet — these are
discrepancies WITHIN the published paper's own account, worth recording now so the report's
threats-to-validity section can cite them precisely rather than rediscovering them mid-write.

1. **"Three-round debate" oversells round 3.** Paper's own hyperparameter table (Appendix B,
   Table 5) sets `number_of_round: 3` and the prose repeatedly calls it a three-round debate,
   but only rounds 1-2 involve 5 parallel agents (round 1 independent, round 2 cross-agent
   refinement — labeled "# debate" in source). Round 3 collapses to ONE discriminator agent
   synthesizing the round-2 outputs, not a third round of 5-agent debate. Matches the code
   exactly (Stage 7: first_round -> second_round "debate" -> final_discrimination), so this is
   the paper's own framing being loose, not a code bug. When the FYP report describes "the
   published 3-round debate," it should say "2 rounds of parallel debate + 1 discriminator
   synthesis round" to avoid repeating the paper's overstatement.
2. **Chain-selection stage isn't iterative debate either.** Section 3.3 describes agents that
   "engage in competitive ranking" and "defend their chain preferences against alternatives,"
   but the actual prompt (Prompt 5, Chain Voting) is a single round of independent parallel
   votes with simple aggregation — no evidence agents see or respond to each other's votes.
   Matches code Stage 6 `_vote_on_chains`. Report should not describe chain selection as
   "debate" — it's a one-shot vote.
3. **Headline abstract/conclusion percentages don't match the in-text same-backbone deltas.**
   Abstract/Conclusion claim "6.7% improvement in issue resolution... 5.1% improvement in
   fault localization," but the same-backbone Table 1/Table 3 deltas are +2.6 pts (Pass@1)
   and +3.93 pts (Acc@1-File). The 6.7/5.1 figures likely come from different, unstated
   comparator rows (approx. match to Moatless Tools and KGCompass respectively, but not
   exact). Cite the in-text same-backbone deltas (2.6 / 3.93 pts), not the abstract's
   headline numbers, when describing "the paper's claimed improvement over baselines."
4. **SWE-Bench-Verified-S is three repos, not two.** Appendix A Table 4 lists the exact 75
   instance IDs: django (23), sympy (26), **sphinx-doc (26)** — not just django/sympy as
   assumed from CLAUDE.md's earlier framing. Confirmed to match `utils/verified75.txt`
   (75 lines) in the repo. Update any report language describing the subset's composition.
5. **Paper corroborates the code's cost-blindness at the documentation level.** Exhaustively
   checked every table/figure/caption — zero token counts, latency, or dollar cost anywhere,
   including Appendix B's own hyperparameter table (lists `number_of_agents`,
   `number_of_round`, temperatures, MCTS params — no cost fields at all). Not a
   contradiction with the code finding, but confirmation the omission is paper-wide, not an
   implementation oversight the authors just forgot to surface.
6. **The paper's "threats to validity" concession is about generalizability, not ablation
   rigor.** Section 7's budget/scope concession ("restricted to... DeepSeek-V3-0324 and a
   subset of SWE-Bench-Verified... limits generalizability") is about model/dataset coverage,
   NOT an admission that the ablation lacks compute-matching, factorial design, or seeds/CIs.
   The paper never names that specific weakness anywhere. Report should not cite Section 7 as
   if the authors already conceded the exact gap this FYP is built around — they didn't;
   that gap is this project's own diagnosis, worth stating as such rather than borrowing
   false authority from the paper's unrelated concession.
7. **Agent differentiation is confirmed, verbatim.** Section 4.5: "the multi-agent debate
   employs official DeepSeek-V3-0324 with different system prompts to simulate diverse
   reasoning perspectives." Section 6.2 (Limitations): "Our multi-agent debate currently
   relies on a single model with different prompts to simulate diverse reasoning
   perspectives... While our specialized prompts enforce distinct analytical viewpoints and
   our ablation study confirms significant performance gains from the debate mechanism,
   integrating multiple heterogeneous models... could further enhance the diversity." This
   confirms CLAUDE.md's characterization exactly and can be quoted directly in the report.
   **But the released code does not do this (2026-10-01):** every agent gets an identical
   prompt. See the 2026-10-01 entry "Agents are not differentiated by prompt in the code".

## 2026-09-19 — Backbone: DeepSeek-V3-0324 is no longer available from DeepSeek
What changed: The source paper ran on DeepSeek-V3-0324 through DeepSeek's API (the code calls
`deepseek/deepseek-chat` in one place and a hardcoded `deepseek-v3` in another). DeepSeek retired
the `deepseek-chat` alias on 24 Jul 2026 and no longer serves V3-0324 itself. A3062 will run a
self-hosted open-weights model at a pinned checkpoint instead (model to be chosen once GPU
memory is known).
Why: The original backbone is unavailable first-party. Self-hosting also keeps the model fixed
for the whole project and gives direct control of sampling and seeds, which compute matching
needs.
Expected impact: Absolute localization accuracy will not match the published 81.67% Acc@1
(File). Comparisons inside A3062 stay valid because every arm shares the backbone. The report
should describe the reproduction as "same pipeline, different backbone" and compare deltas,
not absolute numbers. A lower single-agent baseline may make any coordination benefit easier
to detect (Nature MI capability-saturation finding). If a third-party host still serves
V3-0324, one reproduction arm on the original model would strengthen the comparison.

## 2026-09-20 — Correction: SWE-Bench-Verified-S is 25/25/25, not 23/26/26
What changed: The composition recorded on 2026-09-13 (item 4 above) and in CLAUDE.md said
django 23, sympy 26, sphinx-doc 26. Counting `swe-debate/utils/verified75.txt` directly gives
django 25, sympy 25, sphinx-doc 25 — 75 unique IDs, no duplicates, and all 75 are present in
princeton-nlp/SWE-bench_Verified. The earlier split appears to be a misreading of Appendix A
Table 4.
Why: Noticed while loading the subset for the RQ1 reachability run.
Expected impact: None on the design; the subset is perfectly balanced, which is slightly
better for per-repo analysis than the recorded split suggested. Both CLAUDE.md and item 4
above should be read as 25/25/25.

## 2026-09-20 — Defects fixed in the instrumented fork so the pipeline can run at all
What changed: Five hardcoded values in `swe-debate/localization/` were made
environment-configurable. Each is marked with an `# A3062:` comment at the edit site.
  1. `EntityLocalizationPipeline.__init__` created `OpenAI(base_url="", api_key="")`, so every
     LLM call fails. Now reads `LLM_BASE_URL` / `LLM_API_KEY` (falling back to
     `OPENAI_BASE_URL` / `OPENAI_API_KEY`, and to the literal "EMPTY" key vLLM expects).
  2. The constructor advertised `model_name="deepseek/deepseek-chat"` but both call sites
     hardcoded `model="deepseek-v3"`, so the argument did nothing. Both call sites now use
     `self.model_name`, defaulting to `$LLM_MODEL`.
  3. `self.cache_dir = "/entity_pipeline_cache"` — an absolute path at the filesystem root,
     unwritable on a shared cluster. Now `$ENTITY_PIPELINE_CACHE_DIR`, default `tmp/`.
  4. `LocalizationChainEmbedding.__init__` hardcoded the authors' own model cache,
     `/data/swebench/workspace_agentless/Agentless/models`. Now `$CHAIN_EMBED_CACHE_DIR`,
     defaulting to the standard HuggingFace cache.
  5. (not a code change, recorded here) `localization/requirements.txt` omits `transformers`,
     which `entity_embedding.py` imports at module load. The published requirements file is
     incomplete; a from-scratch install of the localization stage fails on import.
Why: Items 1-4 are hard blockers for the 30 Sep reproduction decision point; none of them
changes any algorithm.
Expected impact: No effect on behaviour, only on whether the code starts. Worth one line in
the report's reproducibility discussion, not the threats-to-validity section.

## 2026-09-20 — The localization stage needs a second model (a local embedding model)
What changed: Nothing yet — recording a planning fact found while reading the code.
`EntityLocalizationPipeline.__init__` eagerly constructs `LocalizationChainEmbedding`, which
loads `intfloat/multilingual-e5-large-instruct` (~2.2 GB) through `transformers` and uses it in
`_select_diverse_chains` to pick the 6 diverse candidate chains. The localization stage is
therefore not "one backbone": it is one generative backbone plus one local embedding model.
Why: Relevant to the GPU application and to compute matching.
Expected impact: Adds ~2.2 GB of GPU (or CPU) memory next to the vLLM server, and the
embedding model must be pinned and held fixed across arms like the backbone is. It consumes no
LLM tokens, so it does not disturb the token-based compute matching, but it should be named in
the experimental setup so the "single backbone" claim is not overstated.

## 2026-09-20 — Graph builder made ~6-12x faster; graphs verified identical
What changed: `CodeAnalyzer._get_source_segment` in `dependency_graph/build_graph.py` opened
the file from disk and called `ast.get_source_segment` once per class and per function, and
`get_source_segment` re-splits the entire source on every call. A file with N entities was
read and split N times — quadratic in file size. The fix reads the source once (the caller
already has it) and hoists the line split to one call per file, using the stdlib's own segment
logic against the pre-split lines.
Why: a single sympy graph took 44 minutes to build, which makes 75 instances impractical and
Phase 3's SWE-bench-Live set impossible. This is a performance defect only.
Expected impact: none on results, by construction and by test. sphinx 180s -> 15s; sympy
2650s -> ~400-500s. The rebuilt graphs were compared node-for-node, edge-for-edge and
attribute-for-attribute against graphs built by the unmodified code for sphinx-doc__sphinx-
10323, django__django-11790 and sympy__sympy-13852: identical in all three. The split uses
`ast._splitlines_no_ff` rather than `str.splitlines` because the two disagree on form feeds,
which occur in django and sympy sources; a regex fallback covers Python versions without the
private helper. Worth one line in the report as a reproducibility contribution.

## 2026-10-01 — Per-call LLM timeout made configurable (was hardcoded 60 s)
What changed: `_call_llm_simple` passed `timeout=60` on every call, overriding the client's
own timeout. It now uses the client's timeout, which reads `LLM_TIMEOUT` (default still 60).
The smoke config sets 600. Fork commit `2f252f9`, in the patch file.
Why: calls request up to 6000 completion tokens (stage 7 debate rounds). The authors used a
hosted API; one power-capped RTX 3090 cannot produce that in 60 s, and a timeout makes the
OpenAI client retry and then raise, so stages would fail for hardware reasons.
Expected impact: none on what the model sees or returns. It only stops slow calls from being
cut off. Calls that still fail are logged per call by the runner.

## 2026-10-01 — The runner passes only four instance fields to the pipeline
workflow.py passes the full moatless record, which also holds the gold patch, gold spans and
tests. The pipeline never reads those fields (grep, 2026-10-01), so the runner passes only
`instance_id`, `repo`, `base_commit` and `problem_statement`. Expected impact: none; it makes
gold-patch leakage impossible instead of merely absent.

## 2026-10-01 — Pipeline environment: litellm 1.53.1 instead of 1.52.1, transformers added
The fork's `localization/requirements.txt` pins `litellm==1.52.1`, which is no longer on PyPI,
and omits `transformers`. The gpu21 environment installs `ablation/gpu21/requirements-swed.txt`:
the upstream list with litellm 1.53.1 (nearest surviving release; satisfies every other pin)
and transformers 4.46.3 (matches the pinned tokenizers 0.20.3). All other 161 pins resolved
on PyPI for Python 3.12 Linux. Expected impact: none on localization. litellm is only imported
by the moatless MCTS stage; the localization stage calls the model through the openai client.
Also added: five packages moatless needs at import time and upstream leaves to the separate
moatless-tree-search package (instructor 1.5.2, docstring-parser, json-repair, tree-sitter-
python/java 0.21.0), and jiter lowered 0.7.0 -> 0.5.0 because no instructor release accepts
both the pinned tenacity 8.5.0 and jiter 0.7. Same expected impact: none; none of these are on
the localization stage's call path.

## 2026-10-01 — Agents are not differentiated by prompt in the code (paper says they are)
Found in a side chat, verified against the fork (upstream `8a7d462`, unmodified here):
in `entity_localization_pipeline.py`, `vote_worker` (stage 6, ~line 1744) and
`analyze_worker` (stage 7 round 1, ~line 1977) send all five agents the same system message
("You are an expert software engineer with deep experience in code analysis and debugging.")
and the same user template. `agent_id` is only a label for logging and parsing; it never
enters the prompt. All calls use temperature 0.7, so the five agents differ only by
sampling. Round 2 (`analyze_worker_round2`, ~line 2049) is a real exchange: each agent gets
its own round-1 answer plus a summary of the others', so inputs differ only in which answer
is labelled "yours". The whole file has four distinct system messages, one per stage, none
per agent. The voting pool also runs only 3 agents at a time (`max_workers=min(num_agents, 3)`),
which affects latency only.
Paper: Sec 4.5 "different system prompts to simulate diverse reasoning perspectives";
Sec 6.2 "our specialized prompts enforce distinct analytical viewpoints".
Impact: we reproduce the code, not the paper's description, and say so. Mechanistically,
stage 6 and stage 7 round 1 are five independent samples pooled by majority or summary
(self-consistency), with one exchange round on top. This bears on Phase 2 (for-chat.md):
"heterogeneous agents" would be adding diversity the paper claims but the code lacks.

## 2026-10-01 — Stage 4 narrows chains by dissimilarity, not relevance, and fixes the order
`_select_diverse_chains` (~line 1526) -> `entity_embedding.select_diverse_chains`: drop empty
and duplicate chains; keep the longest; add the k=5 chains whose e5 embeddings are LEAST
similar to the longest (ascending cosine). The issue text is never used, so a chain that
contains the bug can be discarded for being too similar to the longest one. In the smoke run
6 of 12 chains contained the gold file and 1 of the 6 kept did. Also, the longest chain is
always placed first and shown to the voters as `chain_1`; in the smoke run it won 5/5. Chain
order is therefore not neutral by construction, which is the LLM4FL ordering threat CLAUDE.md
asks us to control. Impact: two things to measure on every run, recall lost at stage 4
(gold in any built chain vs gold in a kept chain) and how often the winner is `chain_1`.
Both are reproduced as-is in the baseline; an ordering control has to be added deliberately.
Stage 3 chain building (`_dfs_traversal`) is single LLM calls steering the walk, not the agents.

## 2026-10-02 — Opt-in lenient JSON parsing in the fork (default off)
What changed: all seven `json.loads` calls in `entity_localization_pipeline.py` (graph walk,
vote, both debate rounds, final plan) go through `_a3062_loads`. With `A3062_LENIENT_JSON`
unset or 0 it is exactly `json.loads`, so default runs reproduce the released code. With 1, a
failed strict parse falls back in order: `strict=False` (raw newlines/tabs in strings); decode
of the first `{...}` (prose before, extra text after); `json_repair` from that first `{`
(comments, trailing commas, invalid escapes like `\s` in code); a later `{` (the first was
prose); arrays only if no object works. Which step succeeded is counted per instance
(`json_parse` in raw.jsonl). Replay on the 32B trial's saved replies: votes 20/20 (released
14/20), round-1 answers 20/20 (released 0/20), all with a `modification_locations` list; two
repaired answers carry stray extra keys from code inside strings. Fork commit after
`2f252f9`, in the patch file. Runner switch: `pipeline.lenient_json` or `--lenient-json`,
recorded in each manifest.
Why: Qwen2.5-Coder-32B wraps its JSON answers in prose ("Based on the issue... {json}" or a
fenced block followed by an explanation), so the released parser rejected every round-1 debate
answer on the first two trial instances and the instance crashed (upstream round-2 defect).
That is a formatting convention, not a reasoning failure, and the paper's model evidently did
not trigger it.
Shape check (added 2026-10-04, lenient mode only): a repaired reply can be valid JSON of the
wrong shape; in job 183230 an agent listed locations as plain strings and the discriminator
crashed calling .get() on a str. `_parse_modification_analysis` now normalises the analysis in
lenient mode (must be an object; location lists become lists of dicts, a string becoming
{"entity_id": string}, unusable entries dropped). Released mode is unchanged.
Same for the final plan (added 2026-10-05): in job 183232 a repaired plan listed a modification
as a string and stage 8 crashed; `_parse_final_plan` now requires an object in lenient mode and
turns a string modification into {"instruction": s, "context": s}. Both normalisers change only
replies that would otherwise crash an instance, so on every non-crashing instance the patched and
unpatched code behave identically; runs that straddle a patch are therefore consistent, and the
crashed instances are re-run with `--resume --retry-errors`.
Adopted 2026-10-04 for every arm of the main experiment (decisions.md); the released-parser
72B runs are kept as an "as released" reference.
Expected impact: when enabled, more agents survive to the debate and fewer instances crash;
nothing changes in what the model is asked or how answers are combined. Any comparison must use
the same setting in every arm; the original-debate baseline is reported with the setting
stated. Agent loss under the released parser stays a measured property (run with it off).

## 2026-10-02 — Backbone chosen: Qwen2.5-72B-Instruct (paper: DeepSeek-V3-0324)
The paper's DeepSeek-V3-0324 (671B MoE) is no longer served (deviation 2026-09-19). Main runs use
Qwen/Qwen2.5-72B-Instruct @495f393 in bf16 on 2 RTX PRO 6000 (tensor parallel), self-hosted with
vLLM 0.30.0 (EEE cluster), context 65,536 tokens via YaRN factor 2 over its native 32,768 (the
paper's API allowed 64k). Smaller and from a different family than the paper's model; all agents
are this one model, as in the paper. Chosen over Qwen2.5-Coder-32B on a 10-instance trial
(decisions.md 2026-10-02). Threat to validity: single model family (for-chat.md).


## 2026-10-08 — Stage-3 neighbour pre-filter exceeds the 64k context on a few sympy instances
Our backbone serves 65,536 tokens (Qwen2.5-72B, YaRN x2), the same window the paper's API allowed,
so the paper's runs may have hit this too (its tokenizer differs, so not on the same instances). On a
fixed handful of sympy instances (17139, 13798, 16766, 18698, 15976, 20916, ...) a
`_prefilter_neighbors_with_llm` prompt plus its 1,000-token output cap exceeds the window; vLLM
returns a context-length BadRequestError and the released code falls back to its heuristic
neighbour selection (`_fallback_neighbor_prefiltering`). 151 such calls across all EEE runs to
2026-10-08, ~2-4 instances per 75-instance run, the same instances in every arm. Deterministic and
identical across arms (and shared outright under --reuse-chains), so it does not bias arm
comparisons; it can lower stage-3 recall on those instances.
Kept as is (no prompt truncation), recorded per call in raw.jsonl.

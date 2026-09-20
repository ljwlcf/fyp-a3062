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

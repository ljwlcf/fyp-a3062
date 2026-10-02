# For chat — FYP A3062

Questions for the claude.ai Project chat: direction, scope, supervisor communication and
writing. Implementation questions stay in Claude Code.

Claude Code adds an item when a question comes up that isn't about the code. When chat
settles one, the answer goes into `decisions.md` (or the plan) and the item moves to
Answered with a pointer.

## Open

- **Possible development: target the graph walk, stage 4 and starting points, not only the
  debate?** For chat and A/P Chen; the approved plan (2026-10-01) is about the debate, so nothing
  here gets built without her agreement. Measured so far (results.md 2026-10-02):
  * Cost: the code-map walk (stages 1-3) is 76-83% of tokens per instance in every run, incl. the
    72B (77%); the vote ~7-11%, the debate ~10-12%. Adaptive debate can save at most ~12%.
  * Where answers are lost: stage 4 (keeps chains least similar to the longest one, never looks
    at the issue) dropped the gold file on 2/10 and 1/10 instances with the 7B and 1/10 with the
    32B (released parser), but 0/10 with the 32B (lenient) and 0/10 with the 72B; the vote lost
    it on a few 7B instances; the 72B selected the gold chain on 10/10. The debate changed the
    file-level answer in 3 of ~80 7B instance-runs (1 wrong->right, 2 wrong->other wrong; order
    check) and 0 times with the 32B or 72B.
  * Made-up starting points: 22-37% of stage-2 start entities are not in the code map and are
    silently dropped (7B 22-27%, 32B 34-37%, 72B 24%).
  Candidate modifications, one at a time as the plan requires:
  1. Issue-aware stage-4 selection: rank kept chains by relevance to the issue as well as
     diversity (e.g. maximal marginal relevance). Correction to the side-chat note: the
     pipeline does NOT already embed the issue (its e5 model only embeds chains, in stage 4),
     so this adds one issue embedding with the already-loaded model. Measured as kept-given-
     built recall.
  2. Grounded starting points: map a made-up entity name to the nearest real node instead of
     dropping it. The name index and a fuzzy retriever already exist in the graph searcher
     (`global_name_dict`, `fuzzy_retrieve_from_graph_nodes`); stage 3 just checks the exact id.
  3. A cheaper walk: fewer or shorter LLM calls in neighbour pre-filtering and node selection,
     where most tokens go.
  Questions: a second modification if adaptive debate shows little room (split-vote rate near
  zero, or the debate rarely changing the answer, as with the 72B so far: 2/10 split, 0 changes)?
  A replacement direction? Or keep the debate focus and present these as future work?
  Caution: the evidence is 7B runs plus one 10-instance pass each of the 32B and 72B. Re-check
  with the chosen backbone's 75-instance baseline before deciding; with the 72B, stage 4 lost
  nothing and almost no answer is lost anywhere, which weakens candidates 1 and 2.
- **Report framing: one model family throughout (threat to validity).** Every agent and both
  backbone candidates in the trial are Qwen models (Qwen2.5-Coder-7B for debugging,
  Qwen2.5-Coder-32B and Qwen2.5-72B for the real runs; decisions.md 2026-10-02), so findings
  about the debate (agreement, order sensitivity, how often the debate changes the answer, JSON
  failures) may not generalise to other model families. The paper used DeepSeek-V3, a different
  family again. Suggested wording for the threats-to-validity section, plus a mitigation that
  doubles as a design option: the heterogeneous agents in adaptive debate (CLAUDE.md plan item
  2, "hardest cases") could come from a second family, e.g. DeepSeek or Mistral, which would
  test cross-family generalisation at the same time. Chat: how to phrase it, and whether a
  second family is worth the compute (it needs its own pinned checkpoint and a GPU slot).
- **Order check failed (weakly): how should adaptive debate's trigger be framed?** With the 7B
  model, vote agreement partly tracks which chain is shown first, so it is not a clean
  confidence signal; and the released longest-first order itself raises accuracy by 15-25
  points (results.md and decisions.md 2026-10-02). Three design options are listed in
  decisions.md; Claude Code will repeat the check with the real backbone first. Chat: is "the
  vote's agreement is order-sensitive" itself a reportable finding about SWE-Debate, and does
  option (b) or (c) change what adaptive debate can claim (it adds cost to save cost)?
- **New hypotheses for the approved plan.** H1-H4 belonged to the retired graph x debate
  factorial (CLAUDE.md). The measurement and adaptive-debate work needs its own, e.g. "on
  instances with a unanimous, confident vote, skipping the debate costs no accuracy". Chat
  should draft them; Claude Code can say what is measurable (scorer:
  `ablation/harness/score_localization.py`).
- **The released code's agents are identical; how to frame that?** The paper says the five
  agents have "different system prompts" (Sec 4.5, 6.2); the code sends all five the same
  prompt at temperature 0.7, so stage 6 and debate round 1 are self-consistency sampling,
  with one real exchange round (deviations.md 2026-10-01). Two questions: whether to raise
  it with A/P Chen or the authors, and how it reshapes the Phase 2 story (heterogeneous
  agents would add diversity the paper claims but the code lacks; adaptive debate would be
  gating what is mostly self-consistency). Related: stage 4 keeps chains by dissimilarity,
  not relevance, and always shows the longest chain first.
- **Ask A/P Chen about her EEE faculty project.** The EEE cluster lists QoS entries
  `chen_lihui_2026_05_00` and `_01`. As a student (`ug`) Jingwei gets 2 GPUs per model and
  180k SU/month; project members get the project's limits and budget instead. Worth asking
  whether Jingwei can be added, since the Phase 1 factorial needs several seeds over 75
  instances. (decisions.md 2026-10-01)
- **How to operationalize candidate density for H4.** Tran & Kiela's distractor injection was
  their weakest lever; SWE-bench-Live multi-file tasks are a candidate proxy. Decide before
  the Phase 1 factorial design is frozen. (CLAUDE.md Known unknowns)
- **Do CoSIL, OrcaLoca, KGCompass and Prometheus need their own literature entries,** or is
  the current 40-paper set enough for Related Work? (progress.md 2026-09-13 (3)/(4))
- **Does the graph-quality finding weaken the Phase 2 primary candidate?** Measured over all
  75 graphs (2026-09-20): 80.0% of django's `invokes` edges, 77.0% of sphinx's and 74.9% of
  sympy's are one-call-name-to-many-targets, i.e. name matches the builder never resolved,
  and invokes is 77.5% of all edges. A single call site naming `get` wires the caller to 618
  different django methods. "Graph-grounded debate"
  assumes graph facts are checkable. If most edges are name collisions, an agent citing
  "X invokes Y" is often citing noise. Three readings, and chat should pick one before
  Phase 2 is fixed: (a) the modification becomes "ground debate in the RELIABLE part of the
  graph" (containment, inheritance, imports — not invokes), (b) resolving the edges properly
  becomes part of the contribution, or (c) fall back to ColMAD. Not urgent until Phase 1
  finishes, but it changes what Phase 1 needs to measure. (notes/results.md 2026-09-20, second entry)
- **Is RQ1 (the reachability ceiling) an interim-report result on its own?** It is the first
  real measurement the project has, it needs no GPU, and it is a number the source paper
  never reports. Worth deciding whether the interim report leads with it or holds it back
  for the final. (notes/results.md 2026-09-20)
- **Report framing / threats to validity: the backbone is much weaker than the paper's.**
  Side-chat figures, approximate and TO BE CHECKED against the DeepSeek-V3 technical report
  before they go in the report: SWE-bench Verified ~42% (DeepSeek-V3) vs ~24% (Qwen2.5-72B);
  GPQA ~59 vs ~49; LiveCodeBench ~38 vs ~31; the paper's V3-0324 is stronger still. Consequence:
  expect lower absolute localization than the paper's ~80%; compare arms with each other, never
  with the paper's numbers. Self-hosting DeepSeek-V3 is not feasible: ~700 GB in FP8 needs 8-16
  pro6000 (ug QoS allows 2; the killable QoS allows 8 but is preempted) and exceeds our 450 GB of
  storage. Only routes: A/P Chen's faculty QoS, or a third-party API serving the open V3-0324
  weights as an optional small robustness check. Chat: worth proposing that check?
- **Methods wording: why self-host (one sentence).** Not cost: at API prices the tokens used so
  far (41.6M in the runs on the Mac by 2026-10-02 evening; the side chat estimated ~37M) would be
  roughly $14 at DeepSeek API prices vs ~$125-170 at GPT-4o or Sonnet prices, and the main
  experiment (~450M tokens) ~$150-200 vs ~$1.5-2k (side-chat price estimates, TO BE CHECKED). The
  reasons: a pinned, unchanging checkpoint across all arms and seeds (DeepSeek-V3-0324 is no
  longer served first-party), logprob access for the adaptive trigger, and reproducibility.
- **Interim report framing (before the "Interim report" item).** Given the 72B results
  (near-unanimous votes, the debate changing nothing, the debate ~10-12% of tokens), consider
  leading with the measurement as the main contribution ("where SWE-Debate's answers are won
  and lost; the debate is mostly redundant at this capability level"), adaptive debate as the
  engineering consequence. Also proposed: freeze the setup (backbone, parser, caps) by
  mid-October so the 75-instance x 3-seed baseline is in the interim report; SWE-bench-Live, the
  second language and the end-to-end check become Semester 2 work. For chat and A/P Chen.
- **Interim report (due 10 Nov): outline and what results it must show.** Not urgent yet;
  start by mid-October.

## Answered

<!-- - YYYY-MM-DD — question → answer, see decisions.md YYYY-MM-DD -->
- 2026-10-02 — Which backbone? → Qwen2.5-72B-Instruct, bf16, 64k, 2x pro6000. Trial (10 instances):
  72B with the released parser 10/10 completed, gold chain selected 10/10, Acc@1 9/10, pre-filter
  truncation 5.6%, hallucinated start entities 24%, 427k tokens and ~2,250 s per instance (8 in
  parallel); Qwen2.5-Coder-32B (1 GPU) collapsed 8/10 debates with the released parser, Acc@1 7/10
  with lenient parsing, truncation ~25%, 34-37% hallucinated starts, 670k tokens. Caveat: 1 vs 2
  GPUs. For A/P Chen: chosen on this evidence; see decisions.md and results.md 2026-10-02.
- 2026-10-01 — Localization-only scope? → Accepted by A/P Chen (no objection), with the small
  end-to-end check as the exception. See decisions.md 2026-10-01 (direction approved).
- 2026-10-01 — Is a vLLM server inside an EEE `sbatch` job allowed? → Yes, Jingwei's call:
  the ban targets personal chatbots, and ours is research use only. See decisions.md 2026-10-01.

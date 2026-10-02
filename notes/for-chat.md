# For chat — FYP A3062

Questions for the claude.ai Project chat: direction, scope, supervisor communication and
writing. Implementation questions stay in Claude Code.

Claude Code adds an item when a question comes up that isn't about the code. When chat
settles one, the answer goes into `decisions.md` (or the plan) and the item moves to
Answered with a pointer.

## Open

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
- **Which backbone for the real runs?** Updated 2026-10-01: the EEE cluster fits a 32B model
  in bf16 (one 96 GB pro6000, or two 48 GB cards), so the MLDA-only trade-off (32B 4-bit vs
  14B bf16) no longer forces quantization. Remaining trade-off is queue time and budget:
  32B bf16 on EEE (busy cluster, 180k SU/month) vs smaller/quantized models on MLDA (free,
  no queue, 2x 24 GB). The paper used DeepSeek-V3 (671B) at full precision, so any choice
  is a logged deviation; unquantized 32B is the smallest one available. A/P Chen may have a
  view. Debug runs use 7B and do not depend on this.
  **Trial under way (2026-10-02, decisions.md):** Qwen2.5-Coder-32B (1 pro6000) vs
  Qwen2.5-72B (2 pro6000), both bf16 at 64k context, on the 10 shakeout instances. Results
  will be added here before this question goes to A/P Chen.
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
- **Interim report (due 10 Nov): outline and what results it must show.** Not urgent yet;
  start by mid-October.

## Answered

<!-- - YYYY-MM-DD — question → answer, see decisions.md YYYY-MM-DD -->
- 2026-10-01 — Localization-only scope? → Accepted by A/P Chen (no objection), with the small
  end-to-end check as the exception. See decisions.md 2026-10-01 (direction approved).
- 2026-10-01 — Is a vLLM server inside an EEE `sbatch` job allowed? → Yes, Jingwei's call:
  the ban targets personal chatbots, and ours is research use only. See decisions.md 2026-10-01.

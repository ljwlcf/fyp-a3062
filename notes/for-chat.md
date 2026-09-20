# For chat — FYP A3062

Questions for the claude.ai Project chat: direction, scope, supervisor communication and
writing. Implementation questions stay in Claude Code.

Claude Code adds an item when a question comes up that isn't about the code. When chat
settles one, the answer goes into `decisions.md` (or the plan) and the item moves to
Answered with a pointer.

## Open

- **Localization-only scope — supervisor confirmation.** Still unconfirmed with A/P Chen.
  Chat: draft the email or meeting point. (progress.md 2026-09-19)
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

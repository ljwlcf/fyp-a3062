# Decisions

## 2026-09-13 — Direction: compute-matched ablation, not a new system
The published SWE-Debate ablation already exists (chains -10.0, edit plan -6.0,
debate -4.2). The gap is that it isn't compute-matched, isn't factorial, reports
no cost, and is single-run. Rejected: building a new multi-agent GraphRAG system.
That ground is occupied by LocAgent, CoSIL, OrcaLoca, KGCompass, Prometheus.

## 2026-09-13 — Scope: localization only
Excludes MCTS patch generation and end-to-end Pass@1. Both factors of interest
live in the localization stage. Removes the Docker test-harness dependency and
most API cost. Cost: not comparable to published Pass@1 numbers. Needs A/P Chen's
agreement.

## 2026-09-13 — Backbone fixed at DeepSeek-V3-0324
Varying the model would reintroduce the confound the project exists to remove.

## 2026-09-13 — No GPU allocation
Inference is API-side. Ask NTU for a persistent CPU node instead.

## 2026-09-13 — Caveat on the single-backbone decision, found via literature review
The single-DeepSeek-V3-0324-backbone decision above (agents differ only by system
prompt, matching SWE-Debate's own setup) may itself suppress any debate benefit,
independent of and prior to compute-matching. ColMAD (arXiv:2510.20963)'s
homogeneous-debater ablation found even its incentive-redesigned debate protocol
fails to beat a single agent when both debaters share the same LLM — heterogeneity,
not protocol design alone, was necessary in their setting. This doesn't change the
backbone decision (SWE-Debate itself is same-model, so matching it is still correct
for isolating architecture from model effects), but it's a real threat to validity:
H2 (debate's contribution shrinks under compute matching) may be partly explained by
agent homogeneity rather than by compute-matching alone, and this is a shared
limitation with the source paper, not something A3062 introduces. Log as an explicit
threats-to-validity item in the report rather than letting it surface as a surprise
in the results. See notes/literature.md's ColMAD entry for the full argument.

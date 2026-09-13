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

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

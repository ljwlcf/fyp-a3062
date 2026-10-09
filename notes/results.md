# Results — FYP A3062

Readable summary of experiment results, newest first. Raw JSON stays in `ablation/results/`.
This file is what chat, the supervisor and the report draw on, so write each entry so it makes
sense without opening the code.

Every entry names its config. A result that can't be traced to a config is not a result.

Format:

## YYYY-MM-DD — <short name> (Phase N, RQx)
Config: `ablation/configs/<file>` · Raw: `ablation/results/<file>`
Setup: backbone + checkpoint, subset, number of instances, seeds
Numbers: Acc@1 (File), chain recall@K, selection precision, tokens/instance by stage
Takeaway: one or two sentences on what this means for H1–H4 or the plan
Caveats: single seed, partial run, logged deviation, etc.

---

## 2026-10-09 — Paired arms on identical chains, pooled: adaptive non-inferior at a 3-point margin, -40% tokens
Tool: `ablation/harness/paired_arms.py` (finds every --reuse-chains run from its manifest; output
`ablation/results/paired_arms_20261009.json`). New runs: adaptive round1_only seed 2
(`baseline_72b_adaptive_r1_lenient_v1/20261008-103700`, job 192118), adaptive seed 5
(`baseline_72b_adaptive_lenient_v1/20261008-220852`, job 192615), noise-floor reruns seed 2
(`baseline_72b_rerun_lenient_v1/20261008-115640`, job 192818) and seed 4 (`/20261008-151604`, job
193013). All 75/75 ok, chains identical to their reference seed. Qwen2.5-72B @495f393, 2x pro6000.
| arm (pooled over seeds) | instance-runs | Acc@1 | stage 6-7 tokens | vs first original run | vs mean of all original-arm runs |
|---|---|---|---|---|---|
| original rerun (noise floor), seeds 1-4 | 300 | 0.760 | +1% | 5 : 8, p 0.58, 4.3% discordant | - |
| adaptive single-agent, seeds 1-5 | 375 | 0.739 | 61.7k (-40%) | 6 : 11, p 0.33, 4.5% | -0.9 points [-2.8, +0.9]; one-sided 95% lower -2.4 |
| adaptive round1_only, seeds 1-3 | 225 | 0.751 | 73.8k (-28%) | 1 : 8, p 0.04, 4.0% | -2.2 [-5.3, +0.4]; lower -4.7 |
| self-consistency (reuse), seeds 1-3 | 225 | 0.760 | 99.8k (-2%) | 3 : 8, p 0.23, 4.9% | -1.3 [-3.6, +0.9]; lower -3.3 |
("vs mean": each seed's reference is the average of its first original run and its noise-floor rerun
where one exists, seeds 1-4; seed 5 has the first run only.)
Takeaway: adaptive debate (skip on unanimous vote, single-agent plan) is non-inferior to the original
at a 3-point margin (one-sided 95% lower bound -2.4 points) while cutting stage 6-7 tokens by 40%
(~10% of all tokens). Its discordance with the original (4.5%) equals the original's with itself
(4.3%). The round1_only skip is worse (p = 0.04 against the first run) and costs more: dropped.
The equal-token single agent (self-consistency) shows no significant difference from the debate.
Caveats: n=75 per seed; one backbone; adaptive seed 6, rerun seed 5 and SC seeds 4-5 are queued.
* Lenient seed 6 added (job 186753, raw `baseline_72b_lenient_v1/20261009-022556`, 75/75 ok, 7 h 46):
  Acc@1 0.747, selected 0.773, kept 0.907. Original arm, 6 seeds: 0.760 / 0.813 / 0.773 / 0.733 /
  0.680 / 0.747, mean 0.751. Replay over 6 seeds, unanimous skip: -0.1 points [-1.6, +1.4] at -39%.
  lp_conf, leave-one-seed-out over the four fixed-order seeds with logprobs (1, 4, 5, 6): the chosen
  threshold jumps between 0.51 and 0.999 and the held-out result is never better than the unanimous
  rule (-2.7, +1.3, -1.3, -0.3 points). Vote agreement stays the trigger.

---

## 2026-10-08 — Adaptive round1_only variant, seed 3; correction on the skipped/debated split
Raw: `baseline_72b_adaptive_r1_lenient_v1/20261008-074136` (job 192116; adaptive, skip_mode
round1_only, --reuse-chains original seed 3; 75/75 ok, 1 h 34; chains identical).
* Seed 3, all on the same chains: original 0.813 (101k stage 6-7 tokens), original rerun 0.813
  (103k), adaptive single-agent 0.787 (63k; 2 : 4 vs original), adaptive round1_only 0.773 (74k,
  -27%; 1 : 4). Skipped 60/75.
* CORRECTION (applies to the 2026-10-07 and 2026-10-08 entries): splitting an adaptive run into its
  "skipped" and "debated" instances conditions on that run's OWN re-sampled vote. Its debated
  instances are those where its vote split, i.e. where its chosen chain is more often wrong, while
  the original's vote on the same instance may have been unanimous on the right chain. The split
  therefore biases the debated subset against adaptive and the skipped subset in its favour; only
  whole-run totals are fair comparisons. The statements "the loss is on skipped instances" (which
  motivated round1_only) and "the loss is on the re-run debate" are both unreliable for this reason.
* Seed 1 added (job 192117, raw `baseline_72b_adaptive_r1_lenient_v1/20261008-091203`, 75/75 ok, chains
  identical; skipped 63/75): original 0.773 (104k), original rerun 0.720 (105k), adaptive single-agent
  0.747 (62k), adaptive round1_only 0.733 (76k; 0 : 3 vs the first original run). Every arm lies inside
  the spread of the original's own two runs (0.720-0.773).
Takeaway so far: both skip variants are within the noise floor on seeds 1 and 3; round1_only costs
more tokens and is not better. Seed 2 (192118) follows.

---

## 2026-10-08 — Live pilot seed 2: INVALID as recorded (33/40 hit a dead server); repair queued
Raw: `live_pilot40_lenient_v1/20261006-101233` (job 186864, killable, resumed after preemption).
As recorded: Acc@1 0.075, built 0.15, because 33 instances' first call failed with
APIConnectionError and were written as "ok" with no entities (decisions.md 2026-10-08). Not a
result; the 7 intact instances stay, the 33 are rerun by job 192683. Do not use this folder until the
repair lands (the local copy is the broken one; re-fetch raw.jsonl explicitly afterwards).

---

## 2026-10-08 — Noise floor measured; adaptive seed 4; adaptive is within run-to-run noise of the original
Raw: `baseline_72b_rerun_lenient_v1/20261007-093747` (job 189863, original arm re-run on original
seed 3's chains, vLLM SEED 103) and `/20261007-185521` (job 190480, on seed 1's chains, SEED 101);
`baseline_72b_adaptive_lenient_v1/20261007-140626` (job 190072, adaptive, reuse of seed 4). All 75/75
ok, chains identical to the reference seed. Qwen2.5-72B @495f393, 2x pro6000, lenient.
* NOISE FLOOR, the identical original arm re-run on the same chains: seed 3 0.813 vs 0.813
  (2 : 2), seed 1 0.720 vs 0.773 (0 : 4); pooled 2 : 6 against the first run, 5.3% of instances
  discordant. Re-running the released vote + debate moves ~4 answers per 75, and the first run
  happened to be the luckier one on seed 1 by 4 instances.
* Adaptive seed 4: 0.733 vs 0.733 (1 : 1), 64.1k vs 103.5k tokens.
* Adaptive, 4 paired seeds vs the single original run per seed: 4 : 10 (p = 0.18), discordance
  4.7%, the same as the noise floor (5.3%); -40% stage 6-7 tokens.
* Adaptive vs the MEAN of all original-arm runs on the same chains (both runs on seeds 1 and 3,
  one on seeds 2 and 4): 0.750 vs 0.763, -1.3 points, 95% bootstrap [-3.3, +0.7], one-sided 95% lower
  bound -3.0 points. On seed 1 adaptive (0.747) scores between the two original runs (0.773, 0.720).
Takeaway: adaptive debate (skip on unanimous vote, single-agent plan) cuts stage 6-7 tokens by 40%
and its accuracy difference is the size of re-running the original itself; non-inferiority at a
3-point margin is borderline with 4 seeds. The round1_only variant (192116-192118) and more seeds
(lenient 5-6 -> adaptive 5-6) will tighten it.
Caveats: two noise-floor reruns; n=75; adaptive seeds are paired with the first original run.
* Lenient seed 5 added (job 186752, raw `baseline_72b_lenient_v1/20261008-003045`, 75/75 ok, 7 h 11):
  Acc@1 0.680, selected 0.640, kept 0.880; debate 1 fixed, 1 broke. Original arm over 5 seeds:
  0.760 / 0.813 / 0.773 / 0.733 / 0.680, mean 0.752 (13-point spread between seeds, mostly from the
  graph walk: kept 0.88-0.93, selected 0.64-0.83; the reason arm comparisons reuse chains). Replay over
  5 seeds, unanimous skip: -0.4 [-2.0, +1.4] at -39% tokens; lp_conf >= 0.99 on seeds 1/4/5: +0.3
  [-0.4, +1.4] at -16%.

---

## 2026-10-07 — Lenient seed 4; adaptive-trigger replay over 4 original seeds
Raw: `baseline_72b_lenient_v1/20261006-222229` (seed 4, job 184812, vote logprobs; 75/75 ok),
`baseline_72b_lenient_v1/trigger_replay_pooled_s1234.json`. Qwen2.5-72B @495f393, 2x pro6000, lenient.
* Seed 4: Acc@1 0.733 (55/75), selected 0.787, kept 0.907; debate effect 53 unchanged right, 18
  unchanged wrong, 2 fixed, 1 broke, 1 no answer; mean lp_conf 0.856. Original arm (lenient), 4
  seeds: 0.760 / 0.813 / 0.773 / 0.733, mean 0.770.
* Replay, 4 seeds (300 rows): skip on a unanimous vote (83% skipped) -0.2 points [-1.9, +1.8] at
  62k vs 102k stage 6-7 tokens (-39%); always-skip 0.755 vs 0.770.
* lp_conf on the two fixed-order seeds with logprobs (1 and 4, 150 rows): >= 0.95 skips 54%, +0.1
  [-0.9, +1.9] at -25% tokens; >= 0.99 skips 35%, +0.4 at -17%. Agreement on the same rows: -1.2
  [-3.6, +1.1] at -37%. lp_conf is the safer trigger, agreement the cheaper one; neither difference
  is significant. Self-reported confidence >= 90.4: held out on each seed, 3 of 4 at or above the
  original, -18% tokens.
* The strict held-out rule ("cheapest threshold with no in-sample loss") is unstable across seeds
  (it jumps between never-skip and 0.8): with ~1-2 instances deciding it, a pre-set threshold
  (unanimous) is the sounder choice; that is what the adaptive arm uses.
Scorer fix (same day): vote-logprob tokens are parsed with isdecimal (seed 4 had a "₁" token that
passes isdigit but not int()); rescoring seed 1 and the shuffled run gives identical lp fields.

---

## 2026-10-07 — First real ADAPTIVE run (72B, paired with original seed 3) and reuse-chains SC seed 2
Raw: `baseline_72b_adaptive_lenient_v1/20261006-174449` (job 188238; arm adaptive, unanimous vote ->
single-agent plan; --reuse-chains original seed 3; 75/75 ok, 1 h 30), `baseline_72b_sc_lenient_v1/
20261006-140151` (job 187682; reuse of original seed 2; 75/75 ok, 58 min). Qwen2.5-72B @495f393,
2x pro6000, lenient, vote logprobs. Chains identical to the reference seed in both.
* Adaptive vs original (seed 3, same chains): Acc@1 0.787 vs 0.813; discordant 2 : 4, exact McNemar
  p = 0.69; stage 6-7 tokens 62.6k vs 101.4k (-38%). Debate skipped on 58/75 (77%).
  The replay predicted 81% skipped, 62.9k tokens (matches) and Acc@1 0.829 (does not).
  Where the gap is: on the 58 skipped instances adaptive 0.810 vs original 0.776 on the same
  instances; on the 17 debated ones adaptive 12/17 vs original 16/17, although both ran the same
  released debate on the same chain set (the vote was re-sampled too). So the shortfall is re-run
  variance of the vote + debate on split-vote instances, not the skip: rerunning the identical
  procedure on the hardest 17 moved 4 answers.
* SC reuse seed 2: 0.733 vs original 0.760, discordant 0 : 2, tokens 97.6k vs 99.8k.
  Reuse-chains SC pooled over 3 seeds (identical chains): SC-only right 3, original-only right 8,
  exact McNemar p = 0.23; SC mean 0.760 vs original 0.782. The equal-token single agent trends
  ~2 points below the debate; not significant.
* Adaptive seed 1 added (job 189312, raw `baseline_72b_adaptive_lenient_v1/20261007-054304`, reuse of
  original seed 1; chains identical, 75/75 ok): 0.747 vs 0.773, discordant 1 : 3 (p = 0.62); stage
  6-7 tokens 61.8k vs 104.4k (-41%); skipped 62/75; on skipped 47 vs 49, on debated 9 vs 9 of 13.
  Pooled seeds 1+3: 3 : 7, exact McNemar p = 0.34; -40% stage 6-7 tokens; adaptive mean 0.767 vs
  0.793 on these two seeds (-2.7 points, not significant; the noise-floor rerun 189863 will show
  how much two runs of the same original arm disagree).
* Adaptive seed 2 added (job 189313, raw `baseline_72b_adaptive_lenient_v1/20261007-082621`, reuse of
  original seed 2; chains identical, 75/75 ok): 0.733 vs 0.760, discordant 0 : 2; tokens 57.6k vs
  99.8k (-42%); skipped 64/75; debated 9 vs 9 of 11.
* THREE PAIRED SEEDS (1-3): adaptive 0.756 vs original 0.782; discordant 3 : 9, exact McNemar p = 0.15;
  difference -2.7 points, 95% bootstrap [-5.8, 0.0], one-sided 95% lower bound -5.3; stage 6-7
  tokens 60.7k vs 101.9k (-40%). The same ~2-instance loss in every seed; mostly on SKIPPED instances
  (the lone plan agent), the debated ones tie in seeds 1 and 2. Not significant, but consistent, so
  the reserve skip branch (five round-1 agents, no round 2) is now being run (decisions.md 2026-10-07).
Takeaway: adaptive debate saves ~38% of stage 6-7 tokens (~9% of all tokens) at an accuracy change
inside run-to-run noise (one seed). Run-to-run variance on split votes is itself large enough that
several seeds per arm are essential; adaptive seeds 1 and 2 are queued (189312, 189313).
Caveats: one adaptive seed; n=75; 17 debated instances.

---

## 2026-10-06 — Equal-token single agent on the SAME chains as the debate (reuse-chains SC seed 3)
Raw: `baseline_72b_sc_lenient_v1/20261006-061753` (job 186863, `--reuse-chains
baseline_72b_lenient_v1/20261004-215633` = original seed 3), Qwen2.5-72B @495f393, 2x pro6000,
lenient, vote logprobs. 75/75 ok, 1 h 07 min wall (vs ~5 h for an own-chains run).
* Chains identical to original seed 3 on all 75 instances (kept recall and kept count match).
* Acc@1 0.840 (63/75) vs the debate's 0.813 (61/75) on the same chains; selected 0.840 vs 0.827.
  Discordant: single agent right / debate wrong 3, debate right / single agent wrong 1; exact
  McNemar p = 0.63. Stage 6-7 tokens 100k vs 101k (achieved / budget = 0.99).
* Read with the own-chains SC result (-3.1 points [-8.0, +1.3]): once the chains are held fixed the
  gap disappears, so most of it was the SC runs' weaker chains (kept 0.87-0.89 vs 0.93), not the arm.
Takeaway: spending the debate's tokens on more independent votes plus one plan agent is at least as
accurate as the debate here. One seed; reuse-chains SC seeds 1 and 2 (187444, 187682) follow.
* Seed 1 added (job 187444, raw `baseline_72b_sc_lenient_v1/20261006-095241`, reuse of original seed 1;
  chains identical, 75/75 ok): SC 0.707 vs debate 0.773, discordant 0 : 5 for the debate; tokens
  101k vs 104k. In 4 of the 5 both arms chose the same chain and the lone plan agent named a wrong
  file (twice a path not in the repository: `models.py`, `babel/messages/catalog.py`) where the
  debate's five round-1 agents and discriminator were right; the 5th is django-11999 (the debate's
  out-of-chain fix). Pooled seeds 1+3: 3 : 6, exact McNemar p = 0.51. No significant difference;
  the single-plan-agent step has visibly higher variance.
* Replay of a cheaper skip branch (keep the five round-1 agents, drop round 2; answer = round-1
  majority), 3 lenient seeds: all rows 0.773 at 70k vs full debate 0.782 at 102k vs single plan
  agent 0.766 at 55k; on unanimous votes 0.783 / 0.778 / 0.774. Within about one instance of each
  other; logged as an alternative skip branch (decisions.md 2026-10-06, adaptive arm).
Caveats: n=75, one seed, the reference seed is the best-scoring original seed (0.813).

---

## 2026-10-06 — Self-consistency seed 2; first 72B SWE-bench-Live numbers (pilot, 40 instances)
Raw: `baseline_72b_sc_lenient_v1/20261005-201603` (SC seed 2, job 184574);
`live_pilot40_lenient_v1/20261004-195344` (Live pilot, job 183679 + repair 186745 for
beetbox__beets-5437, 40/40 ok). Qwen2.5-72B @495f393, 2x pro6000, lenient, released order.
* Self-consistency seed 2: Acc@1 0.773, kept 0.893, stage 6-7 tokens 98k. Seeds 1-2 pooled:
  0.740 at 96k vs the original arm's 0.782 (seeds 1-3) at ~102k. Both SC seeds walked the graph
  themselves (own chains); from seed 3 on the SC arm reuses the original seed's chains
  (decisions.md 2026-10-06). The discriminator keeps the lone round-1 file in 97% of instances.
* Self-consistency seed 3, own chains (job 184575, raw `baseline_72b_sc_lenient_v1/20261006-011332`):
  Acc@1 0.773, selected 0.800, kept 0.893, stage 6-7 98-100k. Own-chains SC, 3 seeds: 0.707 / 0.773 /
  0.773, mean 0.751 vs original 0.782 at 97k vs 102k stage 6-7 tokens; per-instance means over the 3
  seeds, SC minus original -3.1 points [-8.0, +1.3] (paired bootstrap; 8 instances better, 11 worse).
  The equal-token single agent is not significantly worse; part of the gap may be its weaker chains
  (kept 0.87-0.89 vs 0.92-0.93), which the reuse-chains SC seeds (186863, 187444) remove.
* Live pilot (first 40 of the 386; verified split, created after 2024-09-19): Acc@1 0.575 (23/40),
  selected 0.650, kept 0.750, built 0.825; vote agreement 0.96; tokens 640k per instance (stage 6-7
  126k), ~1.6x the Verified subset. Debate effect: 23 unchanged right, 13 unchanged wrong, 3 broke,
  1 changed to another wrong file, 0 fixed. Replay: always-skip 0.630 vs debate 0.575; per-instance
  oracle 0.640.
Takeaway: post-cutoff issues are much harder for the same pipeline (0.575 vs ~0.78), the loss is
spread over every stage (built 0.83, kept 0.75, selected 0.65), and on these the debate did harm,
not good. Consistent with adaptive debate skipping most debates.
Caveats: 40 instances, one seed, first 40 lines of the id file (not a random sample: the file is
in dataset order). The rest of the seed (parts a-c) is running; Live seed 2 started (186864).

---

## 2026-10-06 — Lenient seed 1 and self-consistency seed 1 (72B); trigger replay over 3 seeds; correction
Raw: `baseline_72b_lenient_v1/20261005-082019` (seed 1, job 184572, vote logprobs),
`baseline_72b_sc_lenient_v1/20261005-153006` (self-consistency seed 1, job 184573),
`baseline_72b_lenient_v1/trigger_replay_pooled_s123.json`. Qwen2.5-72B @495f393, 2x pro6000, lenient.
* Seed 1: Acc@1 0.773 (58/75), selected 0.720, kept 0.920; debate effect 56 unchanged right,
  16 unchanged wrong, 2 fixed, 1 changed to another wrong file. Lenient original arm, 3 seeds:
  0.760 / 0.813 / 0.773, mean 0.782 (as-released: 0.707 / 0.720 / 0.760).
* Self-consistency seed 1 (equal tokens: N votes + one single-agent plan): Acc@1 0.707, stage 6-7
  tokens 94k vs ~102k for the original; kept 0.867 (its own graph walk built weaker chains, so
  part of the gap is not the arm; see decisions.md 2026-10-06). The lone round-1 file survives the
  discriminator in 97% of instances, so the replay's skip proxy is sound.
* Replay, seed 1: always-skip 0.733 vs debate 0.773 (the debate helps on ~3 instances).
  Pooled seeds 1-3 (225 rows): debate 0.782, always-skip 0.766 (-1.6 [-4.4, +0.8]); skip only on a
  unanimous vote (84% skipped): 0.779, -0.4 [-2.0, +1.3] points at -39% stage 6-7 tokens. lp_conf
  (seed 1 only) does not beat agreement: >= 0.95 skips 51%, -1.1 [-2.1, -0.3]. Held-out agreement
  thresholds: seeds 2 and 3 never skip when trained on the others' strict no-loss rule; seed 1 at
  0.8 skips 92% and loses 2.7 points.
* CORRECTION to 2026-10-05 ("the debate can fix at most ~3 of 75"): the final plan names files
  freely, not only files in the chosen chain. The debate's real fixes are selection failures
  repaired by naming a file outside the chain: django-11999 (seeds 1 and 3), sphinx-8035,
  sympy-15809; in each, all round-1 agents named the wrong file and the plan named the gold one.
  Most come with split or low-confidence votes (agreement 0.6, lp_conf 0.43), i.e. where adaptive
  debate keeps the debate; django-11999 in seed 1 had a unanimous vote (lp_conf 0.94).
Takeaway: adaptive debate skipping on unanimous votes keeps accuracy within half a point at ~40%
fewer stage 6-7 tokens (~10% of all tokens); the debate's value is small, real, and concentrated on
split votes. Whether a chain-level debate adds more is the open for-chat question.
Caveats: n=75 per seed; replayed skip branch; lp_conf on one fixed-order seed so far (seeds 4-6
will add it); self-consistency seeds 2-3 pending.

---

## 2026-10-05 — Adaptive-debate trigger, offline replay: skipping the debate loses nothing at 72B (lenient); errors are in chain selection (Phase 1 -> plan item 2)
Tool: `ablation/harness/replay_trigger.py` (no GPU; replays both branches from original-arm runs).
Raw: `trigger_replay.json` in each run folder: `baseline_72b_lenient_v1/20261004-143435` (fixed
order, seed 2), `order_72b_lenient_v1/20261004-071233` (shuffled), `baseline_72b_released_v1/
20261003-013441` and `/20261003-091827` (released parser).
Setup: Qwen2.5-72B-Instruct @495f393, 2x pro6000, verified75. Skip branch = one round-1 agent's
top file on the vote's winning chain (expected value over the five exchangeable agents; an
unparsed reply counts as wrong); cost = vote + one round-1 call + the discriminator (overstates the
real skip step). Full branch = the run's own final plan.
Numbers (Acc@1 File; mean stage 6-7 tokens):
| run | original (full debate) | always skip | per-instance oracle |
|---|---|---|---|
| lenient fixed, seed 2 (repaired: django-12155 rerun ok) | 0.760, 100k | 0.760, 53k | 0.765 |
| lenient shuffled | 0.720, 103k | 0.720, 54k | 0.736 |
| lenient fixed, seed 3 (183233) | 0.813, 101k | 0.805, 55k | 0.840 |
| pooled lenient fixed, seeds 2+3 | 0.787, 101k | 0.783, 54k | 0.803 |
| released parser, run 013441 | 0.720, 114k | 0.661, 66k | 0.744 |
| released parser, run 091827 | 0.760, 112k | 0.680, 65k | 0.803 |
* Lenient: the debate changes the outcome on 1-2 instances per run in each direction; no threshold
  on lp_conf, vote agreement or self-reported confidence beats "always skip" (best no-loss
  threshold = skip everything; held-out across the two lenient runs picks the same). Paired
  bootstrap, always-skip minus original, shuffled run: 0.000 [-0.029, +0.037].
* Seed 3 added (2026-10-05, raw `baseline_72b_lenient_v1/20261004-215633`, job 183233; 75/75 ok):
  Acc@1 0.813 (61/75), selected 0.827, kept 0.933, built 0.973, selection given kept 0.886;
  debate effect 59 unchanged right, 12 unchanged wrong, 2 fixed, 1 broke, 1 plan failed after right.
  Seed 2 repaired the same day (184567: django-12155 rerun ok; seed 2 Acc@1 unchanged 0.760, 75/75
  ok; its replay row above is the repaired one). Pooled seeds 2+3, best in-sample trigger: skip when
  vote agreement >= 0.8 (4 or 5 of 5): skips 89%, Acc@1 0.795 vs 0.787, -42% stage 6-7 tokens;
  paired bootstrap adaptive minus original +0.008 [-0.009, +0.031]. Held out (threshold from the
  other seed): seed 2 0.760 = original at -43% tokens; seed 3 0.805 vs 0.813 (one instance) at -46%.
* Released parser: 13-15% of round-1 replies do not parse (4.2-4.4 valid of 5), which sinks a lone
  agent; given a parsed reply the single agent scores 0.747 / 0.811, i.e. at or above the debate.
  The debate's edge there is redundancy against parse failures, not reasoning.
* Where the errors are (lenient): of 21 / 18 wrong instances, 18 / 15 are selection failures (the
  vote's chain does not contain the gold file; 11 / 6 of these had the gold file in another kept
  chain) and only 3 / 3 are within-chain. The released debate works only inside the chosen chain,
  so it can fix at most ~3 of 75. lp_conf < 0.9 (shuffled run) flags 9 of 19 selection failures,
  6 of them recoverable from another kept chain.
* Cost: stages 6-7 are 25% of per-instance tokens at 72B (total ~410k); always-skip saves ~47% of
  them, i.e. ~12% of the total.
Takeaway: as specified (skip vs the released plan debate), adaptive debate can only save tokens:
same accuracy at ~half the stage 6-7 cost. Any accuracy gain must come from the triggered branch
revisiting the CHAIN CHOICE on uncertain votes (question in for-chat.md).
Caveats: 1-2 runs, n=75, intervals +-3-4 points; the skip branch is replayed, not run (the
discriminator on a lone analysis may change its file; to be checked with the self-consistency runs,
`--sc`); lp_conf only on the shuffled run so far (seed 1 and the self-consistency seeds will add it).

---

## 2026-10-05 — 72B order check at scale (lenient): primacy bias in the vote, agreement not inflated; vote logprobs carry signal (Phase 1, precondition)
Configs: fixed order = `baseline_72b_lenient_v1.yaml` seed 2 (job 183232, raw
`baseline_72b_lenient_v1/20261004-143435`); shuffled = `order_72b_lenient_v1.yaml` (shuffle seed 1,
vote logprobs top 10; job 183231, raw `order_72b_lenient_v1/20261004-071233`). Qwen2.5-72B, lenient
parsing, released caps, 2x pro6000 (Server Edition), 75 instances each. Analysis:
`analyze_order.py` (order_analysis.json next to the runs).

**Order** (fixed 74 scored / shuffled 75; one fixed instance crashed, see below):
- Winner shown first: 0.46 -> 0.29 (chance 0.17). Under shuffle, wins by shown position 1..6:
  22, 18, 15, 9, 5, 6 against ~13 expected each by chance: a monotonic PRIMACY bias, independent of
  content (the prompt's `chain_2` example fits the same gradient; no separate effect visible).
- Winner is the longest kept chain: 0.53 -> 0.59 (content preference survives shuffling).
- Mean vote agreement 0.95 -> 0.96; unanimous 0.87 -> 0.88. Agreement when the first-shown chain
  won vs another won: fixed 0.97 / 0.94, shuffled 0.93 / 0.97, i.e. no inflation by position.
- Gold in the selected chain 0.78 -> 0.75; Acc@1 (File) 0.77 -> 0.72 (a few instances; within
  seed noise).

**Vote logprobs** (shuffled run, first real data): mean lp_conf 0.88 (median 0.96, p10 0.59, min
0.35); the logprob top chain is the vote's winner on 71/75; 25/75 instances have lp_conf < 0.9
(vs 6/75 split votes). Selection right when lp_conf >= 0.9: 40/50 (80%); when < 0.9: 16/25 (64%).
By vote agreement: >= 0.8: 53/69 (77%); split: 3/6. Mean lp_conf 0.91 when the selection was right,
0.80 when wrong.

**Also:** lenient seed 2 had one crash (django-12155, a repaired final plan with string entries;
fixed, re-run queued as 184567). 7B SWE-bench-Live smoke test (job 183710, 40 pilot instances, 7B,
killable pro6000): pipeline works end to end, 40/40 completed, gold scoring correct; 7B numbers
(not results): gold in built chains 85%, kept 65%, selected 52.5%, Acc@1 47.5%, split votes 27.5%,
hallucinated starts 31% (verified-set 7B: ~100% / 80-90% / ~70% Acc@1).

**Takeaway.** At 72B scale vote agreement does not depend on display order (the 7B concern does
not carry over), but it is saturated (~88% unanimous), so it identifies few uncertain instances.
The vote itself has a clear primacy bias in which chain wins. Vote logprobs are far less saturated
(a third of instances below 0.9) and do separate right from wrong selections somewhat (80% vs 64%),
which makes them the more promising adaptive-debate trigger. One seed per order condition so far;
needs the other lenient seeds and ideally a second shuffle seed.

---

## 2026-10-04 — 72B as-released baseline: 75 instances x 3 seeds (Phase 1, main baseline)
Configs: seed 1 = `backbone_trial_72b_v1.yaml` (10, job 180343) + `backbone_trial_72b_rest65_v1.yaml`
(65, job 180726), vLLM seed 0; seeds 2/3 = `baseline_72b_released_v1.yaml` with SEED=2/3 (jobs
180739, 180740). Raw + scores: `backbone_trial_72b_v1/20261002-103421`,
`backbone_trial_72b_rest65_v1/20261002-185459`, `baseline_72b_released_v1/20261003-013441` and
`-091827`. Qwen2.5-72B @495f393 bf16, 64k YaRN, 2x pro6000 tensor parallel, released parser,
released caps, released chain order; 8 workers (180343) / 6 (the rest).

**Numbers** (seed 1 / 2 / 3, out of 75; pooled out of 225):
- Gold file in a built chain 73 / 73 / 72 (218, 97%); in a kept chain 71 / 69 / 69 (209, 93%);
  in the selected chain 64 / 58 / 64 (186, 83%); Acc@1 (File) 53 / 54 / 57 (164, 73%); gold file
  anywhere in the plan 57 / 56 / 61.
- Per instance over 3 seeds: Acc@1 right 3/3 on 39, 2/3 on 19, 1/3 on 9, 0/3 on 8 instances.
  By repo (mean Acc@1): sympy 0.81, django 0.73, sphinx-doc 0.64.
- Debate effect over 225 instance-runs: 2 fixed (wrong -> right), 3 broke (right -> wrong),
  3 changed to another wrong file; otherwise unchanged. The debate's net effect is ~0.
- Lost after the vote: selected-chain-has-gold 186 vs Acc@1 164. 12 instance-runs lost the
  answer to an empty final plan, and in all 12 the released parser rejected the discriminator's
  reply (not truncation); 7 of them in seed 1.
- Split votes (agreement < 0.8): 7 / 7 / 8 (~10%); mean vote agreement 0.94-0.95.
- Winner = chain_1 (shown first) 53 / 50 / 46; winner = longest kept chain 64 / 65 / 60
  (chance ~1/6).
- Agents dropped by JSON parsing on 51-59 of 75 instances per seed (rarely all five; 1 debate
  collapse in each of seeds 1 and 2). Hallucinated start entities 27-29%.
- Truncation (4 runs): pre-filter 646/15,742 (4.1%), round-1 analyses 9/1,125, round 2 3/957,
  node selection 1/23,924.
- Tokens per instance 487k / 503k / 496k: graph walk ~78%, vote ~11%, debate ~11%.
- Wall time per 75-instance pass on 2 pro6000, 6 workers: 7.7 h (seed 2), 8.1 h (seed 3).

**Takeaway.** With a backbone far weaker than the paper's, the released pipeline localizes the
right file 73% of the time (paper ~80% with DeepSeek-V3-0324). The graph walk almost always
reaches the gold file; answers are lost mainly in the vote (23 of 209 kept-with-gold) and after
it (22 of 186 selected-with-gold), and the debate itself changes the answer in ~4% of
instance-runs with no net gain. About a third of instances flip between seeds, so paired
multi-seed comparisons are essential. Votes are near-unanimous (~10% split), which bounds what
adaptive debate can save to roughly the debate's ~11% of tokens on ~90% of instances.

**72B parser comparison (same 10 instances, 180343 released vs 180368 lenient):** agents dropped
on 7 vs 0 instances; selected chain 10 vs 8; Acc@1 9 vs 7 (3 instances flipped, within seed
noise); split votes 2 vs 1; 427k vs 321k tokens. Lenient parse steps: strict 1,216, first object
256, repaired 33, relaxed 4.

**Caveats.** Seed 1 mixes 8 and 6 workers and two jobs; seeds 2/3 are single jobs. vLLM is not
bit-reproducible under concurrency, so seeds are independent samples.

---

## 2026-10-02 — Backbone trial, interim: Qwen2.5-72B with the released parser (Phase 1, backbone choice)
Config: `ablation/configs/backbone_trial_72b_v1.yaml` · Raw + scores:
`ablation/results/backbone_trial_72b_v1/20261002-103421/` (EEE job 180343; 2 pro6000 Server
Edition, tensor parallel, highmem, 8 workers, 64k context via YaRN, released JSON parser,
released max_tokens caps). Queue: submitted 06:47, started 10:26 UTC (~59 min genuine wait for
two cards, the rest our own QoS limit); server up in 7.7 min (145 GB weights from the HDD tier).

**Numbers** (10 instances):
- 10/10 completed, 0 debate collapses (the 32B under the same parser: 8/10 collapsed).
- Gold file built 10/10, kept 10/10, selected chain 10/10; Acc@1 (File) 9/10 (sympy-13647 wrong).
- Debate effect: 9 unchanged-right, 1 unchanged-wrong, 0 changed. Round-1 agreement 1.0; vote
  agreement 0.92; split votes 2/10; no invalid votes; agents dropped on 7/10 instances (some
  replies unparseable, never all five).
- Hallucinated start entities 48/200 (24%; 32B 34-37%, 7B 22-27%).
- Truncation: 35/1,751 calls, all in the pre-filter (35/625 = 5.6%; 32B ~25%); 34 of the 35 cut
  replies already contained a complete JSON object (prose after it), 1 needed repair.
- 427k tokens per instance (graph walk 330k, vote 47k, debate 50k); 2,254 s per instance with 8
  in parallel; job RAM peak 173.2 GB of 180 GB (mostly page cache from the 145 GB weights;
  close to the limit, watch it).

**Takeaway so far.** The 72B is the first backbone that runs the released pipeline as intended:
clean enough JSON for the released parser, little truncation, and the best localization in the
trial. Its votes and debate are near-unanimous, which is what capability saturation predicts
and leaves adaptive debate little disagreement to exploit. The 72B lenient pass (180368) and the
32B on 2 GPUs (180486/7) are still to come.

Correction (2026-10-02, after a scorer fix for `entity_N` location names): the debate did change
the file-level answer in three 7B order-check runs (fixed-b 20261002-055750: one wrong->right
and one wrong->other-wrong; shuffle seed 3 20261002-061510: one wrong->other-wrong). "0 changes"
holds for the two shakeout runs (20 instance-runs) and every 32B/72B run so far, not for all 7B
runs.

---

## 2026-10-02 — Backbone trial, interim: Qwen2.5-Coder-32B with the released parser (Phase 1, backbone choice)
Config: `ablation/configs/backbone_trial_32b_v1.yaml` · Raw + scores:
`ablation/results/backbone_trial_32b_v1/20261002-065000/` (EEE job 180342; 1 pro6000 highmem,
6 workers, 64k context via YaRN, released JSON parser). Interim: the lenient-parser pass and
both 72B passes are still running; the full comparison will replace this entry.
Provenance note: the fork was updated on disk during this run (opt-in lenient parser added);
with the option off that code path is identical, but the manifest's fork_sha is the start state.

**Numbers** (10 instances):
- Debate collapsed (all five round-1 answers unparseable, upstream crash) on 8/10; 2 completed.
- Up to the vote: gold file in built chains 10/10, kept 9/10, selected chain 7/10.
- Votes lost to unparseable JSON: up to 3 of 5 per instance; surviving votes were unanimous on
  all 10 instances, so the split-vote rate (0/10) is over surviving votes only.
- Hallucinated start entities 74/200 (37%; 7B: 22-27%).
- 0 context-overflow errors at 64k; 95 calls hit max_tokens, mostly `_prefilter_neighbors_with_llm`
  (limit 1000), whose truncated replies also fail to parse.
- 1,308 s per instance (6 sharing one GPU); 388k tokens per instance (graph walk 304k).

**Same model, lenient parser** (`20261002-073451`, job 180367, 1 pro6000, `--lenient-json`):
10/10 completed, 0 collapses; gold file built 10/10, kept 10/10, selected 8/10; Acc@1 (File) 7/10;
debate effect 7 unchanged-right, 2 unchanged-wrong, 1 lost after the debate (empty final plan),
0 changed; split votes 1/10, mean vote agreement 0.94; agents dropped on 1 instance; hallucinated
start entities 67/200 (34%); 670k tokens per instance (graph walk 555k, vote 49k, debate 66k),
3,090 s per instance with 6 workers on one GPU. Parse steps over 2,227 replies: strict 297,
prose-wrapped (first object) 1,754, repaired 140, later object 3, failed 33; 210 calls hit
max_tokens (mostly neighbour pre-filtering, limit 1000).

**Takeaway so far.** With the released parser a 32B backbone has effectively no debate: it wraps
JSON in prose, so votes and analyses are dropped. With lenient parsing it completes every
instance, but Acc@1 is no better than the 7B's (7/10) and the debate still changes no answer.
Lenient parsing also changes the graph walk (more walk steps parse, so the walk goes further:
555k walk tokens vs 304k), so the parser setting is not confined to the debate stage.
These are 1-GPU runs; under the GPU rules the 32B is rerun on 2 pro6000 (`backbone_trial_32b_v2`).

**Truncation at max_tokens** (scorer `truncated_by_stage` / `truncated_fate`; each cut-off
reply's saved text replayed through the lenient parser):

| run | truncated / calls | `_prefilter_neighbors_with_llm` (cap 1000) | other stages |
|---|---|---|---|
| 7B pro6000 shakeout (180200) | 0 / 1,450 | 0 | 0 |
| 32B released parser (180342) | 95 / 1,104 | 94 / 372 (25%) | 1 / 565 node selection |
| 32B lenient parser (180367) | 210 / 2,227 | 209 / 803 (26%) | 1 / 1,208 node selection |

Fate of the cut-off replies: under the released parser all are dropped and the pre-filter falls
back to a heuristic selection (first neighbour per file, no model; corrected 2026-10-02: the
branch is not lost);
replayed leniently, 180342's would give 24 complete objects (the cut fell after the JSON), 64
repaired partial answers, 7 failures; in 180367 they gave 43 complete, 134 repaired PARTIAL
neighbour lists (candidates silently lost), 33 failures (heuristic fallback). The cut-off replies
are per-neighbour prose before the JSON (>= 3 list items first in 87/94 and 199/209); estimated
full reply lengths for the 32B pre-filter: p50 ~875, p99 ~1,870 tokens (decisions.md). Truncation
is a property of the backbone's
verbosity under caps tuned for DeepSeek-V3, concentrated in one stage; pending decision in
decisions.md (2026-10-02, max_tokens caps).

---

## 2026-10-02 — Order check: vote agreement partly reflects display order; released order helps accuracy (Phase 1, precondition)
Config: `ablation/configs/order_check_v1.yaml` · Raw + scores: `ablation/results/order_check_v1/`
(fixed: `20261002-055659` job 180271, `20261002-055750` job 180272, plus the shakeout's
`shakeout10_localization_v1/20261002-044344` job 180200; shuffled: seed 1 `20261002-060609`
job 180273, seed 2 `20261002-060810` job 180274, seed 3 `20261002-061510` job 180275) ·
Analysis: `ablation/results/order_check_v1/order_analysis.json` (`analyze_order.py`).

**Setup.** The 10 shakeout instances, 7B debugging model, all on pro6000 (highmem, 8 workers;
two hardware variants of the chip, see decisions.md). Three runs with the released chain
order, three with the kept chains shuffled before the vote (seeds 1-3, same permutation per
seed for every arm). Pre-registered pass/fail rule in decisions.md 2026-10-02.

**Numbers** (fixed, 30 instance-runs -> shuffled, 29; one shuffled run crashed, see below):
- Winner shown first: 0.77 -> 0.24 (chance 0.17).
- Winner is the longest kept chain: 0.77 -> 0.55.
- Mean vote agreement 0.89 -> 0.87; unanimous votes 0.67 -> 0.55.
- Agreement when the first-shown chain won vs another won: 0.91 / 0.83 -> 0.94 / 0.85.
- Gold file in the selected chain 0.73 -> 0.59; Acc@1 (File) 0.77 -> 0.52.
- One shuffled instance-run crashed when all five round-1 answers failed to parse
  (`debate_collapsed`, sphinx-8056, seed 1; upstream defect, decisions.md).

**Takeaway.** The check does not pass. Under shuffle the first-shown chain wins only a little
more than chance, so most of the fixed-order "position" effect was the longest chain winning on
content; but the longest chain wins less often once it is not shown first, and agreement is
still higher when the first-shown chain wins. Vote agreement therefore carries some position
signal and is not yet a clean confidence measure. Separately, the released longest-first order
is useful: shuffling cost 15-25 points of selection and Acc@1, so the order acts as a prior.

**Caveats.** 7B debugging model; 10 instances; 7 vs 22 instance-runs in the agreement split;
temperature 0.7 noise is large (shakeout runs flipped 2/10 instances). Must be repeated with
the real backbone (decisions.md), where saturation may make votes near-unanimous regardless.

---

## 2026-10-02 — Shakeout, second sample on a pro6000: same totals, different instances (Phase 1, measurement setup)
Config: `ablation/configs/shakeout10_localization_v1.yaml` · Raw + scores:
`ablation/results/shakeout10_localization_v1/20261002-044344/` (EEE job 180200, one pro6000
Blackwell, `-C highmem`, vLLM 0.30.0, `--workers 4`). Compare with the a6000 run below.

**Setup.** Identical to the a6000 shakeout except the GPU and 4 workers instead of 2. This was
the first pro6000 job (Blackwell + RAM test, decisions.md 2026-10-02).

**Numbers** (a6000 -> pro6000, 10 instances each):
- Gold file in built chains 10 -> 10; in kept chains 8 -> 9; in the selected chain 7 -> 9;
  Acc@1 (File) 7 -> 7. Same Acc@1 outcome on 8/10 instances; sympy-18189 went wrong -> right,
  sympy-13647 right -> wrong (lost at stage 4 this time).
- Debate effect: 7 unchanged-right / 3 unchanged-wrong -> 7 / 2, plus 1 new outcome: on
  sphinx-8548 all four surviving agents named a gold file (`importer.py`) but the final
  discriminator returned no plan, so a correct answer was lost after the debate. Across both
  runs the debate changed the file-level answer on 0 of 20 instance-runs.
- Winner was chain_1 in 3/10 -> 9/10. Mean vote agreement 0.86 -> 0.92.
- Agents dropped by JSON parsing: 5 -> 6 instances. Hallucinated start entities 43 -> 54 of 200.
- Tokens/instance 379k -> 351k (graph walk 76-77% in both). Context-overflow calls 5 -> 6.
- Wall clock: 387 s -> 211 s per instance with twice the parallelism; whole job 35 -> 16 min.
- Blackwell works: vLLM 0.30.0 and FlashInfer's JIT kernel ran on sm_120 with no change.
- RAM: a highmem pro6000 job gets 90 GB; 4 workers peaked at 34.8 GB (4.07 GB per worker).

**Takeaway.** Run-to-run variation at temperature 0.7 is as large as any effect seen so far:
the totals look stable (Acc@1 7/10 twice) while individual instances flip, and the chain_1
rate swung from 3/10 to 9/10. Per-instance claims need several seeds, as the design says. Two
findings repeat in both samples: the debate does not change the answer, and answers are lost
around it (stage 4, the vote, JSON parsing, the final plan) rather than by it.

**Caveats.** 7B debugging model; one seed per machine; the two runs also differ in GPU and
vLLM worker count, so they are two samples, not a controlled comparison.

---

## 2026-10-02 — Shakeout: 10 instances, 7B debugging model, a6000 (Phase 1, measurement setup)
Config: `ablation/configs/shakeout10_localization_v1.yaml` · Raw + scores:
`ablation/results/shakeout10_localization_v1/20261002-041812/` (EEE job 180175, one a6000,
vLLM 0.30.0, `--workers 2`). The earlier folder `20261002-040139` is job 180136, which ran
out of RAM after 4 instances (4 workers, 24 GB) and is kept only as a record of that failure.

**Setup.** 10 hand-picked instances (3 sphinx, 4 django, 3 sympy; every difficulty band; two
multi-file gold patches), Qwen2.5-Coder-7B-Instruct bf16, one run, pipeline as released.
Scored with `ablation/harness/score_localization.py`.

**Numbers** (rates over 10 instances):
- Gold file in ANY chain built (graph's job): 10/10.
- Still in a KEPT chain after stage 4's dissimilarity filter: 8/10, so 2 lost before any vote
  (sphinx-8548, sympy-18189).
- In the chain the vote SELECTED: 7/10, i.e. 7 of the 8 where it was still available.
- Acc@1 (File), first file of the final plan: 7/10, identical to selection on every instance.
- Debate effect (round-1 majority file vs final plan file): 7 unchanged-right, 3
  unchanged-wrong, 0 changed. Mean round-1 agreement 0.97; mean vote agreement 0.86.
- The one wrong vote with the gold chain still available (django-11999) was also the one
  split vote (2/5 for the winner); the debate did not change it.
- Winner was chain_1 (always the longest, always shown first) in 3/10.
- Agents dropped by unparseable JSON: at least one in 5/10 instances.
- Start entities not in the graph (hallucinated by stage 2): 43 of 200 attempts (22%).
- Context overflow: 5 calls failed on the 32k-token limit (4 in sympy-13647, 1 in sympy-18189),
  all in `_prefilter_neighbors_with_llm`.
- Tokens per instance: mean 379k (graph walk 290k = 77%, vote 43k = 11%, debate 46k = 12%);
  range 147k-1,092k (sympy-18189). Mean 387 s per instance with 2 in parallel.
- Job RAM peak 24.0 GB of 24 GB with 2 workers (includes reclaimable page cache); 4.07 GB per
  worker process regardless of repository.

**Takeaway.** Pattern only (7B model, n = 10, one seed), but it is the pattern the approved
plan is about: the gold location is lost at stage 4 or the vote, never by the debate; the debate
changed nothing on these instances while costing as much as the vote; and the single split vote
is exactly where adaptive debate would spend its tokens. Most of the cost is the graph walk.

**Caveats.** Debugging model, one seed, temperature 0.7 everywhere; a second sample of the same
10 instances (pro6000, job 180200) is running. Debate effect is file-level; within-file changes
are not yet measured.

---

## 2026-10-01 — Smoke test repeated on the EEE cluster: 3x faster, debate collapsed (Phase 1, setup)
Config: `ablation/configs/smoke_localization_v1.yaml` · Raw:
`ablation/results/smoke_localization_v1/20261001-092851/` (EEE job 179270) · Compare with the
MLDA run `20261001-133650` below. Scores: `scores.jsonl` / `summary.json` in each folder.

**Setup.** Same instance (sphinx-doc__sphinx-8269), same model (Qwen2.5-Coder-7B-Instruct,
bf16), same config, one run each. Differences: RTX A6000 (300 W) vs RTX 3090 (180 W cap), and
vLLM 0.30.0 (FlashInfer sampling) vs 0.9.2, forced by the two machines' drivers.

| | MLDA gpu21 | EEE a6000 |
|---|---|---|
| wall clock | 483.6 s | 158.8 s |
| LLM calls / tokens | 71 / 161,988 | 52 / 130,134 |
| chains built / kept | 12 / 6 | 7 / 6 |
| kept chains containing gold file | 1 | 3 |
| vote | 5/5 for chain_1 (has gold) | 4/5 for chain_3 (no gold) |
| valid debate answers, round 1 / 2 | 4 / 4 | 1 / 0 |
| final plan | `sphinx/builders/linkcheck.py`, correct | `sphinx/linkcheck.py` (does not exist), wrong |

**Takeaway.** The EEE pipeline runs end to end and is ~3x faster per instance. But the same
instance came out right on one machine and wrong on the other. With temperature 0.7 at every
stage and n = 1, that is within what sampling alone can do, so this says nothing about the
machines; it says single runs are meaningless here, which the design already assumes. The real
finding is the debate collapse: 4 of 5 round-1 answers and the only surviving round-2 answer
failed the pipeline's strict `json.loads` ("Invalid control character", i.e. raw newlines or
tabs inside JSON strings, typical when an agent writes code into a field), so the debate ran
on one agent, and the final plan named a file that does not exist (`sphinx/linkcheck.py`).
(Corrected 2026-10-02: first recorded as an empty plan; that was a scorer bug, since fixed.)

**Caveats.** n = 1 per machine, a 7B debugging model. Raw replies were not saved, so the
control-character diagnosis is inferred from the error text; the runner now stores every reply.
Graph pre-build on EEE CPU: sphinx 4 s, django ~50 s, sympy 157-1279 s (sympy-18189: 442k edges).

---

## 2026-10-01 — Smoke test: SWE-Debate localization runs end to end on gpu21 (Phase 1, setup)
Config: `ablation/configs/smoke_localization_v1.yaml` · Raw:
`ablation/results/smoke_localization_v1/20261001-133650/` (`raw.jsonl` = output + every LLM
call; `stage_cache/` = the pipeline's own record of all 8 stages, every vote and debate turn)
Earlier folders in the same directory are the three failed attempts that led to the fixes
(see that directory's README).

**Setup.** One instance, sphinx-doc__sphinx-8269 (gold: `sphinx/builders/linkcheck.py`,
`CheckExternalLinksBuilder.check_thread.check_uri`). Debugging backbone
Qwen/Qwen2.5-Coder-7B-Instruct, bf16, vLLM 0.9.2, one RTX 3090 on MLDA gpu21. Pipeline called
exactly as workflow.py does; graph built by the pipeline itself. Single run, single seed.
Repo `8582411`, fork `2f252f9`.

**Numbers.**
- Completed all 8 stages: 483.6 s wall clock, 71 LLM calls, 0 failed, 0 truncated.
- Tokens: 142,453 prompt + 19,535 completion = 161,988 per instance. By stage:
  graph walk (stages 1-3: entity extraction, neighbour expansion, chain building) 92,371
  (57%), of which chain building alone is 81,656; chain vote 29,148 (18%); debate (two
  analysis rounds + discriminator) 40,469 (25%).
- Chain recall: the gold file is in 6 of the 12 chains built (3 contain the gold function);
  diversity selection keeps 6 chains, of which exactly 1 contains it.
- Vote: unanimous, 5/5 for that chain, mean confidence 90.4. Selection correct.
- Final plan's first edit location: `check_uri` in `sphinx/builders/linkcheck.py`. Acc@1
  (File) correct on this instance.

**Takeaway.** The 30 Sep go/no-go is met: SWE-Debate's localization stage runs end to end
on self-hosted hardware with full token accounting, so the project stays on SWE-Debate (no
switch to LocAgent/CoSIL). The per-stage split is already informative: most tokens go to the
graph walk, not the debate, which matters for any compute-matched comparison.

**Caveats.** n = 1, one seed, a 7B debugging model rather than the real backbone; none of the
numbers above are results. Two behaviours worth counting on every future run: (1) stage 1
named entities that do not exist (e.g. `sphinx/linkcheck.py`; the pipeline drops them with a
warning), and (2) agent 2's round-1 answer was malformed JSON, so it was silently dropped and
only 4 agents debated in round 2. The winning chain was also the first-ranked and longest of
the 6 shown to the voters, so position cannot be ruled out (the ordering control in
CLAUDE.md). `total_chains_generated` reports 20 while `all_chains` holds 12; not yet checked
why.

---

## 2026-09-20 — RQ1: the graph's reachability ceiling is not the bottleneck (Phase 1)
Config: `ablation/configs/rq1_reachability_v2.yaml` · Raw: `ablation/results/rq1_reachability_v2/`
(`raw.*.jsonl`, `summary.json`, `graph_quality.json`, `manifest.*.json`)
Sensitivity arms: `..._v2_strict.yaml`, `..._v2_loose.yaml`

**Setup.** All 75 SWE-Bench-Verified-S instances (django 25, sympy 25, sphinx-doc 25), 0
failures. No LLM and no GPU. SWE-Debate's own `build_graph` (v2.3, `global_import=True`,
`fuzzy_search=True`), imported unmodified from the fork, run at each instance's base commit.
The gold patch is mapped onto graph nodes (file node, plus the innermost class/function node
spanning each changed pre-image line), and hop distance is measured from a deterministic
stand-in for stage-1 entity extraction: every non-test node whose short name appears verbatim
in the issue text (see decisions.md 2026-09-20). Reported under five edge policies, including
one faithful to `_dfs_traversal` and one that keeps only invoke edges the builder actually
resolved.

**The ceiling, such as it is.** Every gold file in all 75 instances is a Python file, is
present as a graph node, and survives the test-name filter. The gold file is reachable from an
issue-named entity within 2 hops in 96% of instances and within 4 hops in 100% (0 unreachable
under the faithful policy; 1 under dependency edges alone). The gold class or function is
reachable within 3 hops in 97%. Nothing about the graph's connectivity stops SWE-Debate from
finding the answer.

**But the number means almost nothing, which is the actual result.** Measured against the
control — how much of the repository sits inside k hops of the same entry set — the traversal
stops carrying information almost immediately:

| hops | gold FILE reached | share of repo reachable | enrichment | candidate files |
|---:|---:|---:|---:|---:|
| 0 | 42.7% |  2.1% | 20.0x |  10 |
| 1 | 86.7% | 19.7% |  4.4x |  67 |
| 2 | 96.0% | 64.7% |  1.5x | 355 |
| 3 | 97.3% | 84.2% |  1.2x | 476 |
| 4 | 100.0% | 89.2% |  1.1x | 507 |

(`no_dir` policy; enrichment is how much likelier the gold file is to be inside k hops than an
arbitrary file. 1.0x means the traversal has told you nothing.) For class/function targets the
collapse is sharper: 91.4x at hop 0, 11.3x at hop 1, 1.9x at hop 2, 1.1x at hop 3, by which
point the reachable set averages 11,032 entities. `_dfs_traversal` runs to depth 5.

**The signal is in the issue text, not the graph.** Splitting instances by entry-set size, the
bottom quartile (1-14 nodes named) reaches the gold file 61% of the time at 1 hop and 89% at
3; the top two quartiles reach 100% at 1 hop. The single hardest instance
(`sphinx-doc__sphinx-9367`, gold file unreachable through dependency edges alone) has an entry
set of one node: its issue text is a code snippet that names nothing the graph can match.

**Robustness.** The pattern is unchanged across three entry-set definitions whose median size
differs three-fold (strict 16, default 35, loose 46) and across all five edge policies,
including `resolved_only`, which drops every ambiguous invoke edge. Enrichment at hop 3 is
1.2x or lower in all fifteen combinations.

Takeaway for H1: graph grounding's contribution cannot be a reachability effect — the gold
location was always reachable. If multiple chains help, they help by *ordering* candidates,
not by making them available, and that is the mechanism the Phase 1 factorial has to isolate.
The recall/selection split matters even more than expected: chain recall is near-ceiling by
construction, so essentially all of the observed accuracy is selection precision.

Caveats: the entry set is a deterministic upper bound on stage 1, not the real LLM output, so
these are ceilings and not predictions of measured accuracy. 20 of 75 instances have at least
one changed line outside any class/function node (module-level code), so entity-level gold
sets are partial for those. Single run, but the measurement is deterministic — reachability
has no seed.

---

## 2026-09-20 — The graph is mostly unresolved name matches (Phase 1, supporting)
Config: same run · Raw: `ablation/results/rq1_reachability_v2/graph_quality.json`

`build_graph` never resolves a call to one callee. It matches the called name against the
caller's visible scope and keeps every node sharing that short name; if the name is not
visible and `global_import` is on (which is what `batch_build_graph.py` uses), it wires the
caller to every node in the repository with that name. Grouping invoke edges by
(source node, callee short name), any group larger than one is a name match that was never
resolved:

| repo | invoke edges | unresolved | largest single group | ambiguous entity names |
|---|---:|---:|---:|---:|
| django/django | 176,612 | 80.0% | 618 | 11.5% |
| sympy/sympy | 296,020 | 74.9% | 438 | 12.1% |
| sphinx-doc/sphinx | 31,515 | 77.0% |  98 | 19.4% |

Invoke edges are 77.5% of all edges. One django call site naming `get` is wired to 618
different methods. The median ambiguous group has 3-4 targets.

Also measured: the `is_test_file` filter hides 67-68% of file nodes, which is mostly the
intended test suite, but it also takes shipped production code with it — the whole of
`django/test/` (12 files: `django.test.Client`, `TestCase`, the runner), `sphinx/testing/`
(6 files), and 2-28 sympy files, mostly `autolev` parser fixtures. None of the 75 gold files
falls there, so it does not bite on this subset, but on a broader dataset those files are
automatic misses. Separately, no file in any of the 75 graphs failed to parse (0 orphan file
nodes), so the AST builder handles these repositories cleanly.

Takeaway: this is the strongest reason yet to be careful with Phase 2's primary candidate.
"Graph-grounded debate" assumes an agent can cite a checkable graph fact; four in five invoke
edges are not facts. Raised in for-chat.md. It also partly explains the reachability collapse
above — though only partly, since the `no_invokes` and `resolved_only` policies show the same
collapse, so containment and imports alone already connect most of the repository.

Caveats: the split between the local-fuzzy branch and the global fallback is not recoverable
from a finished graph, so the two are counted together as "unresolved". No claim is made about
which member of a group is the true callee.



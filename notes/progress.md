# Progress Log — FYP A3062

One entry per work session, newest at the top. Format:

## YYYY-MM-DD
Did:
Broke:
Next:

## 2026-10-09
Did: Scored round1_only seed 2, adaptive seed 5, noise-floor reruns seeds 2 and 4. New
`paired_arms.py`: adaptive single-agent over 5 paired seeds -0.9 points vs the original-arm mean
[-2.8, +0.9], one-sided lower -2.4 (non-inferior at 3 points), -40% stage 6-7 tokens; noise floor
4.3% discordance vs adaptive 4.5%; round1_only worse (1:8, p=0.04) -> dropped. Fixed the job script's
requeue lookup (killed Live repair 192683 under pipefail); repair resubmitted (194629). Queued rerun
seed 5, adaptive seed 6, SC reuse seeds 4-5 behind lenient seed 6.
Broke: Live repair 192683 FAILED (job-script bug, fixed). The watcher missed completions overnight.
Queue: ug 186753 seed 6 (running) -> 194636 rerun s5 -> 194637 adaptive s6 -> 194638 SC s4 -> 194639
SC s5 | killable 184607-9 Live a-c, 184861 shuffle 2, 194629 Live seed-2 repair (all pending).
Later: lenient seed 6 done (0.747; original mean 0.751 over 6 seeds); replay 6 seeds unanimous -0.1
[-1.6, +1.4]; lp_conf held out never beats agreement. Noise-floor rerun seed 6 queued (195345).
Next: score the queued runs and rerun paired_arms.py; re-fetch the Live seed-2 pilot after repair.

## 2026-10-08
Did: Scored the two noise-floor reruns (original arm re-run on its own chains: 2:6 vs the first run,
5.3% discordant; seed 1 rerun 0.720 vs 0.773) and adaptive seed 4 (0.733 = 0.733). Adaptive over 4
paired seeds 4:10 (p=0.18), discordance 4.7% (= noise floor), -40% stage 6-7 tokens; vs the mean of
all original-arm runs -1.3 points [-3.3, +0.7]. Queued round1_only adaptive seeds 3, 1, 2 (192116-
192118) after lenient seed 5 (running); seed 6 re-pointed behind them.
Broke: Nothing.
Queue: ug 186752 seed 5 (running) -> 192116 -> 192117 -> 192118 -> 186753 seed 6 | killable 184607-9
Live a-c, 184861 shuffle 2, 186864 Live seed 2 (all pending for days: no idle pro6000).
Later: lenient seed 5 done (0.680; original mean 0.752 over 5 seeds); adaptive seed 5 queued (192615,
reuse of seed 5) before seed 6; Live pilot seed 2 (186864) finally got killable cards.
Live pilot seed 2 finished but is invalid: 33/40 instances recorded ok after a dead-server first call.
Fixed the runner (infrastructure call failures -> status error, always rerun on resume; scan of all
runs: only this run affected; the 151 other call failures are context-length errors in the stage-3
pre-filter, logged in deviations.md). Repair 192683 queued on killable in place of the pending Live
seed-2 part a (192675, cancelled; resubmit when a killable slot frees). Live parts a, b running.
Round1_only adaptive seed 3: 0.773 vs 0.813 (1:4) at 74k tokens; corrected the skipped/debated
subset reading (conditions on the arm's own vote; only totals are fair). Noise-floor rerun seed 2
queued (192818) after round1_only seed 2; adaptive seed 5 re-pointed behind it.
Round1_only seed 1: 0.733 (original 0.773, rerun 0.720, single-agent 0.747). Noise-floor rerun seed 4
queued (193013) after rerun seed 2; adaptive seed 5 re-pointed behind it.
Next: re-fetch and score the repaired seed-2 pilot; score round1_only seeds; adaptive seed 6 after lenient seed 6; consider noise-floor
reruns on seeds 2 and 4; the killable lane is starved, so Live has made no progress since the pilot.

## 2026-10-07
Did: Scored the first real adaptive run (paired with seed 3): 0.787 vs 0.813 (2:4, p=0.69) at -38%
stage 6-7 tokens; the gap sits on the 17 split-vote instances where the same released debate was
re-run (12 vs 16), not on the 58 skipped (0.81 vs 0.78). Reuse-chains SC seed 2: 0.733 vs 0.760;
reuse SC pooled 3:8 (p=0.23). Queued adaptive seeds 1 and 2 (189312, 189313, reuse) ahead of
lenient seed 5 (re-pointed).
Broke: Nothing.
Queue: ug 184812 lenient seed 4 (running) -> 189312 adaptive s1 -> 189313 adaptive s2 -> 186752 s5
-> 186753 s6 | killable 184607-9 Live a-c, 184861 shuffle 2, 186864 Live seed 2 (all pending).
Next: score adaptive seeds 1-2 and pool (3 paired seeds); replay with lp_conf held out once seeds
4-6 land; Live parts when the killable lane gets cards.
Later (new session, 10:30): no job ended; lanes full, killable all pending. Power calculation for
the adaptive non-inferiority claim (3 paired seeds prove only ~4-5 points; 3 points needs ~5-10
seeds of 75 or ~1-2.5 runs of Lite) parked in for-chat.md. Planned (decisions.md 2026-10-07): a
noise-floor control (original arm re-run on its own chains, config baseline_72b_rerun_lenient_v1,
copied to EEE) and adaptive seeds 4-6; queue both as ug slots free (next: when seed 4 ends).
Seed 4 done (0.733; original arm mean 0.770 over 4 seeds); noise-floor rerun on seed-3 chains
queued (189863, SEED=103) after adaptive s2, seed 5 re-pointed behind it. Replay over 4 seeds:
unanimous-skip -0.2 [-1.9, +1.8] at -39% tokens. Scorer fix for a '₁' logprob token. Scratch venv
recreated (json_repair, pyyaml) after the session restart.
Adaptive seed 1 done: 0.747 vs 0.773 (1:3), -41% tokens; pooled seeds 1+3 3:7 (p=0.34), -40%.
Adaptive seed 4 queued (190072, reuse of seed 4) after the noise-floor rerun; seed 5 re-pointed.
Adaptive seed 2 done (0.733 vs 0.760, 0:2). Three paired seeds: 0.756 vs 0.782, 3:9 (p=0.15),
-40% tokens, losses mostly on skipped instances -> built skip_mode round1_only (five round-1 agents,
no round 2), unit tests moved into the repo (test_arms.py), gpu21 check ok (11 calls). Config
baseline_72b_adaptive_r1_lenient_v1 on EEE; queue r1 seeds 1-3 as ug slots free. Second noise-floor
rerun (seed-1 chains, 190480) queued.

## 2026-10-06
Did: Fetched and scored lenient seed 1 (0.773, vote logprobs) and self-consistency seed 1 (0.707);
replay over 3 lenient seeds (skip-on-unanimous -0.4 points at -39% stage 6-7 tokens; debate's few
fixes name files outside the chosen chain; correction to 2026-10-05 in results.md). Built
`--reuse-chains` (stages 1-4 from a reference run): unit-tested on 75 cached instances and end to end
on MLDA gpu21 with the 7B (smoke_reuse_chains_v1, stages 1-5 identical). Live pilot finished 39/40;
repair of beets-5437 queued (186745, killable). Lanes refilled: ug lenient seeds 5-6 (186752,
186753, vote logprobs) after seed 4; killable has Live parts a-c, second shuffle, pilot repair.
Broke: Nothing. The EEE watcher missed three completions while the Mac was off (checked manually).
Queue: ug 184574 SC seed 2 (running) -> 184575 SC seed 3 -> 184812 seed 4 -> 186752 seed 5 ->
186753 seed 6 | killable 184607-9 Live a-c, 184861 shuffle 2, 186745 pilot repair.
Later: Jingwei confirmed --reuse-chains; SC seed 3 own-chains run left to finish (already 34/75),
reuse-chains SC seed 3 queued after it (186863; seed 4 re-pointed behind it). Runner synced to EEE.
SC seed 2: 0.773 (SC seeds 1-2: 0.740 vs original 0.782). Live pilot repaired and scored: 0.575,
debate 3 broke / 0 fixed (results.md). Live seed 2 started on killable with its first 40 (186864).
SC seed 3 own chains done (0.773; own-chains SC mean 0.751 vs 0.782, -3.1 [-8.0, +1.3]); reuse-chains
SC seed 3 running (186863); reuse-chains SC seed 1 queued after it (187444), seed 4 re-pointed behind.
Reuse-chains SC seed 3 done (1 h 07; 0.840 vs the debate's 0.813 on identical chains, 3:1 discordant,
p=0.63); reuse-chains SC seed 2 queued (187682) after seed 1 (187444); seed 4 re-pointed behind it.
Reuse-chains SC seed 1 done: 0.707 vs debate 0.773 on identical chains (0:5; pooled with seed 3 3:6,
p=0.51; the lone plan agent is the weak step). Adaptive arm built (unanimous vote -> skip the debate),
unit-tested and run end to end on gpu21 (smoke_adaptive_v1: skipped, 7 calls); 72B adaptive paired
with seed 3 queued (188238) after SC-r2 (187682); seed 4 re-pointed behind it. Live seed 2 preempted
at 15/40, requeued.
Next: score SC-r2 and adaptive-r3; queue adaptive seeds 1-2 (reuse) as ug slots free; replay with lp_conf held out once seeds 4-6 land; adaptive
arm (real run) after the chain-debate question is settled.

## 2026-10-05
Did: Scored the 72B order check at scale (lenient fixed seed 2 vs shuffled): primacy bias in which
chain wins (positions 1..6 win 22/18/15/9/5/6 vs ~13 chance), vote agreement not order-dependent
but saturated; first real vote logprobs: lp_conf below 0.9 on a third of instances and 80% vs 64%
selection accuracy above/below it (results.md, decisions.md). 7B SWE-bench-Live smoke test: works
end to end (40/40). Fixed a second lenient-mode shape crash (final plan with string entries,
django-12155 in seed 2); added `--resume --retry-errors`. Queued the seed-2 repair (184567,
killable) and self-consistency seeds 2-3 (184568, 184569; ug, chained after 183711).
Broke: Nothing. The killable watcher missed a job that finished before its first look (fixed by
checking manually); the 72B Live pilot is being preempted repeatedly but resumes correctly.
Both-lanes rule (decisions.md 2026-10-05, memory updated): killable lane filled with the rest of
the 72B Live seed in three parts, live_72b_lenient_{a,b,c}_v1 (184607-184609; pilot + parts = 386).
Trigger replay (no GPU): `replay_trigger.py`; at 72B lenient, always skipping the debate matches
it at ~half the stage 6-7 tokens and no lp_conf/agreement threshold beats that; ~85% of errors are
vote selection failures the plan debate cannot reach (results.md; for-chat item on debating the
chain choice). MLDA gpu21 now usable 24/7 (memory). Live pilot: beets-5437 hit the pre-fix
stage-8 shape crash; rerun it with --resume --retry-errors when the pilot ends.
Lenient seed 3 done (0.813; replay agrees: skip 0.805). Seed 4 (184812, vote logprobs) queued on
ug after 184575 to keep the lane full and give lp_conf a second fixed-order run for held-out
thresholds. Seed-2 repair (184567) done: django-12155 ok, seed 2 raw.jsonl replaced by the EEE copy
(only that line differed), rescored; Acc@1 unchanged 0.760; replay updated (results.md).
Killable slot refilled: second shuffle seed `order_72b_lenient_shuf2_v1` (184861; chain_order seed 2,
vote logprobs) to check the primacy gradient on another permutation.
Queue: 183233 lenient seed 3 (DONE) (running, 53+/75) -> 184572 seed 1 -> 184573 SC seed 1 -> 184574 SC
seed 2 -> 184575 SC seed 3 (ug, pro6000; the four not-yet-started jobs 183310/183711/184568/184569
were requeued with --vote-logprobs 10, which does not change outputs, so the trigger can be
evaluated on the original arm) | killable pro6000: 183679 72B Live pilot (15/40, requeue-
resuming), 184567 seed-2 repair, 184607-184609 Live parts a-c. Lenient seeds 2 and 3 have no vote logprobs; seed 1, the shuffled
run and all self-consistency seeds will.
Next: when seeds 3 and 1 land, pool the lenient original arm (3 seeds) and compare with the
as-released row; build and evaluate the adaptive trigger on lp_conf (needs vote logprobs on the
original-arm runs too: the lenient seeds ran without them, so either reuse the shuffled run or add
--vote-logprobs to future arms); score the self-consistency arm as it lands; finish the Live pilot.

## 2026-10-04
Did: EEE reachable again; everything from 2026-10-02 had finished. Scored the 72B as-released
baseline, 75 instances x 3 seeds (Acc@1 File 53/54/57 of 75 = 73%; debate net effect ~0 over 225
instance-runs; 12 answers lost to discriminator JSON failures; ~10% split votes; results.md) and
the 72B released-vs-lenient parser comparison. GPU-wait sampler summarised (thin coverage; chained
jobs keep the lane within ~10 s; observed fresh waits 13-59 min; decisions.md). Decided with
Jingwei: lenient parsing for every arm of the main experiment, released max_tokens caps. Built
while EEE was unreachable (2026-10-02 evening): vote logprobs (--vote-logprobs), SWE-bench-Live
loader (388 verified instances after 2024-09-19), equal-token self-consistency arm (per-instance
budgets, glob references). Synced to EEE.
Broke: Nothing. Sampler coverage was poor (Mac sleep); Live cutoff still to confirm.
Update ~07:15 UTC: 183230 (lenient seed 1) was CANCELLED after ~25 min: lenient parsing let a
wrongly shaped reply (locations as strings) reach the discriminator, which crashed the instance.
Fixed in the fork (lenient-only shape normaliser, deviations.md), synced, and seed 1 requeued as
183310 at the end of the chain so every lenient run uses the same code. 183230's partial output
on EEE is discarded (not a result). New chain: 183231 shuffle -> 183232 seed 2 -> 183233 seed 3
-> 183310 seed 1. Live graphs: 183253 aborted on a commit reachable only by sha, 183282 OOM at
12 GB on azure-sdk-for-python; builder fixed (fetch by sha, per-graph memory cap, skip+record),
rerun as 183289 with 48 GB.
Queue on EEE (submitted 2026-10-04 ~06:00 UTC):
  183230 original arm, lenient, SEED=1 -> 183231 shuffled order (seed 1, lenient, vote logprobs)
  -> 183232 original lenient SEED=2 -> 183233 original lenient SEED=3 (2x pro6000, 12 h limits,
  ~8 h each) | 183234 Live prep (CPU: dataset + 40-instance pilot graphs) DONE: dataset on EEE
  matches the Mac's (388, revision b51a8642), 40 pilot graphs (369 MB), clones ~2 GB for the pilot
  | 183253 graphs for all 388 Live instances (CPU, free; est. 6-8 GB clones, ~3.6 GB graphs).
Killable QoS (second pro6000 lane, decisions.md): 183679 72B Live pilot and 183710 7B Live smoke,
both 2x pro6000 under override-limits-but-killable (idle cards only; requeue-safe). 5th ug slot:
183711 self-consistency seed 1, after 183310 (pro6000-first rule; l40 smoke 183697 cancelled).
Cancelled 183230 folder moved to ablation/results/_discarded/ on EEE.
Next: score each lenient seed as it lands (compare with the as-released row); after 183231, the
order analysis at 72B scale (analyze_order.py vs 183230) and the first real vote-logprob signal
(lp_conf when selection right vs wrong); then queue the self-consistency arm x 3
(`baseline_72b_sc_lenient_v1.yaml`, after 183233) and the Live pilot run. Confirm the Live cutoff.

## 2026-10-02
Did: Second day of the same Claude Code session (all EEE work driven by Claude, with Jingwei's
OK). Shakeout x2 (a6000, pro6000); order check (fails weakly: agreement partly order-driven,
released order helps accuracy); GPU rules (2x pro6000 for 32B/72B) and a 24 h queue-wait sampler;
backbone trial 32B vs 72B (72B chosen: 10/10, Acc@1 9/10, no collapses); opt-in lenient JSON
parser in the fork; truncation measured (pre-filter cap; 2,048 candidate); runner --resume and
SEED; scorer: stage-by-stage recall, debate effect, truncation, parse fates. All in results.md,
decisions.md, deviations.md.
Broke: Nothing open. Known risks: 72B RAM peak 173/180 GB at 8 workers (runs now use 6);
pre-filter truncation and parser setting undecided; the debate rarely changes answers.
Queue on EEE at hand-off (in order):
  180368 72B lenient trial pass (running, gpu-pro6000-9)  |  180724 all 75 code maps (CPU, running)
  -> 180726 72B released, 65 instances (seed 1 with 180343; after 180368 + 180724, 14 h)
  -> 180739 72B released, 75 instances, SEED=2 (14 h)  -> 180740 same, SEED=3 (14 h)
  Cancelled: 180486/180487 (32B on 2 GPUs).
Check first next session:
  1. Score 180368 (72B lenient) and decide the parser setting; if it changes, cancel 180726,
     180739, 180740 and resubmit with --lenient-json (decisions.md 2026-10-02).
  2. 180726's progress, RAM peak and split-vote rate; then queue the deferred 75-instance
     shuffled-order 72B run (--shuffle-seed 1) after 180740, or skip it if split votes are ~0.
  3. GPU-wait sampler on the Mac (PID in ablation/results/gpu_wait_v1/sampler.pid; samples.tsv,
     gitignored; gaps when the Mac sleeps or is off NTUSECURE are logged as skipped). After 24 h
     (from 2026-10-02 08:35 UTC) write the time-of-day summary and the practicality verdict into
     decisions.md ("GPU rules"), and commit samples_final.tsv.
  4. Caps decision (pre-filter 1,000 -> 2,048 candidate) with the 72B truncation numbers.
Next (build objectives): the equal-token single-agent arm; the adaptive-debate arm (trigger
pending the order-check outcome); saving vote logprobs (vLLM supports them) as an
order-independent trigger signal; a SWE-bench-Live loader for plan item 3; possibly SEEDS
bundling in the job script (decisions.md, after the sampler summary).
Final side-chat items: idle-gap order check NOT done (Jingwei: leave the queue); pass bundling
recorded as a proposal (decisions.md); backbone-strength threat, why-self-host wording and
interim-report framing added to for-chat.md with the side chat's benchmark and price figures
marked to be checked. At 12:33 UTC the code-map build was at 27/75 (sympy now, ~1.5-2.5 h left)
and 180368 had finished 1/10 (django-11880 ok, 1,550 s).
Later (21:00 SGT, Mac off the NTU network, EEE unreachable): built vote-logprob capture
(`--vote-logprobs K`, default off; scorer lp_conf / lp_margin / lp_entropy), unit-tested with
mocks, not yet run on vLLM; committed, NOT yet synced to EEE (safe: off by default). Scorer: the
truncation replay now reports `repair_unavailable` when json_repair is missing instead of
miscounting; score with an environment that has json_repair.
Also offline: SWE-bench-Live loader (388 verified instances after 2024-09-19, pinned revision,
shared instance source; draft config live_72b_released_v1) and the equal-token single-agent arm
(self-consistency, per-instance budget; draft config baseline_72b_selfconsistency_v1). Both
unit-tested, neither run on GPUs yet; none of it changes the default path the queued jobs use.

## 2026-10-01
Did: Status review; no code or experiments. Noted that decisions.md and the plan were changed
on 2026-09-22 with no progress entry: GPU access secured (MLDA + EEE cluster), and a proposed
change of direction to adaptive debate, pending A/P Chen. Walked Jingwei through using MLDA
(direct SSH to one shared workstation, no queue) versus the EEE cluster (login node + Slurm
`sbatch`); no commands run on either. Read the EEE docs: the AI digest is now `skill.md`
(`agent.md` is gone; CLAUDE.md link fixed). Their terms ban serving a personal chatbot or
inference endpoint; Jingwei ruled that vLLM inside a research job is fine (decisions.md).
Broke: Git failed on this Mac until the Xcode license was accepted, so the SessionStart pull
failed and the stop hook's session-start SHA was empty (fixed by hand; the 2026-09-22 edits
were already pushed). The 30 Sep go/no-go passed without an end-to-end SWE-Debate instance.
Later: Jingwei confirmed SSH key login to gpu21 and a changed password; gpu21 is 4x RTX 3090
(24 GB). Recorded the hardware and the open backbone choice (32B 4-bit vs 14B bf16, in
for-chat.md). Wrote the one-instance smoke test: config `smoke_localization_v1.yaml`, runner
`ablation/harness/run_localization.py` (calls the pipeline as workflow.py does, logs tokens per
call and per stage), and step-by-step gpu21 setup in `ablation/gpu21/README.md`. Fork change:
the hardcoded 60 s per-call timeout now follows LLM_TIMEOUT (deviations.md). The runner is
compiled but not yet executed anywhere: this Mac has no Python 3.12 env with the fork's deps.
Then, the same session: Jingwei did the gpu21 setup by hand with step-by-step guidance and ran
the smoke test. SWE-Debate's localization stage ran end to end on sphinx-doc__sphinx-8269
(483.6 s, 71 calls, ~162k tokens, correct file; results.md). Go/no-go met (decisions.md).
Fixes found on the way, all in the repo: vLLM pinned to 0.9.2 + transformers 4.53.x (newest
vLLM needs CUDA 13, gpu21's driver is 12.7); `ablation/gpu21/requirements-swed.txt` (litellm
1.52.1 gone from PyPI, five missing moatless deps, jiter 0.5.0); git via conda; the pipeline
needs full graphs, not RQ1's code-stripped ones (`data/graphs_full`); manifest date bug.
Also: EEE cluster login works (user i230002, key-based `ssh eee`). Verified two code findings
from a side chat and logged them in deviations.md: all five agents get identical prompts
(the paper says different ones), and stage 4 keeps chains by dissimilarity to the longest,
not by relevance, and always shows the longest first.
EEE cluster, same session, all typed by Jingwei: login and key auth, limits read (ug QoS:
2 GPUs/model, 180k SU/month; 32B bf16 fits there), SSD project folder /projects/fypA3062 with
caches redirected, first srun and sbatch jobs, job dependencies. Built `ablation/eee/`
(setup_envs.sh CPU job: vLLM 0.30.0 + pipeline env + models, succeeded; build_graphs_job.sh;
run_localization_job.sh with server + pipeline in one job). The EEE smoke run needed two fixes:
nvcc for FlashInfer's JIT sampler (CUDA/13.0.0 module) and a libstdc++ clash with the GCC
module (scoped to the vLLM process). Job 179270's server reached "startup complete"; the run
result was not yet seen when the session ended. Also built: score_localization.py (built ->
kept -> selected recall, Acc@1 File, chain_1 wins, dropped agents, debate before/after),
parallel worker processes in the runner, build_full_graphs.py, shakeout10 config. A/P Chen
approved the adaptive-debate direction (decisions.md, committed from another session);
CLAUDE.md rewritten to match.
Broke: Nothing known. Unverified: the runner's parallel mode (shakeout will test it).
Later (2026-10-02, same session): EEE job 179270 finished: ok in 158.8 s (3x MLDA), but 4/5
round-1 debate answers failed the pipeline's strict JSON parse, the vote picked a chain without
the gold file, and the plan came out empty (results.md). Graph job 179267 built all 10 full
graphs (sympy-18189 took 21 min). Runner now saves every reply's text; parser decision pending
(decisions.md). Fixed: results rsync must be one-way (`--ignore-existing`); a two-way sync
overwrote local score files. Explained the 20-vs-12 chain count: one attempt per stage-2 start
entity, and attempts whose entity id is not in the graph come back empty: 8/20 (MLDA) and 13/20
(EEE) start entities were hallucinated. Scorer now counts them. Jingwei now lets Claude submit
EEE jobs too (memory).
Then: shakeout run twice. a6000 (job 180175, 2 workers, after an OOM at 4 workers and a
`module: command not found` from a non-interactive submission, both fixed) and pro6000
(job 180200, first Blackwell + RAM test, 4 workers, 90 GB RAM). Acc@1 (File) 7/10 both times,
8/10 instances agree; the debate changed no file-level answer in 20 instance-runs; losses come
from stage 4, the vote, JSON parsing and the final plan (results.md). New rules from Jingwei:
Claude submits EEE jobs, always on the best free GPU via `ablation/eee/pick_gpu.sh`, which now
also picks the GPU count; budget is not a constraint (decisions.md). Scorer: hallucinated
start entities, plan-failed outcome, plan locations in any format. Runner: fresh process per
instance, retries after a killed worker, peak RAM logged, reply text saved.
Broke: Nothing open. Known limits: 32k context overflows on sympy (64k planned, decisions.md);
JSON parse losses (parser decision pending, decisions.md).
Later: order check done (failed weakly; agreement partly order-driven, released order helps
accuracy; decision pending). Backbone trial set up per Jingwei (Qwen2.5-Coder-32B on 1 pro6000
vs Qwen2.5-72B on 2, pinned, 64k via YaRN; 72B weights on new HDD folder /projects/fypA3062models).
32B with the released parser: 8/10 debate collapses (JSON wrapped in prose) -> opt-in lenient
parser added to the fork (default off). Jobs queued: 32B lenient (180367, running), 72B released
(180343), 72B lenient (180368). Fixed on the way: download script fetched no weights; YaRN
override needs rope_parameters + scaled max_position_embeddings in vLLM 0.30.
Later still: 72B released-parser trial done (10/10, Acc@1 9/10, 0 collapses; results.md).
Lenient parser made opt-in in the fork; truncation measured (32B pre-filter ~25%, 72B 5.6%;
caps decision pending with a 2,048 candidate); runner --resume; GPU rules (2x pro6000 for
32B/72B) with pick_gpu.sh rewritten; 24 h queue-wait sampling running on the Mac. Submitted:
180724 (CPU: all 75 full code maps, baseline_75_v1.yaml) and 180726 (72B on the other 65
instances, 180343 settings, after 180487 and 180724; cancel if 180368 changes the parser
decision). Queue: 180368 72B lenient running; 180486/180487 32B on 2 GPUs; then 180726.
Next: score 180368 (parser decision; cancel 180726 if it changes), score the 32B v2 runs (2-GPU
time for the job-structure decision), write the backbone comparison into for-chat.md, summarise
the 24 h GPU-wait sampling (commit samples_final.tsv), then decide backbone, parser and caps.
Ask A/P Chen about her EEE project QoS. New hypotheses (for-chat.md).

## 2026-09-20
Did: First real measurement of the project. Built the RQ1 harness
(`ablation/harness/{swe_graph,reachability,analyze_reachability,graph_quality}.py`, config
`ablation/configs/rq1_reachability_v2.yaml`) and ran it over all 75 SWE-Bench-Verified-S
instances with no LLM and no GPU — see results.md for the numbers. Headline: the graph's
reachability ceiling is not the bottleneck (gold file reachable within 2 hops in 96% of
instances, 100% by 4 hops, 0 unreachable), but the control shows why that is almost vacuous —
by hop 3 the traversal has 84% of the repository in reach and the gold file is only 1.2x
likelier to be in that set than any other file. The traversal's information is spent in the
first one or two hops; `_dfs_traversal` runs to depth 5. Robust across three entry-set
definitions and five edge policies. Supporting result: 75-80% of the graph's `invokes` edges
are unresolved name matches (one django call site naming `get` is wired to 618 methods), and
invokes is 77.5% of all edges.
Also: fixed five hardcoded values in the fork (empty API credentials, the dead `model_name`
argument, and three absolute paths at the filesystem root) so the pipeline can start at all;
found that `localization/requirements.txt` omits `transformers`, which `entity_embedding.py`
imports at load, and that the localization stage quietly needs a second model (a 2.2 GB local
embedding model for chain diversity). Made the graph builder 6-12x faster by hoisting a
per-entity file read and line split out of `CodeAnalyzer` — verified graph-identical against
pre-fix builds on three instances; a sympy graph went from 44 min to 6-8 min. Corrected the
subset composition to 25/25/25 (it was recorded as 23/26/26). Narrowed `.gitignore` so raw run
output is tracked, and started exporting the gitignored fork's changes to
`ablation/patches/`.
Broke: Nothing regressed. Two things are slower or uglier than they should be. (1) The graph
builder still spends ~50% of its time in `find_all_possible_callee`, which redoes per-file
import resolution once per entity; the file-level part of it is cacheable and provably
identical, and it matters for Phase 3 where hundreds of graphs are needed. (2) The 75 graph
builds took 10.6 CPU-hours total even after the fix. Still no SWE-Debate end-to-end run: that
needs an LLM endpoint, so it is blocked on GPU access, not on the code.
Next: 30 Sep decision point — get one SWE-Debate instance through the localization stage end
to end as soon as an endpoint exists; the non-LLM parts are now unblocked. Cache the file-level
part of `find_all_possible_callee`. Confirm localization-only scope with A/P Chen. Pick the
backbone once GPU memory is known. Read A1-A9. Chat has two new questions in for-chat.md,
including whether the unresolved-edge finding weakens Phase 2's primary candidate.

## 2026-09-19
Did: Project plan submitted 14 Sep. Plan discussion with A/P Chen: she read it as a
reproduction and suggested testing other datasets and modifying the debate, so the plan is now
three phases (diagnose, modify, validate) — see decisions.md and FYP_A3062_Project_Plan.md.
Renamed the 41 PDFs in papers/ to their titles with A/B/C/D reading-order labels
(notes/reading-order.md). Added a SWE-bench-Live entry to literature.md and wrote
notes/literature-summary.md. Found that "Agent Scaling Science" is the preprint of the Nature
MI paper (one study, not two), and that SWE-Debate's -4.2 debate effect is end-to-end Pass@1,
not localization — gap statement corrected in decisions.md. Updated CLAUDE.md. Moved the
repo out of iCloud to ~/IM4080/FYP-A3062 (fresh clone plus copied papers and swe-debate).
Broke: No SWE-Debate run recorded yet. DeepSeek-V3-0324 is no longer served by DeepSeek, so
the backbone moves to a self-hosted open model (deviations.md). GPU access pending: MLDA
application first, at the supervisor's request.
Next: Get one SWE-Debate instance running end to end by 30 Sep, or switch to LocAgent/CoSIL.
Start the reachability measurement (no GPU needed). Confirm localization-only scope with
A/P Chen. Pick the backbone once GPU memory is known. Read A1-A9.

## 2026-09-13 (3)
Did: Reviewed the big 29-paper batch dropped in papers/, added a literature.md entry for
every one. This was the real haul — most of the project's actual reference list, not just
cross-domain flavor:
- SWE-Debate itself (arXiv:2507.23348), read in full against the earlier repo inspection.
  Confirmed exact ablation numbers (chains -10.0, edit plan -6.0, debate -4.2), confirmed the
  "3-round debate" is actually 2 agent rounds + 1 discriminator round, confirmed the 5 agents
  are one DeepSeek-V3-0324 model under different system prompts (paper's own words, Sec 6.2),
  confirmed zero cost reporting anywhere, confirmed the 75-instance subset is django+sympy+
  sphinx-doc (three repos, not two as previously assumed). Full discrepancy list written to
  deviations.md.
- Core comparators: LocAgent, Agentless, SWE-bench (the benchmark itself), SWE-Search (origin
  of the excluded MCTS repair stage), SWE-Effi (closest existing precedent to our own cost-
  accuracy-frontier deliverable — needs an explicit "how we differ" paragraph in the report).
- Multi-agent debate lineage: Du et al. (the original debate paper SWE-Debate's mechanism
  descends from), Huang et al. (earliest compute-matched critique of that exact mechanism),
  Cemri et al. MAST (14-failure-mode taxonomy, usable as an analysis tool for our own results).
- The three most load-bearing methodology papers: Tran & Kiela (DPI-based proof + the
  boundary-condition H4 is built on — important caveat: their distractor-injection condition,
  closest analogue to "candidate density," was their WEAKEST crossover lever, so H4 may need a
  stronger operationalization than plain additive distractors), "Inside the Scaffold" (near-
  verbatim precedent for our confounded-comparisons premise), ColMAD (shows debate CAN beat
  compute-matched single-agent under incentive redesign, but only with heterogeneous backbones
  — flagged as a threat to validity against our single-backbone decision, logged in
  decisions.md).
- GraphRAG terminology: Peng et al.'s survey and Microsoft's original GraphRAG paper — critical
  finding that "GraphRAG" in the literature usually means LLM-extracted graphs (real inference
  cost to build), NOT our static-analysis AST graph (zero LLM cost to build). Report needs to
  disambiguate this explicitly on first use of the term.
- Closest kin found: LLM4FL (Defects4J fault localization, graph-nav + Reflexion, leave-one-out
  ablation, actually reports cost) and Agent Scaling Science / MAS Capability Saturation
  (Nature MI) — the single most methodologically relevant paper in the whole batch, a large-
  scale compute-matched 5-architecture study whose own SWE-bench-Verified arm shows every
  multi-agent architecture losing to single-agent under matched budget.
- Several SE-agent and issue-resolution surveys (LLM Agents for SE, LLM-Agent-SE, LLM-based
  Issue Resolution) that independently name SWE-Debate and confirm "no efficiency-aware
  evaluation" as a recognized field-wide gap.
- Historical grounding: BugLocator and BLUiR, pre-LLM IR-based bug localization — gives a
  concrete numeric anchor (~24-55% Top-1 depending on project) for what "baseline" localization
  accuracy meant before graphs/agents existed.
- Several more compute-matching-adjacent papers (MacNet, Agent Forest, Reasoning in Token
  Economies, Entropy Perspective on MAS, FJ-MoE, OneFlow) — all converging on the same pattern:
  debate's advantage shrinks or inverts once properly budget-matched, in domains from GSM8K to
  general agentic benchmarks.
Broke: Nothing — investigation only.
Next: See (4) below — the last 5 papers are now done too. Check with supervisor whether CoSIL,
OrcaLoca, KGCompass, and Prometheus (named as fallback/competitor systems in CLAUDE.md but not
yet in papers/) still need dedicated review, or whether the current set already covers what's
needed for the report's Related Work.

## 2026-09-13 (4)
Did: Reviewed the last 5 papers (Software Testing LLM Survey, LLMAO, AutoFL, Agent4SE Survey,
LLM4SE SLR). Literature review is now at 40 unique papers reviewed, 40 entries in
literature.md (41 PDFs in papers/, one is an accidental duplicate of 2601.12307v1). Two
flagged as uncertain/low relevance for student review (Software Testing LLM Survey — no
multi-agent or graph-grounded FL in its 102-paper corpus at all; LLM4SE SLR — corpus cutoff
predates the entire multi-agent-debate-for-FL literature, near-zero overlap). One genuinely
new load-bearing finding: Agent4SE Survey (ACM TOSEM, 124-paper survey of LLM-agents-for-SE)
reports that only 46.7% of surveyed agentic SE papers report ANY cost/efficiency data — the
best available field-scale statistic backing the "no cost reporting" half of A3062's
motivation, better than any single-paper anecdote. AutoFL (arXiv:2308.05487) and LLMAO
(arXiv:2310.01726) add two more single-agent, non-graph fault-localization baselines that
trade compute for accuracy without ever compute-matching against a stronger single model —
useful contrast points for describing SWE-Debate's heavier design.
Broke: Nothing.
Next: Literature review is effectively saturated for now. Good time to pause and discuss
direction in Chat — particularly: (a) whether to chase down CoSIL/OrcaLoca/KGCompass/
Prometheus specifically, (b) how to operationalize "candidate density" for H4 given Tran &
Kiela's own distractor-injection result was their weakest crossover lever (see literature.md),
(c) whether/how to address the single-backbone-debate threat to validity flagged from ColMAD
(see decisions.md). All findings pushed to GitHub once the student confirms.

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

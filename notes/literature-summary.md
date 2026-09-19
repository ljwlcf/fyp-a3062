# Literature review summary — FYP A3062

A synthesis of the 41 papers in `notes/literature.md`, read against the three-phase plan
(diagnose SWE-Debate → modify its debate → validate on fresh data). Labels such as A1 refer
to `notes/reading-order.md`. Last updated 2026-09-19.

## 1. What the field has established

### 1.1 Localization is the bottleneck, and graphs help — but nobody has bounded them

- **Repository-level localization is the hard part of issue resolution**, yet SWE-bench (A7)
  never scores it. Later work invents its own metrics: LocAgent's Acc@k (A6), Agentless's
  patch-superset check (B7), SWE-bench-Live's patch-derived file match (A8). There is no
  standard localization metric.
- **The approach has evolved** from flat text retrieval (BugLocator, C5) to structure-aware
  retrieval (BLUiR, C6) to static dependency graphs (LocAgent A6, LLM4FL A5) to graphs plus
  multi-agent debate (SWE-Debate, A1). Pre-LLM file-level Top-1 ranged from about 24% to 55%
  per project (C6).
- **Every localization ablation reviewed that removes the graph component loses accuracy**:
  SWE-Debate's multiple-chain generation is its largest component (−10.0 Pass@1 points), and
  LLM4FL drops 16.5% Top-1 (relative) without graph navigation. All of these are
  one-factor-at-a-time, single runs, never compute-matched.
- **No paper measures the structural ceiling**: whether the true fix location is even
  reachable in the graph from the issue's entry points. This is open, and cheap to measure.
- **"GraphRAG" is ambiguous.** In the survey literature (C8) and Microsoft's GraphRAG (C9) it
  means graphs extracted by an LLM, which cost inference to build. SWE-Debate's graph comes
  from static analysis of Python ASTs and costs nothing to build. The report must say which
  one it means on first use.

### 1.2 The evidence on multi-agent debate has turned

- **The origin** (Du et al., B1) showed debate gains on arithmetic, GSM8K and MMLU, but never
  gave the single-agent baseline the same compute.
- **Once compute is matched, the gains shrink or reverse.** Huang et al. (B9): debate loses to
  self-consistency at equal response counts on full GSM8K. Token Economies (B5): multi-agent
  debate's advantage shrinks or inverts under equal budgets, and answer diversity collapses
  across rounds. More Agents (B6): much of the gain comes from sampling and voting, and
  stacking debate on top can hurt. OneFlow (A9): one model can simulate a same-model
  multi-agent workflow at lower cost.
- **There is now theory behind the scepticism.** Tran & Kiela (A4) show, via the Data
  Processing Inequality, that a single agent with full context should do at least as well at
  a fixed token budget. Multi-agent setups become competitive only when the single agent's
  context is degraded — clearly under corrupted context, but not under plain distractors,
  which was their weakest lever.
- **A large controlled study agrees.** Kim et al. (A2, Nature Machine Intelligence; C14 is
  its preprint — one study, not two) ran 260 configurations. Coordination helps less as the
  single-agent baseline rises, with little benefit above about 45%. Coordination costs 58% to
  515% extra tokens. On SWE-bench Verified every multi-agent setup came out slightly below the
  single agent — but on only 20 instances per cell, and for full issue resolution, not
  localization.
- **Failure analyses explain why.** MAST (B4) catalogues 14 failure modes. The entropy study
  (B2) finds a single agent wins in about 43% of cases, outcomes are largely fixed in round
  one, and only ~6% of samples show genuine improvement from interaction versus ~83% that look
  like anchoring.
- **Debate can work, but under narrow conditions.** ColMAD (A3) shows both competitive debate
  (SWE-Debate's style) and consensus-seeking debate fail through "debate hacking": agents
  mislead to win, or agree too early. Its collaborative protocol beats a compute-matched single
  agent — **but only when the debaters are different models**; with the same model on both
  sides it loses. The mixture-of-experts analysis (B3) adds that debate helps when influence
  follows competence, and fails when it follows confidence.

**Net position:** with compute matched, the default expectation is that same-model debate does
not beat a single agent. The known exceptions need (a) incentives that reward information over
persuasion, (b) genuinely different agents, or (c) a single agent whose context is badly
degraded. SWE-Debate meets neither (a) nor (b) by design: five copies of one model, competitive
framing. Whether code localization supplies (c) is exactly what H4 tests.

### 1.3 Evaluation practice is weak across the field

- Only 46.7% of 124 agentic software-engineering papers report any efficiency data (C1).
- The issue-resolution survey (B10) names "lack of efficiency-aware evaluation" as a top open
  challenge, in a survey that covers SWE-Debate among graph-based localization methods.
- SWE-bench comparisons confound scaffold, model and configuration in one number (B11).
- SWE-Effi (B12) re-ranks agents by cost and finds failed attempts are the expensive ones
  (over 4x the tokens in one pairing).
- All six cross-domain systems (D1–D6) use one-factor-at-a-time, single-run ablations with
  little or no cost reporting. Supporting breadth only: these are mostly regional venues.
- **Contamination is real.** The same agent and model score 43.2% on SWE-bench Verified but
  19.25% on fresh issues (A8), and do better on original SWE-bench repositories than new ones.

## 2. The specific gap

SWE-Debate's ablation (A1) removes the debate together with its tokens, varies one factor at a
time, reports no cost anywhere, and is a single run. Reading the paper against the code also
shows the "three-round debate" is two rounds of five same-model agents plus one discriminator,
and chain selection is a one-shot vote (`notes/deviations.md`).

**Be precise about what SWE-Debate measured.** Its debate ablation (Table 2) is on end-to-end
Pass@1 on SWE-bench Verified: 41.4% with debate, 37.2% without. That no-debate figure is
*below* A2's ~45% threshold, so A2 does not contradict it — below the threshold, coordination
is expected to help sometimes. The paper's 81.67% file-level localization accuracy is a
separate result on SWE-bench Lite, and debate is never ablated at the localization level.

So the open question is narrower and cleaner than "two papers disagree": **what does debate
add to localization, the stage where it actually runs, once compute is matched?** At
localization-level accuracy (roughly 80%), A2's capability-saturation account predicts little
or nothing. Nobody has tested that, and nobody has crossed a graph factor with a coordination
factor.

**Weakest joint:** A2's threshold is defined on task success in its own benchmarks. Applying it
to file-level localization accuracy is an assumption — state it as the hypothesis being tested,
not as a known result.

## 3. What this means for each phase

### Phase 1 — Diagnose (Semester 1)

- **Reachability ceiling:** no precedent. Novel, and needs no GPU.
- **Compute matching:** follow A4's structural budget split and B5's accuracy-versus-budget
  curves. Include a majority-vote arm (B6) and a self-consistency arm (B9).
- **Control candidate ordering:** ordering alone moved Top-1 by 22 points in A5.
- **Log retrieval and selection separately:** did the graph surface the right file, and did the
  debate pick it? C1 calls for this kind of fine-grained metric; no existing evaluation does it.
- **Statistics:** every arm runs on the same instances, so analyse per-instance pairs (McNemar
  or paired bootstrap) with several seeds. A2's own SWE-bench arm had wide intervals at n = 20.
- **Threat to validity:** same-model agents may suppress any debate benefit regardless of
  compute (A3). Logged in `notes/decisions.md`.

### Phase 2 — Modify (Semester 2, first half)

The literature ranks the candidate changes:

1. **Graph-grounded debate (primary).** Agents must cite checkable graph facts — does the
   claimed path exist, how long is it, which edge types — and disagreements are settled
   against the graph. B9 shows models can't correct themselves without an external signal; the
   dependency graph is exactly such a signal, and it costs nothing. No paper does this.
2. **ColMAD protocol with different models (fallback).** The only protocol shown to beat a
   compute-matched single agent (A3), but only with heterogeneous debaters, so it means
   serving two model families. Compute matching becomes harder when the agents differ.
3. **Adaptive stopping (cost only).** Stop when round-one agreement is high (B2). Cheaper, but
   not much of a contribution on its own.

Ruled out: switching to consensus-seeking debate alone. A3 shows it fails too.

### Phase 3 — Validate (Semester 2, second half)

- **SWE-bench-Live (A8):** start from the 300-instance Lite subset and keep only issues created
  after the backbone's training cutoff. Localization-only evaluation needs no Docker, and the
  repositories are all Python, so the AST graph construction carries over.
- **H4:** A8's multi-file difficulty gradient is a candidate proxy for candidate density. A4
  warns that merely adding look-alike candidates may narrow the gap without reversing it.

## 4. Gaps in the review itself

- **Not yet reviewed:** The SWE-Bench Illusion; Debate or Vote (arXiv 2508.17536); CoSIL
  (arXiv 2503.22424); OrcaLoca; KGCompass; Prometheus; Multi-SWE-bench.
- **Venue-published software engineering work is under-represented** because most papers were
  found through arXiv. Search ACM DL and IEEE Xplore (ICSE, FSE, ASE, ISSTA, TSE, TOSEM, 2020
  onward) before writing related work.
- **Many entries are preprints.** Check DBLP for a published version before citing.
- **Peripheral papers:** C2, C10, C12 and D1–D6 earn at most one citation each.

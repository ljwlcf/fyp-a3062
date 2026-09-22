# FYP A3062 — Project Plan (updated for discussion)

**Student:** Li Jingwei · **Supervisor:** A/P Chen Lihui · **Programme:** Information
Engineering and Media, NTU · **Version:** 22 Sep 2026 (supersedes the plan submitted 14 Sep)

## What has changed since 14 Sep

- **Scope widened from a reproduction to three phases** (diagnose, modify, validate), following
  our discussion. The project now changes the debate mechanism and tests on a second dataset.
- **First result obtained.** The code dependency graph can reach the correct file in every
  one of the 75 test instances, but by the depth SWE-Debate searches it also reaches most of
  the repository, so reachability tells us almost nothing. Most of the graph's call edges are
  unresolved name matches. Details in Section 6.
- **This reshapes Phase 2.** The planned "graph-grounded debate" must use only the reliable
  part of the graph. This is one of the points for discussion below.
- **Model:** the model used in the paper (DeepSeek-V3-0324) is no longer offered by DeepSeek.
  The project will self-host one open-weights model on NTU GPUs instead.

## Points for discussion

1. **Scope:** can the project focus on fault localization (finding the buggy file) and leave
   out patch generation? Neither the graph nor the debate operates at the patching stage, and
   patching needs a Docker test environment for every instance.
2. **Phase 2 direction, given the graph-quality result:** (a) ground the debate only in the
   reliable edges (containment, inheritance, imports, resolved calls) — my recommendation;
   (b) make resolving the call edges part of the contribution; or (c) switch to the fallback,
   collaborative debate with two different models (ColMAD).
3. **GPU:** MLDA application submitted as requested; awaiting access. May I also apply for the
   EEE GPU Cluster as a backup? The next step (running SWE-Debate end to end, decision point
   30 Sep) needs a GPU to serve the model.
4. **Interim report (10 Nov):** is it acceptable to lead with the graph analysis (Section 6),
   which needs no GPU, plus the first baseline runs?

## 1. Title

**Diagnosing and Improving Multi-Agent Debate for Code Fault Localization**

## 2. Objective

To find out which part of graph-guided multi-agent fault localization does the work — the code
dependency graph, the multi-agent debate, or the two together — when every configuration gets
the same compute budget; to use that diagnosis to design and test one improved debate
mechanism; and to check the findings on bugs the model cannot have seen during training.

## 3. Background

Automated issue resolution asks a system to read a bug report, find the responsible code in a
whole repository, and fix it. Finding the code — fault localization — is the bottleneck. Two
techniques dominate current systems: searching a code dependency graph built by static
analysis, and having several LLM agents debate the answer. SWE-Debate (Li et al., ICSE 2026)
combines both and reports 81.67% file-level localization accuracy on SWE-bench Lite.

Controlled studies now question the debate half. When a single agent is given the same token
budget, multi-agent debate usually stops helping (Huang et al., ICLR 2024; Tran & Kiela, 2026).
A large study (Kim et al., Nature Machine Intelligence 2026) finds coordination helps less as
the single-agent baseline gets stronger, with little benefit once it scores above about 45%,
while costing 58–515% more tokens. Debate can work, but so far only with rules that reward
sharing information and with agents built on different models (ColMAD, 2025). SWE-Debate uses
competitive debate among five copies of one model.

## 4. Gap and motivation

SWE-Debate's evidence for debate is one ablation: end-to-end Pass@1 on SWE-bench Verified
falls from 41.4% to 37.2% without it. That removes the debate's tokens along with the
mechanism, measures the full pipeline rather than localization, reports no cost, and is a
single run. Debate was never tested at the localization stage, where accuracy is already about
80% and the capability-saturation finding predicts it adds little. No study has crossed a graph
factor with a debate factor under matched compute, and the paper does not report whether the
correct location is even reachable in its graph.

This matters because building the graph is cheap while debate multiplies inference cost. Teams
building software engineering agents cannot currently tell which of the two earns its place.
And if debate does not pay as designed, the next question is whether a better-designed debate
can.

## 5. Research questions

**Phase 1 — Diagnose**
- RQ1. What fraction of correct fix locations can the dependency graph reach, and how much does
  reaching them narrow the search? *(Answered — Section 6.)*
- RQ2. Does the graph still help once compute is matched? (H1: yes, by ordering candidates
  rather than by making them available)
- RQ3. Does debate improve localization once compute is matched? (H2: little)
- RQ4. Do the graph and debate interact rather than add up? (H3: yes)
- RQ5. Is any debate benefit concentrated on bugs with many plausible candidate locations? (H4)

**Phase 2 — Modify**
- RQ6. Does one evidence-led change to the debate beat both the original debate and a single
  agent with the same token budget?

**Phase 3 — Validate**
- RQ7. Do the Phase 1 and 2 findings hold on issues created after the model's training cutoff?

## 6. Progress to date: the graph analysis (RQ1)

Run on all 75 instances of SWE-Debate's own evaluation subset (django, sympy, sphinx: 25 each),
using SWE-Debate's unmodified graph builder. No LLM or GPU is needed.

- **The correct file is always reachable.** Starting from the code names that appear in the
  issue text, the graph reaches the correct file within 2 hops in 96% of instances and within 4
  hops in 100%.
- **But by then the graph has reached almost everything.** The table compares how often the
  correct file is reached with how much of the repository is reached at the same depth.
  "Enrichment" is how much likelier the correct file is to be reached than a random file; 1.0×
  means the graph has told us nothing.

  | Hops from issue | Correct file reached | Share of repository reached | Enrichment |
  |---:|---:|---:|---:|
  | 0 | 42.7% | 2.1% | 20.0× |
  | 1 | 86.7% | 19.7% | 4.4× |
  | 2 | 96.0% | 64.7% | 1.5× |
  | 3 | 97.3% | 84.2% | 1.2× |

  SWE-Debate searches up to 5 hops deep, well past the point where the graph carries
  information. The result holds across three definitions of the starting set and five edge
  policies.
- **Most call edges are guesses.** The builder never resolves which function a call refers
  to; it links the caller to every function with that name. 75–80% of call edges are such
  unresolved matches (one django call to `get` is linked to 618 different methods), and call
  edges make up 77.5% of the graph.

**What this means for the plan.**
- The graph does not help by making the answer *available* — it always is. If it helps, it
  helps by *ranking* candidates. The Phase 1 experiment is designed to isolate this.
- Since the correct file is almost always among the candidates, nearly all of the accuracy
  comes from *selection*, which is the debate's job. This makes the debate question sharper.
- Phase 2's graph-grounded debate cannot rely on call edges as they stand (discussion point 2).

Engineering done alongside: fixed five hard-coded values that stopped SWE-Debate from starting;
made graph building 6–12× faster with identical output; all run outputs and configurations are
tracked in the project repository.

## 7. Approach

### Phase 1 — Diagnose (Semester 1)

1. **Graph analysis (done).** Section 6.
2. **Reproduction.** Serve one open-weights model at a fixed version with vLLM on NTU GPUs.
   Reproduce SWE-Debate's localization stage on the 75-instance subset. Record tokens per stage,
   and log separately whether the correct file appears in any candidate chain (retrieval, the
   graph's job) and whether the debate picks it (selection, the debate's job).
3. **Compute-matched 2×2 experiment.** Cross graph (many candidate chains vs one) with debate
   (five agents vs one). Every multi-agent setting gets a single-agent counterpart with the
   same token budget, plus majority-vote and self-consistency settings. Candidate order is held
   fixed across settings, since order alone can shift accuracy by up to 22 points (LLM4FL).
   Several runs per setting, compared instance by instance (McNemar test or paired bootstrap);
   expand to the 300-instance SWE-bench Lite if differences are too small to detect.

### Phase 2 — Modify (Semester 2, first half)

Build **one** change to the debate, chosen from the Phase 1 evidence:
- **Default: graph-grounded debate.** Agents must back each claim with a graph fact that can be
  checked (does this path exist, how long is it, which edge types), and disagreements are
  settled against the graph. Models cannot reliably correct themselves without an outside
  signal; the graph is such a signal and costs nothing to consult. Following Section 6, only
  reliable edges count as evidence.
- **Fallback: collaborative debate (ColMAD) with agents from two model families** — the only
  protocol shown to beat an equal-budget single agent, and only with different models.
- Tested against the original debate and the equal-budget single agent, with the Phase 1
  controls.

### Phase 3 — Validate (Semester 2, second half)

Re-run the key settings on SWE-bench-Live (Zhang et al., 2025), starting from its
300-instance Lite subset and keeping only issues created after the model's training cutoff. It
is Python-only, so the graph builder carries over, and localization-only testing needs no
Docker. Its multi-file tasks also give a natural high-candidate group for H4.

## 8. Scope

**Included:** fault localization; the static dependency graph; SWE-Debate's chain voting and
plan debate; one debate modification; token and latency cost as outcomes; the SWE-bench subset
and SWE-bench-Live.

**Excluded, with reasons:**
- Patch generation and end-to-end resolve rate — neither factor operates there, it dominates
  cost, and it needs Docker test environments. *(Discussion point 1.)*
- Changing the model within a comparison — would bring back the confound being removed. The
  two-model Phase 2 fallback is the one deliberate exception.
- Number of debate rounds as a factor — fixed in the implementation.
- Non-Python repositories — the graph is built with Python's `ast` module.
- Training or fine-tuning models.

## 9. Schedule

| Period | Phase | Work | Milestone |
|---|---|---|---|
| Sep 2026 | 1 | Graph analysis (done); GPU access; one SWE-Debate instance end to end | Go/no-go on SWE-Debate, 30 Sep |
| Oct 2026 | 1 | Serve model; reproduce localization baseline; token accounting; retrieval/selection logging | Baseline reproduced |
| Early Nov 2026 | 1 | First 2×2 pass; interim report and video | Interim report, 10 Nov |
| Nov–Dec 2026 | 1 | Equal-budget single-agent settings, majority vote, self-consistency, repeated runs, paired analysis | Phase 1 results |
| Jan – mid-Feb 2027 | 2 | Build and test the debate modification | Phase 2 results |
| Mid-Feb – early Mar 2027 | 3 | SWE-bench-Live validation; H4 analysis | Phase 3 results |
| Mar 2027 | — | Writing, figures, demonstration | Draft final report, 25 Mar |
| Apr 2027 | — | Revision; demonstration | Final report 9 Apr; demo 12–16 Apr |
| May 2027 | — | Oral presentation | Oral 10–12 May |

The December vacation carries the equal-budget runs.

## 10. Deliverables

1. Graph analysis: reachability, how quickly the graph stops narrowing the search, and edge
   quality (first version done).
2. An instrumented SWE-Debate with switches for each component and token accounting.
3. Results of the 2×2 experiment with paired statistics and cost–accuracy plots.
4. One improved debate mechanism, tested at equal compute.
5. Validation results on SWE-bench-Live.
6. A demonstration: original debate, improved debate and single agent on the same bug, with
   live token counts.
7. Interim report and video, final report, oral presentation.

## 11. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| SWE-Debate does not run or reproduce | Medium (non-LLM parts now run) | Decision point 30 Sep; same design on LocAgent or CoSIL. The graph analysis stands either way. |
| GPU unavailable or too old | Medium | MLDA first; EEE GPU Cluster as backup; smaller model if needed. |
| Graph too noisy to ground the debate | Medium (Section 6) | Use reliable edges only, or switch to the ColMAD fallback (discussion point 2). |
| The modification does not beat the baseline | Medium | A clear negative result under proper controls is still a finding; Phase 1 results stand. |
| Too few post-cutoff SWE-bench-Live instances | Low–Medium | The benchmark adds issues monthly; a model with an earlier cutoff leaves more. |
| Differences within noise | Medium | Paired design, repeated runs, expand to 300 instances. |

## 12. Key references

Li et al., SWE-Debate, ICSE 2026 (arXiv:2507.23348) · Kim et al., Capable language models can
outgrow the benefits of collaboration, Nature Machine Intelligence 2026 · Chen et al., When and
Why Does Multi-Agent Debate Fail (ColMAD), arXiv:2510.20963 · Tran & Kiela, arXiv:2604.02460 ·
Huang et al., Large Language Models Cannot Self-Correct Reasoning Yet, ICLR 2024 · Du et al.,
Multiagent Debate, ICML 2024 · Rafi et al., LLM4FL, arXiv:2409.13642 · Chen et al., LocAgent,
arXiv:2503.09089 · Jimenez et al., SWE-bench, ICLR 2024 · Zhang et al., SWE-bench Goes Live!,
arXiv:2505.23419 · Cemri et al., Why Do Multi-Agent LLM Systems Fail, NeurIPS 2025.

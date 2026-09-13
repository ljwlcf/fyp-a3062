# Literature Notes — FYP A3062

One entry per paper, using this schema:

## <short name> — arXiv:xxxx.xxxxx (venue, date)
Claim:
Task/benchmark:
Method:
Ablation:
Cost reporting:
Relation to A3062:
Report section:

## MAKG — DOI:10.1016/j.jmsy.2026.02.016 (J. Manuf. Syst. 85, 2026)
Claim: A multi-agent + knowledge-graph RAG framework (MAKG) for industrial equipment
fault diagnosis beats non-RAG, NaiveRAG, HyDE RAG, GraphRAG and LightRAG baselines,
reaching 90.1% accuracy on a private 210-case benchmark, via (1) lightweight contrastive
fine-tuning of a 12M-param embedding model instead of full LLM fine-tuning, and (2) a
4-role agent pipeline (query rewrite/split -> multi-path graph+text retrieval -> summary
extraction -> iterative self-reflection).
Task/benchmark: Industrial robot fault diagnosis QA, private dataset (IFD-QA, 210 cases,
3 difficulty tiers: simple/multi-context/reasoning). Not code, not SWE-bench-adjacent.
Method: Two custom fault-diagnosis KGs (KDKG: 1587 entities/8 relations/2643 triples;
KACKG: 2869 entities/14 relations/6217 triples) built from enterprise data; DeepSeek-V2-16B
backbone; 4 sequential specialized-role agents — not a competitive debate/vote among peers,
closer to Agentless-style role decomposition than SWE-Debate's multi-agent debate.
Ablation: One-factor-at-a-time removal of 5 components (KACKG, fine-tuned embeddings,
query rewrite/split, summary extraction, self-reflection). Single run, no seeds, no CIs, no
compute-matching — the same methodological gap this project targets in SWE-Debate. KG
removal is the largest single drop (90.1% -> 80.08%).
Cost reporting: Wall-clock only (avg response time 9.3s vs baselines 3.8-11.3s), reported
separately from one-time embedding fine-tuning compute (45min/5GB GPU vs 5hr/38GB for full
LLM fine-tuning). No token counts, no dollar cost, and the two cost numbers measure different
things (inference latency vs training cost) rather than a unified cost-accuracy frontier.
Relation to A3062: Confirms "ablation is not compute-matched, one-factor-at-a-time, no token
cost" is a field-wide norm, not specific to SWE-Debate — a second data point for the report's
motivation section. Its agents are a sequential pipeline of specialized roles, not competitive
debate, so it's a useful boundary case when defining what counts as "multi-agent debate" vs
"multi-agent pipeline" in scope. Domain (industrial maintenance) has no direct methodological
transfer to code localization.
Report section: Related Work (multi-agent GraphRAG outside code) / Motivation (evidence
uncontrolled ablations are the field norm, not a SWE-Debate-specific weakness).

## Agentic Graph-RAG — DOI:10.1109/ICCC68654.2025.11437910 (IEEE ICCC 2025)
Claim: A blackboard-style multi-agent Graph-RAG framework (agents coordinate via a shared
"Common Factual Ground" rather than dialogue) claims new SOTA on multi-hop QA — 75.8%
accuracy on long-tail PopQA, 94.2% faithfulness on 500 manually evaluated samples, plus best
EM/F1 on HotpotQA and 2WikiMultiHopQA.
Task/benchmark: Multi-hop open-domain QA — HotpotQA, 2WikiMultiHopQA, PopQA (long-tail),
ALCE-ASQA. Knowledge base is Wikidata + Wikipedia. Not code, not SWE-bench-adjacent.
Method: Fixed sequential pipeline, not debate. Planner Agent decomposes the query
(Least-to-Most, escalating to Tree-of-Thoughts on hard queries) into an ordered sub-query
chain. Per sub-query, a Dual-Retrieval Module runs a Graph Navigator Agent (entity linking +
SPARQL/Cypher over Wikidata) and a Corpus Retriever Agent (hybrid dense+sparse + re-ranking
over Wikipedia text) in parallel; a Synthesizer-Verifier Agent cross-checks both evidence
sources and writes a verified answer back to shared state before the next sub-query runs. No
peer agents independently answer then argue/vote — this is Agentless-style role
specialization, not SWE-Debate-style competitive debate.
Ablation: One-factor-at-a-time (Text-Only, KG-Only, Single-Agent-collapse vs. full system;
Fig. 3) — never factorial, never compute-matched (the "Single-Agent" condition collapses the
whole pipeline into one call, obviously spending far less inference compute, yet the drop is
attributed to "multi-agent structure"), single-run point scores, no seeds, no CIs.
Cost reporting: None anywhere — no tokens, no latency, no dollar cost, for either main
results or the ablation.
Relation to A3062: A clean second data point for the FYP's central complaint: a real
graph+multi-agent RAG system attributes a large ablation drop to "removing multi-agent
structure" without compute-matching, exactly the SWE-Debate pattern. Its coordination is
pipeline-style (not debate), so it's out of scope as direct H2/H3 comparison literature, but
its KG-ablation result — the largest single-benchmark drop is on PopQA (long-tail/rare
entities) — is a suggestive analog to H4 (graph/structure benefit concentrating where the
target is sparse or hard to find via flat retrieval).
Report section: Motivation (uncontrolled-ablation critique); secondarily Related Work —
graph-grounded RAG (non-code example), explicitly not the multi-agent-debate bucket.

## Agentic RAG for SW Testing (Hybrid Vector-Graph) — DOI:10.1109/ICODSE68111.2025.11351757 (IEEE ICoDSE 2025)
Claim: An "Agentic RAG" framework for enterprise QE test-artifact generation (test
plans/cases from SAP documentation) combining multi-agent orchestration with a hybrid
vector-graph knowledge base, claiming accuracy 65% (basic RAG) -> 94.8% (full system), 85%
reduction in artifact-creation time, 35% cost savings, 92% fewer post-deployment defects, on
a real SAP S/4HANA migration project.
Task/benchmark: Enterprise QE test-artifact *authoring* (test plans/cases from legacy SAP
docs), not test execution or code-level bug detection — not SWE-bench-adjacent. Evaluated on
a proprietary 5,000-scenario synthetic set and a proprietary 1,000-case enterprise SAP
dataset; no public benchmark, no shared data, "accuracy" undefined (no stated ground truth).
The closest software-engineering paper in this batch, but on a different task from
localization.
Method: Sequential pipeline of 5 specialized agents (Legacy Test Analysis -> Functional
Change Mapping -> Integration Point ID -> Modernized Test Case -> Compliance Validation) —
no competitive/adversarial structure, no voting. Hybrid retrieval: vector DB (SingleStore)
similarity search first, then a TigerGraph knowledge graph (15+ edge types: Requires,
Validates, DependsOn, Impacts, Covers) traversal expands context; dynamic LLM routing
(Mistral 7B for simple cases, Gemini Pro for complex reasoning).
Ablation: One-factor-at-a-time removal of 4 components (Multi-Agent Orchestration -12.3%,
Hybrid Vector-Graph -15.7%, Enhanced Contextualization -18.2%, Traceability Framework -8.9%)
— no factorial combinations, no compute-matching (5-agent orchestration's removed tokens are
never substituted), single point estimates, no seeds/CIs/significance testing anywhere. Even
more uncontrolled than SWE-Debate's own ablation.
Cost reporting: No tokens, no $/API-call, no latency figures anywhere — "cost" is reported
only as business ROI ("35% cost savings," "85% time reduction," measured in labor-hours),
never as inference/compute cost. A clean illustration of the FYP's complaint that "cost"
gets reported as a marketing KPI rather than the accounting needed to judge whether
compute-heavy architecture is worth its keep.
Relation to A3062: A starker version of the field-wide pattern this project targets — even
weaker methodology than SWE-Debate's ablation, useful as a second data point that the problem
is systemic. Pipeline architecture, not debate, so it doesn't bear on H2/H3. Its own graph
ablation (-15.7%) is suggestive for H1 but, being uncontrolled and single-run, can't actually
support or refute it — cite as "another graph-grounding claim the methodology can't back up."
Domain (SAP test-artifact generation) is software-engineering-adjacent but not a competitor
system to LocAgent/CoSIL/KGCompass/SWE-Debate.
Report section: Motivation (uncontrolled ablations recur across agentic-RAG-for-SE broadly,
not just localization); brief mention in Related Work — multi-agent systems in SE.

## MedRAG-Agent — DOI:10.1109/GCAT66372.2025.11368379 (IEEE GCAT 2025)
Claim: A 4-agent KG-enhanced RAG framework for medical QA claims 78.5% accuracy (4.30/5) on
MedQA (USMLE, via the MIRAGE harness), a 12% relative gain over vanilla RAG (3.70/5), and a
15% relative reduction in hallucinated content (95.2% vs 82.5% faithfulness).
Task/benchmark: Medical QA (MedQA/USMLE). Not code, not SWE-bench-adjacent — a different
domain from A3062.
Method: Sequential 4-agent pipeline, not debate: Query Decomposer -> KG Navigator (biomedical
KG built via NER over MedlinePlus/PubMed, mapped to UMLS) -> Document Retriever (FAISS dense
search over KG-constrained context) -> Synthesizer/Verifier (citations + faithfulness
penalty for unsupported claims). Each agent runs once per query in fixed order — pipeline
role-specialization like Agentless, not competitive/voting debate.
Ablation: One-factor-at-a-time removal of 3 agents (Verifier, Query Decomposer, KG
Navigator; Table II) — no factorial combinations, no compute-matching, single point values,
no seeds/CIs/significance testing. Explicitly framed as confirming a pre-registered
hypothesis rather than a rigorous ablation design.
Cost reporting: None — no tokens, no latency, no dollar cost anywhere, for main system or
ablation. Only "cost-adjacent" detail is which backing LLM/vector-DB was used (GPT-4o or
Claude 3.5 Sonnet; FAISS), with no usage accounting.
Relation to A3062: Another cross-domain data point for the field-wide uncontrolled-ablation
complaint. Pipeline, not debate, so out of scope for H2/H3 directly. Its KG Navigator
ablation produces the largest single-component drop (4.30->3.85), loosely consistent with H1
(graph grounding carries real information) but, being uncontrolled and single-run, cannot
actually adjudicate it the way A3062's compute-matched design would.
Report section: Related Work — multi-agent/KG-RAG outside code; brief Motivation mention as
cross-domain evidence.

## OSINT-MicroAgents — DOI:10.1109/INISTA68122.2025.11249668 (IEEE INISTA 2025)
Claim: A 4th ADD-iteration OSINT pipeline replacing a single "mega-agent" with specialized
micro-agents, unifying vector+graph stores into one GraphRAG layer, and replacing a
key-value URL cache with a hierarchical Bloom filter. Headline number is a systems
microbenchmark, not an LLM result: Bloom-filter URL dedup is ~100x faster than RediSearch
TAG lookups (0.305s vs 3477s for 3M URL queries).
Task/benchmark: OSINT data acquisition (news/social/RSS) — NLP subtasks are stance
detection, NER, contradiction detection, ontology extraction, report generation. No shared
benchmark; evaluated on synthetic Redis URL sets (dedup experiment) and a ~10-11M
deduplicated-record dataset with no accuracy metrics reported. Not code, not
SWE-bench-adjacent.
Method: Supervisor-orchestrated pipeline of single-purpose agents (Stance Detection, NER,
Contradiction Detection, Ontology Extraction, Report Generation) invoked sequentially/
conditionally — no independent-answer-then-vote step, no debate. Graph+vector unified into
one Neo4j-style store (HNSW vector index as node properties, hybrid Cypher queries). The
Bloom filter is a pure crawl-dedup engineering component, unrelated to LLM-agent
coordination.
Ablation: Essentially none for the actual multi-agent/GraphRAG architecture — the only
quantitative comparison is the Bloom-filter-vs-RediSearch cache microbenchmark (a systems
experiment, not an ablation of agents or graph-grounding). The claimed multi-agent and
GraphRAG improvements are validated only qualitatively via ATAM expert-panel review and
citations to other papers' numbers — never run against the old architecture on a shared
task. No seeds, no repeated runs, no CIs anywhere, including the Bloom-filter timing (appears
to be single cumulative runs per dataset size).
Cost reporting: Wall-clock latency reported only for the Bloom-filter cache comparison
(total and per-query seconds) — the paper's one real cost number, and it isn't even about
the LLM/agent pipeline. Zero token/dollar/latency figures for the actual multi-agent LLM
pipeline or GraphRAG retrieval layer; claims about those are backed only by citations to
other papers, with LLM experiments explicitly deferred to future work.
Relation to A3062: Low direct relevance — pipeline coordination, not debate, so it can't
speak to H1-H4. Its value is illustrative: architectural claims validated by expert opinion
and literature citation rather than measurement, with zero compute accounting for the actual
LLM components — an even more extreme version of the "no cost reporting, no real ablation"
pattern this project is built to correct. The Bloom-filter dedup idea is a possibly reusable
engineering aside, orthogonal to fault-localization graph construction.
Report section: Related Work — multi-agent/GraphRAG outside code; optional Motivation
mention as a supporting cross-domain example.

## KG-News-Agents — DOI:10.1007/s00521-026-11944-0 (Neural Computing and Applications, Mar 2026)
Claim: A multi-agent LLM system using a shared, dynamically-built knowledge graph as memory
for two specialist agents (bias detector, fact-checker) claims to beat an unstructured-RAG
baseline and an LLM-only baseline on political news bias detection (F1 0.901 vs 0.287 RAG vs
0.713 LLM-only) and fact-checking (F1 0.794 vs 0.661 RAG vs 0.720 LLM-only), p<0.01 via
McNemar's test.
Task/benchmark: News bias detection (3-class, 45 held-out articles from a 222-article
AllSides corpus) and binary fact-checking (214 claims from Media Bias/Fact Check). Not code,
not SWE-bench-adjacent — political-news NLP classification, no code artifacts.
Method: Sequential dispatch, not debate — an Agent Manager routes a query to one of two
independent specialist agents (Bias Detector, Fact Checker), each of which queries a shared
Neo4j KG (built separately by a KG Builder agent via LangChain's LLM Graph Transformer) and
makes one LLM call (Claude 3.5 Sonnet v2). No inter-agent argumentation or voting — agents
answer alone. Closer to a simple retrieval pipeline than to SWE-Debate's peer-argue-vote
design.
Ablation: A single 3-arm comparison (RAG baseline / LLM-only / LLM+KG), not factorial (never
toggles "multi-agent" and "KG" as independent factors — the LLM+KG arm bundles both). Not
compute-matched — explicitly acknowledged confound: the RAG baseline runs on a smaller model
(Mistral-7B-Instruct) than the other two arms (Claude 3.5 Sonnet v2), for practical/access
reasons, not controlled for. Does report bootstrap 95% CIs (1000 resamples) and McNemar's
tests — better statistical practice than a bare point estimate — but no seed variation or
repeated independent runs; CIs are over test-set resampling only.
Cost reporting: None quantitative — Section 6.2.3 gestures narratively at a "computational
trade-off" (RAG called compute-heavy, KG called costly to build/maintain) with no numbers
attached.
Relation to A3062: Low direct relevance — no debate mechanism (says nothing about H2/H3/H4),
different domain, and its "multi-agent" system is really a router-plus-independent-
specialists dispatch. Useful only as one more current (2026) illustration of the field-wide
complaint: an admitted, unaddressed model-size confound across ablation arms, no factorial
separation of "multi-agent" from "KG," and zero cost measurement despite narrative cost
claims. Domain mismatch is severe enough that inclusion should be flagged for supervisor
review rather than treated as core comparison literature.
Report section: Uncertain relevance — if included, only in the literature review's broader
"evaluation rigor across graph-RAG/multi-agent literature" framing, not in the
SWE-Debate/LocAgent/CoSIL technical lineage.

## SWE-Debate — arXiv:2507.23348 (arXiv preprint, 31 Jul 2025)
Claim: 41.4% Pass@1 on SWE-Bench-Verified (207/500) with DeepSeek-V3-0324, and 81.67%
file-level localization accuracy (Acc@1) on SWE-bench-Lite. Same-backbone deltas: +2.6 pts
Pass@1 over SWE-Agent/OpenHands-DeepSeek, +3.93 pts Acc@1-File over LocAgent+Claude-3.5.
Abstract's headline "6.7%/5.1% improvement" figures don't exactly match these same-backbone
deltas — likely computed against different, unstated comparator rows (see deviations.md).
Task/benchmark: SWE-Bench-Verified (500) for Pass@1 and the component ablation;
SWE-bench-Lite (300) for the localization-accuracy table only. SWE-Bench-Verified-S (Appendix
A, 75 instances: django 23 + sympy 26 + **sphinx-doc 26** — three repos, not two) used only
for the chain-depth sweep (RQ4). Confirmed to match `utils/verified75.txt` in the repo.
Method: (1) Fault Propagation Traces — AST-based static dependency graph (call/inherit/
import/variable-reference edges), entry points via LLM matching to top-K=5 issue entities,
then BFS (top-W=4 neighbors) + depth-limited DFS (L=5), yielding K*W=20 candidate chains.
(2) Multi-Agent Debate, two sub-phases: chain selection is a SINGLE round of independent
parallel votes over a diverse 6-chain shortlist (not iterative debate, despite prose calling
it "competitive ranking" — maps to code Stage 6 `_vote_on_chains`); modification-plan debate
is 5 agents: round 1 independent analysis -> round 2 cross-agent refinement (paper's own
Appendix B hyperparameter table calls this "3 rounds," `number_of_round: 3`, but round 3 is
actually ONE discriminator agent synthesizing round-2 outputs, not a third round of 5-agent
debate — maps exactly to code Stage 7). (3) MCTS-based patch generation (out of scope for
A3062) extending the SWE-Search/moatless scaffold. CONFIRMED verbatim (Sec 4.5, Sec 6.2): the
5 agents are one DeepSeek-V3-0324 model differentiated only by system prompts — the paper's
own Limitations section concedes this while still claiming the ablation validates the
mechanism.
Ablation: Table 2, one-factor-at-a-time (chains -10.0, edit plan -6.0, debate -4.2 pts vs
full system), no factorial cell crosses chains x debate, single run, no seeds/CIs anywhere in
the paper (confirmed exhaustively). RQ4's chain-depth sweep (Fig. 3, 75-instance subset) is
likewise a single-point sweep over depths {1,3,5,7}, no repeats.
Cost reporting: None anywhere — checked every table/figure/caption including the MCTS
hyperparameter table (Appendix B), which lists only algorithmic params (agents=5, rounds=3,
temperatures, UCT constants) with zero cost/token/latency fields.
Relation to A3062: This is the paper being re-ablated. A3062 adds exactly what's missing:
compute-matching (Table 2's ablated rows silently change token budget along with the
architectural factor), factorial crossing (no interaction cell exists, so H3 is untestable
from this paper alone), the recall/selection decomposition (chain-selection-Stage-6 vs
modification-plan-Stage-7 conflate "did the graph surface it" with "did voting pick it," which
neither this paper's Acc@1 nor its ablation separates), and multi-seed CIs + full cost
logging. The paper's own Section 7 "threats to validity" concession is about model/dataset
generalizability, NOT an admission of the ablation-methodology gap A3062 targets — don't
overstate what it concedes (see deviations.md for the full discrepancy list found reading
this paper against the actual repo).
Report section: Anchors the report's core Method (pipeline description) and Motivation
(ablation's lack of compute-matching/factoriality/cost/seeds as the explicit gap) sections,
plus Reproduction (Table 1/2/3 numbers A3062 must first reproduce before re-ablating).

## LocAgent — arXiv:2503.09089 (arXiv preprint, cs.SE, Mar 2025)
Claim: Graph-guided single-agent localization; Claude-3.5 backbone gets 77.74/91.97/94.16%
file Acc@1/3/5 on SWE-Bench-Lite (274/300), beating all baselines tested. Fine-tuned
Qwen2.5-Coder-32B matches Claude-3.5-level accuracy at ~86% lower cost ($0.66->$0.09/instance).
Better localization propagates downstream: ~12% higher Pass@10 (33.58%->37.59%) vs Agentless's
localizations.
Task/benchmark: SWE-Bench-Lite (274/300 after dropping instances touching no existing
function). Also introduces Loc-Bench (560 instances, post-Oct-2024 issues, contamination-
reduced). Localization metric is Acc@k (borrowed from Agentless): all ground-truth locations
must appear in top-k, scored separately at file/module/function granularity — an ad hoc
extension of SWE-bench, which doesn't score localization itself.
Method: Heterogeneous AST-derived graph (nodes: dir/file/class/function; edges: contain/
import/invoke/inherit) + hierarchical sparse index (BM25 over IDs and code chunks). THREE
tools exposed to a SINGLE agent: SearchEntity, TraverseGraph (type-aware BFS, tree-format
output shown to beat row/DOT/JSON encodings), RetrieveEntity. Explicitly single-agent,
iterative CoT tool-use — no multi-agent debate; "confidence" comes from self-consistency
(repeated single-agent runs, RRF-aggregated), not adversarial/cooperative discussion.
Ablation: One-factor-at-a-time component removal (Table 6, using cheaper fine-tuned Qwen-7B
"due to budget constraints" rather than the headline config) plus a serialization-format
sweep (Table 9, fixed 37-sample subset). Both single-run, no seeds/CIs, budget-constrained
rather than compute-matched.
Cost reporting: Table 5 reports avg $ cost and agent-interaction-round count per instance
(Claude-3.5 / two fine-tuned Qwen sizes) plus a cost-efficiency ratio (Acc@10 / avg cost),
computed from public per-token API prices. No latency reported; round count used as a rough
proxy. Single-run point estimates.
Relation to A3062: Direct H1 comparison point — graph grounding via a single agent, no
debate layer. Its own component ablation is suggestive that graph-traversal specifically
(not just more tool calls) contributes real accuracy, but it's not compute-matched or
multi-seed — exactly A3062's gap. Its cost-table methodology (public per-token pricing +
efficiency ratio) is a reasonable template, though it lacks latency and per-stage breakdowns.
Report section: Related Work — graph-grounded localization.

## Agentless — arXiv:2407.01489 (arXiv preprint, cs.SE, Jul 2024)
Claim: A purely staged, NON-agentic 3-phase pipeline (localize -> repair -> validate) gets
32.00% (96/300) on SWE-bench Lite at $0.70/instance avg — highest among open-source
approaches, undercutting most agentic baselines on cost while beating them on accuracy.
38.80% (194/500) on SWE-bench Verified. Also manually finds 4.3% of SWE-bench Lite leaks the
gold patch in the issue text, 10.0% lack sufficient info, 5.0% have misleading proposed
solutions -> filtered SWE-bench Lite-S (249 instances).
Task/benchmark: SWE-bench Lite (300) and Verified (500). "% Correct Location" metric: a
repair patch is credited as correctly localized if it edits a superset of all gold-patch
locations — a cruder binary superset match measured post-hoc on the final repair patch, not
a dedicated ranked localization-only evaluation (contrast with LocAgent's Acc@k).
Method: NO LLM-driven decision loop, no environment feedback controlling control flow, and
CONFIRMED NO GRAPH STRUCTURE AT ALL — the exact "no-graph" baseline A3062 contrasts against.
Three fixed phases: (1) Localization — flat directory-tree listing + embedding retrieval
(OpenAI text-embedding-3-small) narrows to suspicious files, then file "skeletons"
(signatures+comments only) narrow to classes/functions, then full code narrows to edit lines
(4x sampled). (2) Repair — Search/Replace diffs, 10 samples/location set (40 total).
(3) Validation — LLM-synthesized reproduction tests filter candidates, plus regression tests
+ AST-normalized majority voting.
Ablation: Extensive but one-factor-at-a-time across all 3 stages (Tables 2-4, Fig. 6):
prompting-only vs embedding-only localization, full-file vs skeleton context, greedy vs
multi-sample; repair sample-count swept 4->44 (plus a 42%-oracle upper bound at "all
samples"); validation ablated as majority-voting-alone -> +regression -> +reproduction tests.
All single-run, fixed sample counts, no seeds/CIs.
Cost reporting: The most granular of any paper reviewed so far — Table 1 gives avg $ and
avg tokens/instance; Tables 2-4 break dollar cost down PER PIPELINE STAGE (e.g. file
localization $0.02-0.06, edit-location localization $0.06-0.18, reproduction-test generation
+$0.25). This stage-by-stage decomposition is exactly the instrumentation granularity A3062
wants.
Relation to A3062: The strongest existing precedent that cheap/simple can match or beat
expensive/complex — directly supports A3062's overarching skepticism about whether debate
earns its tokens. Its non-agentic, non-graph localization stage is a natural template/
candidate for A3062's own compute-matched single-agent baseline arm; its per-stage cost table
is a strong methodological model. Its "% Correct Location" metric is weaker than A3062's
recall/selection split — it conflates "did retrieval surface the right location" with "did
the model choose it," exactly the distinction A3062's design separates.
Report section: Related Work — cost-efficient/agentless baselines; also cite in Motivation.

## SWE-bench — arXiv:2310.06770 (ICLR 2024)
Claim: 2,294 task instances from real GitHub issues + merged PRs across 12 Python repos,
requiring a repo-level patch passing the PR's tests. Even the best model tested (Claude 2 +
BM25) resolves only 1.96% (4.80% oracle-file-retrieval). Performance degrades as retrieved
context grows; not correlated with issue date (argues against memorization); models
systematically under-edit vs gold patches.
Task/benchmark: 2,294 instances via scrape-> attribute-filter (resolves linked issue, touches
tests) -> execution-filter (>=1 fail-to-pass test, no install/runtime errors) pipeline across
astropy/django/flask/matplotlib/pylint/pytest/requests/scikit-learn/seaborn/sphinx/sympy/
xarray. Also introduces SWE-bench Lite (300, self-contained bug-fix subset, 11/12 repos).
Metric is strict end-to-end %Resolved (patch + FAIL_TO_PASS/PASS_TO_PASS tests all pass) via
per-repo-version conda environments (NOT literally Docker in this paper's own text — Docker
is a feature of the later official evaluation harness). CRITICALLY: SWE-bench does NOT define
or measure localization as a sub-task anywhere — file retrieval (BM25 vs oracle) is used only
to fit context in-window, never scored as IR. This absence is exactly what motivates
LocAgent's Loc-Bench and Agentless's %Correct Location. SWE-bench VERIFIED (500,
OpenAI-curated) is NOT introduced in this paper at all — it postdates this ICLR work; per
Agentless's account it's OpenAI's 2024 human-validated subset of the original 2,294. A3062's
provenance chain should read: SWE-bench (2,294, this paper) -> SWE-bench Verified (500, OpenAI
2024) -> verified-mini (community-curated, external to both papers) -> A3062's 75-instance
sub-subset — two links external to anything reviewed here.
Method: N/A as a localization method (benchmark/dataset paper). Baselines are simple
BM25/oracle retrieval + long-context generation (ChatGPT-3.5/GPT-4/Claude 2/fine-tuned
SWE-Llama), whole-file patch generation, no localization tooling, no graph, no agent loop.
Ablation: Not a method ablation — systematic analyses instead (BM25 vs oracle vs
oracle-collapsed context; context-length sensitivity; per-repo breakdown; temporal
partitioning; 6-way failure taxonomy). All single-run (GPT-4 evaluated on only a 25% random
subset "due to budget constraints"), no seeds/CIs.
Cost reporting: None — only context-window token LIMITS are reported (Table 4), no
actual $/token cost for any model.
Relation to A3062: Establishes the shared measurement standard the whole field (including
SWE-Debate and A3062) evaluates against, even though A3062 scopes out the execution/Docker
dependency by restricting to localization only. Directly justifies why A3062 must borrow a
localization metric from later work (LocAgent's Acc@k or Agentless's correct-location check)
rather than from SWE-bench itself, since SWE-bench never measures localization. Report should
cite the Verified/verified-mini provenance chain precisely rather than attribute it to this
paper.
Report section: Methodology — benchmark/dataset.

## SWE-Search — arXiv:2410.20285 (ICLR 2025)
Claim: 23% mean relative Pass@1 improvement across 5 backbones on SWE-bench Lite vs a matched
non-search baseline (e.g. GPT-4o 25.7->31.0, Qwen2.5-72B 18.0->24.7). Internal value function
alone picks the eventual-correct solution 73% of the time; adding the multi-agent
Discriminator debate raises this to 84%.
Task/benchmark: SWE-bench Lite (300). Metrics: Pass@1 resolve rate, Pass@5.
Method: MCTS applied to the REPAIR/patch-generation stage (not localization) — this IS the
direct architectural precedent for SWE-Debate's excluded MCTS repair stage. Modified UCT
(AlphaZero-style, not LLM-driven, for interpretability/efficiency) with an early-depth
exploration bonus and late-depth exploitation penalty; capped expansion (3-5 children/node,
100 iterations, depth 20). A Value Agent scores state-action pairs AND emits natural-language
"hindsight feedback" fed back to re-expand parent nodes. Once search yields up to 5 final
candidates, a Discriminator Agent runs the SAME multi-agent-debate mechanism (5 agents, 3
rounds, temp 1.0) to pick the final patch — architecturally identical debate machinery to
what SWE-Debate reuses for its own final discrimination.
Ablation: Partial — flexible vs rigid state transitions (+1.4%), hindsight feedback on/off
(qualitative case study only), state-specific vs generic value prompts (qualitative). Closest
to compute-matching: Appendix J compares Pass@5 from one search run vs Pass@5 from 5
independent baseline runs (excludes GPT-4o "to avoid exorbitant API costs"). Not factorial,
no multi-seed/CIs, all single-run.
Cost reporting: Appendix I: explicit USD table showing MCTS multiplies cost 5-14x over the
non-search baseline (GPT-4o $40.86->$576.00). No token counts, no latency, no cost-accuracy
frontier plot — cost is a static table contrasted post hoc with accuracy, not jointly
visualized.
Relation to A3062: Origin paper for the MCTS-repair architecture A3062 explicitly excludes.
SWE-Debate's repair stage closely follows this design (modified-UCT selection, LLM
value/hindsight-feedback loop, final multi-agent Discriminator debate over candidates).
Running this stage requires test execution to ground the value function — confirmed here via
Docker images + Kubernetes pod-per-instance testbed (Appendix B) — exactly the "Docker
test-harness dependency" A3062's scope note excludes, and the 5-14x cost multiplier
substantiates "much more API cost" in the same sentence. Lets the report describe the
excluded stage mechanistically rather than vaguely.
Report section: Related Work — MCTS-based repair; primary citation for the Scope/Motivation
paragraph justifying exclusion of the repair stage.

## SWE-Effi — arXiv:2509.09853 (arXiv preprint, cs.SE, Sep 2025)
Claim: Introduces 4 normalized "effectiveness" scores (AUC of resolve-rate vs
resource-consumption, capped budgets) and re-ranks 5 scaffolds x 3 LLMs (15 systems) on a
50-instance stratified SWE-bench-Verified subset. Effectiveness is a scaffold x model
interaction, not a scaffold property (e.g. SWE-Agent+Qwen3-32B EuTB=21.8% vs
SWE-Agent+GPT-4o-mini EuTB=5.1%, an 18x token-cost increase for a 28%->10% resolve-rate drop).
Finds a "token snowball" effect and that unresolved attempts consume markedly MORE resources
than resolved ones ("expensive failures": >4x tokens/time for failures vs successes in one
pairing).
Task/benchmark: SWE-bench-Verified, stratified-random 50-instance subset (full 500 "took
upwards of two weeks... several hundred dollars"). Primary raw outcome is plain Resolve Rate;
the real contribution is 4 derived effectiveness scores layered on top.
Method (directly relevant precedent for A3062's cost-per-correctly-localized-instance
metric): raw per-trial metrics = Resolve Rate, CPU Time (local compute, excludes LLM latency),
LLM Calls, Input/Output Tokens, and a derived Normalized Inference Time (regression-fit
provider-agnostic latency proxy, R^2=0.79 on 515k raw API logs). Four capped-AUC scores:
EuTB (tokens, cap 2M), EuCB (dollar cost, cap $1.00, rates from openrouter.ai), EuCTB (CPU
time, cap 30min), EuITB (normalized inference time, cap 30min) — each the AUC of cumulative
resolve-% vs cumulative resource/issue. Appendix Figs 5-7 are literally cost-accuracy frontier
plots (resolve rate y, log-x resource budget, one curve per scaffold x model) — exactly A3062
Deliverable #4's plot family.
Ablation: Not a factorial ablation of one system's internal components — a crossed (5x3)
AUDIT of pre-existing unmodified black-box scaffolds x LLMs, no compute-matching across
systems (uncontrolled cost variance IS the finding, not something removed), single run per
pair, no seeds/CIs, explicitly scope-limited by cost/time.
Cost reporting: Extremely detailed — the closest existing methodological template found for
A3062's cost reporting: per-pair EuTB/EuCB/EuCTB/EuITB tables, raw CPU/inference-time/token/
LLM-request tables split by resolved vs unresolved outcome (exposing the expensive-failure
asymmetry directly), and genuine log-x cost-accuracy frontier plots.
Relation to A3062: The single closest piece of prior art to A3062's overall premise — needs
explicit discussion, not just a citation. Shares: accuracy-alone-is-incomplete framing,
AUC-of-resolve-vs-resource methodology, frontier-plot visualization. Does NOT do: isolate/
ablate one internal architectural mechanism within a single pipeline (no "graph on/off" or
"debate on/off" analogue), and does NOT compute-match — cost variance across systems is a
*finding* here, not removed to isolate causality. Also has no localization-specific or
recall/selection-precision metrics (unit of success is whole-issue resolve rate). The report
should include an explicit "how this differs from SWE-Effi" paragraph: A3062 does a
compute-matched factorial isolating named mechanisms within one pipeline; SWE-Effi audits
uncontrolled black-box systems against each other. A3062 should consider adopting the
AUC-under-a-capped-budget summary statistic and the resolved-vs-unresolved cost breakdown as
diagnostics.
Report section: Related Work — cost-aware evaluation; requires an explicit "how this differs
from SWE-Effi" paragraph given how close the methodology is to A3062's own Deliverable #4.

## Du et al. (Multiagent Debate) — arXiv:2305.14325 (ICML 2024, orig. May 2023)
Claim: Multi-agent debate (default 3 agents, 2 rounds, same base LLM) substantially improves
reasoning/factuality over single-agent baselines across 6 tasks (e.g. Arithmetic 67.0%->81.8%,
GSM8K 77.0%->85.0%, MMLU 63.9%->71.1%). Gains rise monotonically with more agents (up to 7)
and more rounds (up to 4). Debate can recover correct answers even when all agents start
wrong.
Task/benchmark: Arithmetic, GSM8K, Chess Move Prediction/Validity, Biographies (novel
dataset), MMLU — all on `gpt-3.5-turbo-0301`, default 3 agents/2 rounds.
Method: N copies of the same black-box LLM independently answer, then each subsequent round
every agent sees all other agents' latest responses (concatenated or, for >=5 agents,
LLM-summarized) via a fixed consensus prompt and updates its answer. No explicit judge/vote/
termination rule — "final answer" is whatever the population empirically converges to. THIS
IS THE DIRECT ANCESTOR of SWE-Debate's debate mechanism (N-agent, R-round, convergence-based).
Ablation: Closest is a 4-way comparison (Single Agent / Single Agent+Reflection / Majority
Vote / Debate) plus internal sweeps of agent count and round count — but NONE of these are
token-matched: majority voting uses as many single-shot calls as there are agents, while
debate uses agents x rounds calls, and the "equivalent" comparison row doesn't equalize this.
Cost reporting: Only qualitative ("debate is more costly, requiring multiple model instances
and rounds," Limitations) — no token/dollar/latency figures anywhere. Earliest paper in this
trio (May 2023), predates compute-matching discussion entirely; it's precisely the paper
Huang et al. later apply a compute-matched critique to.
Relation to A3062: The direct ancestor of SWE-Debate's mechanism — SWE-Debate's 5-agent,
3-round debate structurally mirrors this N-agent, R-round convergence design. Du et al. never
compute-match debate against a token-equalized baseline; A3062's compute-matched
majority-voting arm closes exactly this gap, first left open here.
Report section: Related Work — multi-agent debate origins and scepticism / Background 3.3.

## Huang et al. (LLMs Cannot Self-Correct) — arXiv:2310.01798 (ICLR 2024)
Claim: Intrinsic self-correction (no oracle/external feedback) DECREASES accuracy vs standard
prompting in nearly every setting across GSM8K/CommonSenseQA/HotpotQA (e.g. GPT-3.5 on
CommonSenseQA: 75.8%->41.8% after 2 rounds). Only "works" when gated by oracle labels — an
unrealistic setting. Separately replicates Du et al.'s EXACT debate protocol on full GSM8K:
at matched response counts, debate UNDERPERFORMS self-consistency (6 responses: 83.2% debate
vs 85.3% self-consistency; 9 responses: 83.0% vs 88.2%).
Task/benchmark: GSM8K (full 1,319-problem test set for GPT-3.5), CommonSenseQA, HotpotQA.
Method: Fixed 3-step self-correction prompt sequence (generate -> self-critique -> revise),
tested with oracle-gated early stopping vs fully intrinsic. Section 4 reuses Du et al.'s exact
prompts/protocol, reframing debate as functionally closer to self-consistency/voting than
genuine debate.
Ablation: Yes — genuinely compute-matched, unusually rigorous for its era (2023). Table 7
compares debate against self-consistency at MATCHED response counts (3/6/9) on the full
GSM8K test set, explicitly motivated by "self-correction... utilizes multiple LLM responses,
thus making it crucial to compare it to baselines with equivalent inference costs." This is
the exact same logic A3062 applies to graph-grounded debate vs compute-matched majority
voting.
Cost reporting: Explicit and central — every results table reports #calls/#responses
alongside accuracy specifically to surface inference cost; the Conclusion explicitly
recommends future self-correction work always include inference-cost analysis and
call-matched baselines. Plausibly the EARLIEST paper to apply compute-matching specifically
to Du et al.'s multiagent debate method.
Relation to A3062: The single most important citation for H2 (debate's contribution shrinks
under compute matching). It's a miniature, single-benchmark preview of A3062's whole
factorial logic (uncontrolled multi-agent claim redone compute-matched), applied to plain
GSM8K debate rather than graph-grounded SWE-bench localization. Its finding that LLMs can't
reliably judge their own correctness without external signal also supports a mechanistic
story for H2: without a verifier, extra debate rounds may just relabel consensus rather than
fix errors.
Report section: Related Work — multi-agent debate origins and scepticism / Background 3.3.

## Cemri et al. (MAST Taxonomy) — arXiv:2503.13657 (NeurIPS 2025 D&B Track)
Claim: MAS gains over single-agent/best-of-N baselines are often minimal; measures 41%-86.7%
failure rates across 7 open-source MAS frameworks via 1,642 annotated traces (MAST-Data).
Introduces MAST, a 14-failure-mode taxonomy across 3 categories (Grounded Theory, kappa=0.88
inter-annotator agreement; LLM-as-Judge annotator at 94% accuracy/kappa=0.77 vs humans).
Guided interventions informed by MAST yield up to +15.6% task-success (adding verification to
ChatDev) — but framed as partial fixes, not solutions.
Task/benchmark: 7 MAS (ChatDev, MetaGPT, HyperAgent, AppWorld, AG2/MathChat, Magentic-One,
OpenManus) across coding/math/general-agent benchmarks including SWE-Bench Lite (for
HyperAgent). Models: GPT-4/4o, Claude-3.7-Sonnet, Qwen2.5-Coder-32B, CodeLlama-7b.
Method: 3 top-level categories: System Design Issues (44.2% of failures: disobeying task/role
spec, step repetition, lost history, unaware termination conditions), Inter-Agent
Misalignment (32.3%: conversation reset, failure to clarify, task derailment, information
withholding, ignored input, reasoning-action mismatch), Task Verification (23.5%: premature
termination, no/incomplete verification, incorrect verification).
Ablation: Not classical ablation, but controlled comparisons: same MAS x 2 backbones
(isolating model effect on failure distribution), same LLM x 2 architectures (isolating
architecture effect), and intervention case studies with Wilcoxon significance tests over 6
repetitions. None are compute/token-matched — model, architecture, prompt and topology all
vary without equalizing inference budget.
Cost reporting: Only for the paper's OWN annotation pipeline (avg $1.8/trace for the LLM
judge), not for the underlying MAS methods — cites (via Kapoor et al.) that MAS gains are
"often minimal compared to simple baselines" but doesn't itself measure this under a
controlled budget.
Relation to A3062: MAST's 14 failure modes are a ready-made coding scheme A3062 can apply
post hoc to its own factorial results — e.g. classifying debate non-improvements against
FM2.6 (Reasoning-Action Mismatch) or FM3.2/3.3 (No/Incorrect Verification). Its headline
framing is a second, independent (2025, taxonomy-based) corroboration of the scepticism line
Huang et al. established via controlled comparison, reinforcing H2. Its verification-failure
category loosely parallels A3062's own recall-vs-selection split.
Report section: Related Work — multi-agent debate origins and scepticism / Background 3.3;
also Discussion/Analysis as an error-categorization framework for A3062's own results.

## Peng et al. GraphRAG Survey — arXiv:2408.08921 (ACM J.ACM/TOIS, Sep 2024)
Claim: First systematic GraphRAG survey. Central taxonomy: Graph-Based Indexing (G-Indexing)
-> Graph-Guided Retrieval (G-Retrieval) -> Graph-Enhanced Generation (G-Generation), each with
its own sub-categorization (indexing method, retriever type/paradigm/granularity, generator
type/format/enhancement-stage).
Task/benchmark: N/A — survey spanning dozens of tasks/benchmarks (KBQA, CSQA, entity linking,
fact verification, recommendation, etc). Mentions exactly ONE code-adjacent system (DepsRAG,
under "Other" applications) — omits LocAgent/CoSIL/SWE-Debate entirely, but only because all
three postdate the survey's Sep 2024 publication (temporal, not a judgment call).
Method: The taxonomy itself. CRITICAL FINDING for A3062's terminology: the survey does NOT
name an "LLM-extracted vs static-analysis" axis explicitly — its own split is "Open Knowledge
Graphs" vs "Self-Constructed Graph Data," and every example given under Self-Constructed Data
(including Edge et al./Microsoft GraphRAG) is an LLM-extraction pipeline. No code-dependency-
graph construction method is described as its own category; DepsRAG is filed only under
application domains, not cross-referenced into the G-Indexing/Retrieval/Generation framework.
Ablation: None — review paper, no experiments.
Cost reporting: No empirical benchmarking; only qualitative forward-looking notes (graphs of
thousands vs industrial millions/billions of entities; long linearized-graph contexts raise
inference cost).
Relation to A3062: The correct citation for the general GraphRAG taxonomy A3062's background
invokes, but must be cited carefully — its own "self-constructed graph data" examples are
overwhelmingly the LLM-extraction lineage (real inference cost to build the graph), whereas
A3062's graph (and SWE-Debate's) is recovered by deterministic static analysis of Python ASTs
with ZERO LLM calls at construction time — closest to the survey's "graph indexing" method
(full-structure BFS/shortest-path retrieval) but built via a construction source the survey
never names as its own category. Report should state this distinction explicitly on first
use of "graph-grounded"/"GraphRAG" so a reader doesn't assume Microsoft's community-
summarization pipeline is what's being ablated.
Report section: Related Work — graph-grounded retrieval (background/taxonomy); cite early,
before describing SWE-Debate's actual graph construction.

## Edge et al. GraphRAG (Microsoft) — arXiv:2404.16130 (preprint under review, v2 Feb 2025)
Claim: For query-focused summarization (QFS) over large private text corpora (~1M tokens), an
LLM-built entity KG partitioned into a community hierarchy and pre-summarized bottom-up beats
vector RAG on comprehensiveness/diversity (win rates 72-83%/62-82% across two datasets,
p<.01/.001), while vector RAG stays more "direct" (a deliberate control criterion).
Task/benchmark: QFS over podcast transcripts and a news-article corpus (~1M tokens each); no
existing QA benchmark — the paper generates its own 125-question "global sensemaking" set per
corpus, scored by an LLM judge on comprehensiveness/diversity/empowerment/directness. Entirely
text-corpus tasks — no code, no SWE-bench.
Method: Chunk -> LLM-PROMPTED entity/relationship/claim extraction per chunk -> aggregate into
a KG -> hierarchical Leiden community detection (levels C0-C3) -> bottom-up LLM community
summarization -> query-time map-reduce over community summaries. THIS IS THE OTHER GRAPHRAG
LINEAGE: the graph literally does not exist without per-corpus LLM inference.
Ablation: Effectively yes — GraphRAG at 4 hierarchy levels (C0-C3) vs a graph-free map-reduce
baseline (TS) vs vector RAG (SS). Ablates graph-vs-no-graph and how much hierarchy is needed;
no multi-agent/debate ablation (single-agent, non-adversarial pipeline throughout).
Cost reporting: Query-time cost is a headline result (Table 2: root-level C0 needs only
2.3-2.6% of TS's query-time tokens, "9x-43x fewer"). BUT graph-CONSTRUCTION (indexing) cost is
reported only as wall-clock ("281 minutes for the Podcast dataset" on gpt-4-turbo), never as
tokens or dollars — a real one-time LLM cost (entity/relationship/claim extraction across
every chunk, plus a self-reflection "gleaning" loop that multiplies calls, plus community
summarization at every hierarchy level) left unquantified. This is the paper's one significant
cost-transparency gap.
Relation to A3062: The OTHER GraphRAG lineage the FYP must distinguish by construction method,
not by name, since "GraphRAG" is this paper's trademark term. If A3062's design were ever
extended to include an Edge-et-al.-style LLM-extracted graph as a comparison arm (it currently
isn't — static-analysis-only), that arm's graph-construction cost (this paper's unquantified
281-minute indexing pass) would need its own token/dollar accounting before any comparison
could be called compute-matched. Citing Peng et al.'s taxonomy alongside this paper is what
makes the distinction precise for the report.
Report section: Related Work — graph-grounded retrieval (background/taxonomy); cite alongside
Peng et al., early, specifically to draw the LLM-extracted-graph vs static-analysis-graph line
before SWE-Debate's graph construction is described — highest risk of reader confusion if not
disambiguated at first mention.

## MacNet — arXiv:2406.07155 (ICLR 2025, Mar 2025)
Claim: Organizing LLM agents into DAG topologies lets multi-agent collaboration scale to
1000+ agents; quality follows a "collaborative scaling law" (logistic growth in agent count);
irregular/random topologies statistically outperform regular ones; divergent (tree/star-like)
structures beat convergent ones.
Task/benchmark: MMLU, HumanEval, SRDD (repo-level requirement-to-code), CommonGen-Hard. No
SWE-bench, no fault localization.
Method: Agents placed on DAG nodes/edges (chain/star/tree/mesh/layer/random topologies);
supervisory-critic/compliant-actor bipartition drives dual-agent refinement in topological
order; memory-control mechanism propagates only the latest artifact (not full history)
between adjacent agents, keeping token growth linear rather than quadratic in agent count.
GPT-3.5 backbone, default 3 rounds.
Ablation: Compares 6 topology types across scales (2^0-2^6 agents); density/shape/direction
analyses; a "profile" ablation (simplified agents) shows a 3.67% avg quality drop. NOTABLY:
one of very few papers in this space that even gestures at compute-matching — equalizes LLM
CALL COUNTS across single-agent baselines (majority voting, best-of-N) when arguing
multi-agent structure adds more than raw calls, finding majority voting improves only 0.9%.
Single-run per topology/scale, no factorial crossing of "graph structure" x "collaboration"
as independent factors.
Cost reporting: No dollar/latency figures — only theoretical token-complexity analysis
(O(n) vs O(n^2) context growth) and empirical token/artifact-length counts as compute proxies.
Relation to A3062: Not code/SWE-bench or adversarial debate specifically — don't force into
H1-H4 framing. Its narrow value: one of the few papers attempting even call-count parity for
single-agent baselines, and its finding that naive call-count parity barely helps (+0.9%) is
a precedent supporting A3062's premise that raw budget alone isn't what makes multi-agent
setups work (consistent with H2's spirit, though this isn't true token/compute matching,
just call-count matching). Its topology-density findings loosely echo "structure matters more
than volume" (H1-adjacent). Reports no cost, no seeds/CIs, no true factorial design — another
field-wide-problem example.
Report section: Related Work (multi-agent topology/scaling background); optional Motivation
citation as a partial, informal compute-matching attempt outside the FL/debate literature.
Not a direct experimental comparator for H1-H4.

## LLM4FL — arXiv:2409.13642 (arXiv preprint, Mar 2025)
Claim: A 3-agent LLM fault-localization pipeline (graph-based RAG code navigation + Reflexion
self-critique re-ranking) beats LLM baselines AutoFL and AgentFL/SoapFL by 18.55% and 4.82%
Top-1 respectively, is competitive with SUPERVISED techniques (DeepFL, Grace) with no
task-specific training, at ~$0.05/bug (roughly the cheapest baseline's cost).
Task/benchmark: Defects4J v2.0.0 (Java), 675 real faults across 14 projects, method-level FL,
Top-N accuracy. Not SWE-bench, not Python — but the closest-kin FAULT LOCALIZATION paper found
in this entire review.
Method: 3 GPT-4o-mini agents: Context Extraction (order-aware coverage-data chunking by
Ochiai suspiciousness + failure-reason extraction), Debugger (Graph-RAG navigation of an
inter-procedural call graph via get_MethodBody/get_CallGraph tools -> initial ranking),
Reviewer (Reflexion-style self-critique re-ranking, NOT multi-agent adversarial debate — a
single agent iteratively critiquing itself).
Ablation: Leave-one-component-out (single system, not multi-agent-debate ablation): w/o graph
navigation drops Top-1 16.53% (327->273); w/o order-aware division drops 23.24% (327->251,
LARGEST effect); w/o Reflexion drops 11.31% (327->290). A separate RQ shows the initial
ordering heuristic ALONE swings Top-1 by up to 22 points (299->366) — a confound orthogonal to
the graph/reflexion factors. All single-run over the full 675-fault set, no seeds/CIs,
components removed one-at-a-time (not factorial), no compute added back on removal (not
compute-matched).
Cost reporting: Unusually, yes — per-bug dollar cost from token pricing (LLM4FL ~$0.05/bug vs
AutoFL ~$0.065 vs SoapFL/AgentFL ~$0.055), explicitly claimed "comparably cost-effective."
But only ONE aggregate number for the whole pipeline — not broken out per ablation arm, so
graph-navigation cost vs reflexion cost can't be isolated.
Relation to A3062: HIGH relevance — close kin to A3062's design, missing exactly
compute-matching and factorial structure. Isolates a graph-grounding-like factor (H1-adjacent)
and a self-refinement factor (Reflexion — H2-adjacent, but single-agent self-critique, not
true multi-agent adversarial debate, so map onto H2/H3 as a loose structural analogy only) via
leave-one-out ablation on a REAL fault-localization benchmark. Its quantified ordering-confound
(up to 22 points of Top-1 from input order alone) is a concrete warning for A3062: constructing
single-chain vs multi-chain candidate lists must control for ordering, or ordering effects
could masquerade as graph-grounding effects. Positive precedent: it DOES report cost (rare in
this review) — cite that positively — but still single-run, unseeded, non-compute-matched,
non-factorial, and conflates three candidate benefit sources (coverage/division, graph nav,
reflexion) rather than isolating two orthogonal factors the way A3062 intends.
Report section: Related Work — closely related graph+agent fault-localization system (adjacent
to SWE-Debate/LocAgent/CoSIL); also Methodology/Motivation as a concrete example of a
single-run, non-compute-matched, non-factorial leave-one-out ablation A3062 explicitly
improves upon, and as one of the few papers that reports cost at all.

## LLM Agents for SE Survey — arXiv:2409.02977 (arXiv preprint, orig. Sep 2024, v2 Dec 2025)
Claim: Systematic survey of 124 papers on LLM-based agents for SE, organized by SE-task
(requirements, codegen, static checking, testing, debugging [FL+repair], IT ops, end-to-end)
and by agent-architecture (planning, memory, perception, action, foundation LLM; multi-agent
roles/collaboration/information-flow; human-agent collaboration).
Task/benchmark: None of its own — synthesizes benchmarks/results from the 124 surveyed papers,
runs no new experiments.
Method: Systematic-review methodology (DBLP keyword search, 10,362 raw hits -> 67 papers after
screening, + snowballing + author feedback -> 124 final).
Ablation: N/A. Its Debugging subsection (4.5.1) discusses AgentFL and AutoFL (both also cited
as baselines in LLM4FL above) and its multi-agent-systems discussion catalogs known
coordination-failure patterns (role drift, infinite loops, cascading errors from bad feedback,
degraded long-context reasoning) — descriptive, not empirical.
Cost reporting: N/A (no experiments), though notes in passing that iterative/multi-agent
refinement "introduces significant overhead... in terms of efficiency and cost" as a
recognized open challenge — echoes A3062's complaint without quantifying it.
Relation to A3062: Low-to-moderate direct relevance to H1-H4 (tests/ablates nothing), but
useful as orientation: a comprehensive, current map of the LLM-agents-for-SE space that names
and situates AgentFL/AutoFL (precursor FL agents also discussed in LLM4FL) and documents
multi-agent coordination-failure modes thematically aligned with the Cemri et al. MAST line
already in this review. Should not be cited as evidence for/against any specific hypothesis —
useful for establishing field scope and sourcing pointers to individual FL-agent baselines.
Report section: Related Work/Background — general landscape citation and pointer source for
locating specific FL-agent baselines; not applicable to the core experimental/ablation-design
sections.

## Tran & Kiela (Single-Agent vs Multi-Agent, Equal Thinking-Token Budgets) — arXiv:2604.02460 (Stanford preprint, Apr 2026)
Claim: THE flagship compute-matched precedent. Theoretical: models MAS messages M as a
function of the full single-agent context C (Markov chain Y<->C<->M); by the Data Processing
Inequality, a single agent with full context is guaranteed Pe(C) <= Pe(M) — SAS is
info-theoretically at least as good as any MAS built on message summaries, under a FIXED
thinking-token budget. Empirically across 2 datasets (FRAMES, MuSiQue-4hop), 3 model families
(Qwen3-30B-A3B, DeepSeek-R1-Distill-70B, Gemini-2.5), 5 MAS architectures (Sequential,
Subtask-parallel, Parallel-roles, Debate, Ensemble): SAS is best or statistically
indistinguishable from best at every budget except the lowest (100 tokens), using far fewer
actual tokens. BOUNDARY CONDITION formalized as context degradation C~alpha=T_alpha(C):
crossovers found under corruption-type degradation (substitution: SAS leads at alpha=0.3,
ties at 0.5, Sequential MAS wins at 0.7; masking: similar, weaker pattern) but NOT under pure
distractor injection (SAS stays ahead throughout k=10-30 distractors, margin only shrinks —
no crossover observed within their tested dosage).
Task/benchmark: FRAMES and MuSiQue (4-hop) multi-hop world-knowledge QA, LLM-judge scored.
Degradation experiments only on MuSiQue+Qwen3-30B-A3B. Gemini-version and paraphrasing
robustness sweeps included.
Method: Equal-budget enforcement via a hard requested-token cap split across each
architecture's own topology (Sequential splits evenly across k steps; Debate splits between 2
debaters + budget-neutral aggregator). Explicitly NOT extended-reasoning-vs-best-of-N — budget
matching is structural (same total requested allotment). Diagnoses a Gemini-specific
token-accounting artifact (API-reported tokens up to 4.7x visible-content tokens) as a
measurement confound, not a real finding.
Ablation: Full grid (2 datasets x 3 model families x 6 architectures x 6 budget levels), 95%
bootstrap CIs, a checkpoint-robustness sweep, a paraphrasing/contamination check, and a
fine-grained error-bucket analysis. NOT factorial across two independent architectural factors
(single SAS-vs-MAS-variant axis x budget, not a 2x2 the way A3062 crosses graph x debate). No
wall-clock, no dollar cost — cost accounting is tokens only. CIs are bootstrap over the eval
set, not multi-seed variance — weaker than A3062's planned multi-seed design.
Cost reporting: Precise and self-critical — tracks 3 separate token quantities for Gemini
(API-reported, visible-content word count, proxy count) to diagnose the accounting artifact
above; compares on matched REQUESTED budget while reporting measured consumption separately.
No dollar/latency reporting anywhere.
Relation to A3062: Direct theoretical/methodological ancestor of Motivation and H1/H2. H4
explicitly operationalizes the boundary condition — A3062's "candidate density" is closest to
this paper's DISTRACTOR-INJECTION condition specifically, not masking/substitution. IMPORTANT
CAVEAT: distractor injection was the WEAKEST of their four degradation levers — SAS stayed
ahead throughout their tested dosage, crossovers only appeared under corruption-type
degradation. If A3062 models candidate density as additive similar-but-wrong candidates
(closest to distractor injection), this precedent predicts only a modest narrowing of debate's
disadvantage, not necessarily a crossover — H4 may need either much higher "dosage" than
k=10-30, or a more corruption-like operationalization (candidates that actively mislead, not
just resemble). Their continuous-scalar degradation measurement (alpha, k) swept against
accuracy is directly transferable to a continuous candidate-density metric. As a Methodology
template: match on requested budget, split per-topology, audit actual-vs-requested separately
— A3062 should cite and mirror this while noting it goes further (factorial 2x2, recall/
selection decomposition, wall-clock+dollar cost, all absent here).
Report section: Motivation (primary theoretical grounding — DPI argument, boundary condition);
Related Work — compute-matched evaluation (flagship exemplar); Methodology (compute-matching
protocol template); Discussion of H4 (boundary-condition precedent + distractor-injection
caveat).

## Inside the Scaffold — arXiv:2604.03515 (preprint, cs.SE, Apr 2026)
Claim: NOT an experimental/benchmarking paper — a purely qualitative, source-code-level
architectural taxonomy of 13 open-source coding-agent scaffolds (Aider, OpenHands, SWE-agent,
mini-swe-agent, AutoCodeRover, Agentless, Moatless Tools, DARS-Agent, Prometheus, OpenCode,
Gemini CLI, Codex CLI, Cline), every claim pinned to a file path + line number + git commit.
Reports ZERO performance numbers — Section 3.5 states this is deliberate: "benchmark scores
confound scaffold architecture with model capability, prompt engineering, and incidental
configuration choices." Finds architectures occupy continuous spectra (control loop: fixed
pipeline -> ReAct -> phased loop -> tree search -> full MCTS; tools 0-37), 5 loop primitives
freely composable (11/13 agents layer multiple), and dimensions converge where external
constraints dominate (tool categories, edit format, Docker isolation) but diverge on genuinely
open questions (context compaction, state management, multi-model routing).
Task/benchmark: No datasets — a systematic qualitative source-code review (open-coding/
grounded-theory) of 13 agent codebases selected from 22 candidates via inclusion criteria.
296 extracted claims verified against clones: 267 confirmed, 19 corrected, 10 minor
simplifications.
Method: 12 taxonomy dimensions across 3 layers (control architecture; tool & environment
interface, including context-retrieval paradigm — keyword/regex, PageRank repo-map, AST-aware,
knowledge-graph traversal e.g. Prometheus, embedding search e.g. Moatless Tools, hierarchical
file->class->line e.g. Agentless, classical SBFL e.g. AutoCodeRover; resource management).
Ablation: None in the ML sense — deliberate scope choice, arguing current SWE-bench
comparisons can't be fixed by MORE benchmark runs since they confound scaffold/model/config,
requiring architectural decomposition instead. Section 5.5 explicitly PROPOSES the kind of
controlled comparison A3062 executes ("fixing tool set while varying control loop," "fixing
model while varying scaffold") but never runs it.
Cost reporting: No cost measured directly, but architecturally explains cost patterns from
other papers (Fan et al.'s "token snowball" and "expensive failures" mapped onto its own
context-compaction dimension).
Relation to A3062: Near-verbatim precedent for A3062's premise. Section 5.5: "SWE-bench
comparisons between agents confound scaffold design, model choice, and configuration in a
single metric" — backed by concrete evidence (Codex CLI routes across 4 models in one run;
SWE-agent/AutoCodeRover use per-attempt model cycling, so a single benchmark run may silently
involve multiple models). Two further leverage points: (1) its "sampling-vs-iteration"
cross-cutting theme (independent-sample-then-vote vs feedback-driven iterative retry) is
structurally analogous to A3062's recall-vs-selection-precision split, giving external
taxonomic vocabulary for that decomposition; (2) its finding that loop primitives and
context-retrieval paradigms are SEPARATELY COMPOSABLE (Moatless Tools decouples its executor
from orchestration strategy) taxonomically supports treating "graph grounding" and "debate" as
two independent, factorially crossable factors — the load-bearing assumption behind A3062's
2x2 design. Note: SWE-Debate itself is NOT in the 13-agent corpus.
Report section: Related Work — compute-matched/architecture-isolated evaluation (primary
anchor); Motivation (field-level statement of A3062's premise); Methodology (supporting
footnote for the factorial decomposition's taxonomic justification).

## ColMAD (When and Why Does MAD Fail?) — arXiv:2510.20963 (ICML 2026 workshop / v2 Jul 2026)
Claim: Categorizes existing multi-agent debate into CopMAD (competitive, rewarded for
convincing the judge regardless of correctness) and CosMAD (consensus-seeking). Proves via a
game-theoretic model (judge decision = accumulated log-likelihood ratio) that CopMAD's
Nash-equilibrium risk EQUALS the no-debate baseline risk — the debate transcript carries ZERO
additional information at equilibrium (a "babbling equilibrium," Crawford & Sobel-style cheap
talk), an even starker, TIGHT version of Tran & Kiela's DPI bound. Proposes ColMAD
(utility = each message's mutual-information contribution to Y), proven to weakly dominate
both: V_col <= V_cos <= R(X0) = V_cop. Empirically (ReaLMistake): CopMAD/CosMAD consistently
UNDERPERFORM single-agent, sometimes below the weaker of the two agents (up to -15pts F2 for
CopMAD). ColMAD consistently outperforms CopMAD/CosMAD and beats best SA by up to 4pts,
including under matched token/call budgets vs self-consistency-scaled SA.
Task/benchmark: ReaLMistake (3 objective LLM-error-detection tasks), extended to GSM8K,
AIME-2024, Anthropic-Harmful (safety). Multiple LLM backbones/pairings.
Method: Formal Nash-equilibrium games (3 utility structures) + oracle-collaboration-potential
analysis (cross-family LLM pairs show 30-60% error-reduction potential vs much less for
same-family pairs) + rubric-coded "debate hacking" behaviors (fabricated evidence,
overconfidence, redundant repetition) + a theory-to-implementation mapping (quote-based
evidence verification, self-auditing, confidence calibration).
Ablation: Component ablation (removing quote-system/confidence/self-auditing individually and
jointly) shows the core advantage survives even with all three removed — gain is attributable
to the incentive structure, not prompt tricks. CRITICAL: a homogeneous-debater ablation shows
even ColMAD underperforms single-agent when both debaters share the SAME LLM — heterogeneity,
not protocol design alone, is necessary. Judge-choice and round-count (1-5) robustness checks;
10-seed 95% CIs on the protocol comparison. NOT factorial across two independent architectural
factors (single "protocol" axis x debater-pair x budget). Cost reporting is token-only.
Cost reporting: Token cost per protocol (ColMAD ~13.2-13.3K vs CopMAD ~11.4-11.5K vs
CosMAD ~6.6-9.5K) — argues CopMAD spends comparably to ColMAD yet performs WORSE than SA,
directly demonstrating protocol/incentive design (not raw compute) drives the outcome. A
genuine matched-compute comparison (tokens-per-sample and calls-per-sample vs
self-consistency-scaled SA curves) — second usable precedent alongside Tran & Kiela. No
dollar/latency reporting.
Relation to A3062: Formally REINFORCES Tran & Kiela (CopMAD's zero-information equilibrium is
a tight version of the DPI bound) while showing a redesigned, incentive-aligned protocol CAN
beat compute-matched SA — but only under TWO conditions: (a) incentives rewarding information
contribution over persuasion/consensus, and (b) AGENT HETEROGENEITY (same-LLM debaters fail
even under ColMAD). This surfaces a SECOND, orthogonal moderator for "when debate earns its
tokens" beyond H4's candidate-density story: model/error-profile diversity. IMPORTANT THREAT
TO VALIDITY: CLAUDE.md commits A3062 to a single model backbone (DeepSeek-V3-0324) across all
debate agents for compute-matching purity — per this paper's own homogeneous-debater ablation,
that choice may itself structurally suppress any debate benefit, independent of and prior to
compute-matching or candidate-density effects. H2 may be partially confounded with this;
SWE-Debate's own debate design is also not heterogeneous-model, so this is a shared limitation
worth naming explicitly, not something A3062 introduces. H3 has a loose analogue in the
protocol-design x heterogeneity interaction (their Table 9).
Report section: Motivation (qualifying/nuancing citation alongside Tran & Kiela — debate fails
under standard incentives, but incentive redesign can reverse this under specific conditions);
Related Work — compute-matched evaluation (second exemplar); dedicated Discussion subsection
cross-referencing H2/H3/H4, flagging the agent-homogeneity confound as a threat to validity
given A3062's single-backbone constraint.

## BugLocator — DOI:10.1145/2337223.2337226 (ICSE 2012, Zurich)
Claim: A revised Vector Space Model (rVSM) combined with signal from textually similar
previously-fixed bugs ranks source files more accurately for bug localization than existing
IR methods (VSM, LDA, LSI, SUM). Pre-LLM, pure IR/text-similarity — no LLM, no execution
traces.
Task/benchmark: File-level bug localization from NL bug reports, 4 open-source Java projects
(Eclipse v3.1, SWT, AspectJ, ZXing), >3,000 fixed bugs, 391-12,863 files/project.
Method: FinalScore = (1-alpha)*rVSM (cosine similarity + length-adjustment boosting larger
files) + alpha*SimiScore (transfers signal from similar past bugs via a 3-layer heterogeneous
graph: new bug -> similar past bugs -> files they touched), alpha tuned to 0.2-0.3.
Ablation: rVSM vs classic VSM, with/without similar-bug info, alpha sweep, baseline
comparison — deterministic method (no LLM stochasticity), single-run with t-test significance
rather than seeds/bootstrap CIs (not comparable in kind to the FYP's rigor gap, since there's
no run-to-run variance to average over for a non-learned method).
Cost reporting: None — no compute/API cost concept applies to lightweight lexical retrieval;
only "lines of code a developer must examine" discussed as a practical cost proxy.
Relation to A3062: Low/background relevance only — predates LLMs and multi-agent systems
entirely, shares no methodology with debate/compute-matching/LLM-graph-grounding. Useful
purely as historical grounding for the IR-based fault-localization lineage that LocAgent/
CoSIL/SWE-Debate supersede. Does not bear on H1-H4.
Report section: Background/Related Work — brief historical mention in the FL thread
(predecessor to graph-grounded FL), not ablation/methodology sections.

## Agent Forest (More Agents Is All You Need) — arXiv:2402.05120 (TMLR, Oct 2024)
Claim: Simply increasing the number of independently sampled LLM outputs, combined via
similarity-weighted majority voting ("Agent Forest"), improves accuracy scaling with ensemble
size, is largely orthogonal to (stackable with) sophisticated prompting/collaboration
methods, and correlates with task difficulty.
Task/benchmark: GSM8K, MATH, MMLU, a chess-state-tracking task, HumanEval (BLEU-based voting
for code). Backbones: Llama2-13B/70B-Chat, GPT-3.5-Turbo, GPT-4.
Method: Sample N outputs -> pick highest cumulative pairwise similarity to the rest as
consensus (occurrence-frequency for closed-form, BLEU for code/open text). Homogeneous
independent sampling + voting — no role specialization or argument exchange, explicitly
framed as simpler than the "complicated" multi-agent frameworks it's compared against.
Ablation: Sweeps ensemble size 1-40 across 3 model scales x 5 tasks (10 runs averaged, std
error bars); tests stacking on CoT/ZS-CoT/SPP/Debate/Reflexion — NOTABLY, stacking with Debate
(Du et al.) DEGRADES performance for Llama2-13B/70B, attributed to "noise from referencing
other agents' answers" disrupting code-logic coherence — a direct data point that naively
adding debate on top of a sampling baseline can hurt. Not a designed compute-matched factorial
in A3062's sense; variance is standard error over repeated runs, not seeded bootstrap CIs.
Cost reporting: Explicit token-usage table per method/task, accuracy-vs-token-budget plots —
closer to real cost-awareness than most multi-agent papers, though never converted to dollars;
flags the escalating-cost problem of multi-call methods as unresolved future work.
Relation to A3062: Directly relevant to H2 and A3062's core complaint. Empirically
demonstrates the exact confound A3062 isolates: naive compute scaling via independent
sampling + majority vote — not smarter inter-agent collaboration — drives much of the gain
typically credited to sophisticated multi-agent frameworks, and shows this simple baseline is
compatible with (sometimes better than) stacking on debate. Direct precedent for A3062's
"compute-matched majority-voting arm... included as the cheap baseline." Its
Debate-degrades-performance finding foreshadows a plausible failure mode A3062 should watch
for in its own multi-round debate cells. No code/SWE-bench task, no graph-grounding factor —
doesn't speak to H1/H3/H4 directly.
Report section: Related Work — compute-matched evaluation/multi-agent-debate skepticism
(alongside Du et al., Huang et al., Cemri et al.); directly citable in Methodology to justify
the compute-matched majority-voting baseline arm.

## Reasoning in Token Economies — arXiv:2406.06461 (arXiv preprint, Jun 2024)
Claim: When MAD/Reflexion/Tree-of-Thoughts/Plan-and-Solve/Least-to-Most/Progressive Hints are
compared against CoT+self-consistency (CoT SC) under an EQUALIZED inference budget (queries,
tokens, or $), CoT SC matches or beats the more complex strategies on almost every
dataset/model; MAD's and Reflexion's advantages shrink or invert once budget is held constant,
and MAD can even plateau/degrade with more budget because multi-round conditioning on prior
answers REDUCES response diversity (falling entropy across rounds vs flat entropy for SC).
Task/benchmark: GSM8K, MATH, TheoremQA, HotpotQA, CSQA, plus Game of 24 for a dedicated ToT
ablation. 7 strategies x 5 models (GPT-3.5, GPT-4, Mistral-7B, Llama-2-70b, Mixtral-8x7B). No
code/SWE-bench task.
Method: A "budget-aware evaluation framework" with 3 interchangeable budget axes (API
monetary cost, total tokens, number of queries), plotted as Performance@Budget curves instead
of single-point comparisons. Decomposes ToT/Reflexion into proposer-budget vs
evaluator-budget to isolate where gains come from (e.g. weak evaluator + strong proposer keeps
most accuracy at ~5x lower cost than strong evaluator).
Ablation: Itself a compute-matched re-evaluation, closely analogous in spirit to A3062 —
re-runs MAD (Liang et al., a close relative of SWE-Debate's debate module) etc. across
matched budgets, factorially decomposes ToT's evaluator/proposer budgets (4 setups), reports
across 5 backbones with error bands over repeated sampling (not single-run points).
Cost reporting: Central, not an afterthought — explicit dollar figures (e.g. GPT-4 ToT with
weak evaluator: $33.53 for 72% vs strong evaluator: $159.87 for 76%), alongside token/query
counts, argued as the most holistic of the three budget metrics.
Relation to A3062: The single closest methodological sibling among all reviewed papers,
alongside Tran & Kiela and Inside the Scaffold. Performs, for general reasoning, essentially
the move A3062 performs for SWE-bench localization: re-run a debate method under matched
compute instead of the original budget, find the advantage shrinks/vanishes/reverses — direct
external evidence for H2 in a different domain. Its diversity-collapse mechanism (falling
entropy across debate rounds) is a concrete hypothesis A3062 should test in its own 1/2/3-round
debate cells. Its dollar-cost reporting and proposer/evaluator factorial decomposition are
close analogues of what's missing from SWE-Debate's own ablation. Says nothing about graph
grounding (no H1/H3 bearing); domain transfer should be treated as suggestive, not
confirmatory.
Report section: Related Work — core citation in the compute-matched evaluation thread (primary
precedent alongside Tran & Kiela); also Methodology (budget-matching design template) and
Discussion (comparing A3062's H2 result against this paper's MAD-vs-SC finding).

## Agent-Eval Taxonomy — arXiv:2507.21504 (KDD '25, Toronto, Jul 2025)
Claim: Proposes a 2D taxonomy for LLM-agent evaluation (objectives: behavior/capabilities/
reliability/safety, x process: interaction mode/data/metrics/tooling/context), arguing current
practice is fragmented and under-serves enterprise needs (RBAC, compliance, long-horizon
reliability).
Task/benchmark: None of its own — catalogs ~100+ existing agent benchmarks (AgentBench,
WebArena, tau-bench, HELM, SWE-bench cited as one example), no evaluation run.
Method: Qualitative literature synthesis/taxonomy construction. No experiments.
Ablation: None — not empirical.
Cost reporting: None measured. Discusses cost/latency only as a metric CATEGORY, and future
work explicitly calls for "Time- and Cost-Bounded Evaluation Protocols" — names the gap
without filling it.
Relation to A3062: Low relevance, flag for review — never discusses multi-agent debate,
graph-grounded retrieval, or SWE-bench localization, and performs no ablation, so cannot
support/refute H1-H4 empirically. Only connection is rhetorical: an independent
enterprise-ML-community voice making the same generic complaint A3062 is built on.
Report section: Introduction/Related Work — weak, non-specific general motivation only; don't
lean on it past the framing paragraph.

## LLM-Agent-SE Survey — arXiv:2510.09721 (arXiv preprint, cs.SE, Oct 2025)
Claim: First survey jointly taxonomizing *solutions* (prompt-based, fine-tuning-based,
agent-based) and *benchmarks* (codegen, translation, repair, other) for LLM-powered SE,
reviewing 150+ papers, connecting 50+ benchmarks to solution paradigms; proposes a unified
pipeline and future directions (multi-agent collaboration, self-evolving systems, formal
verification).
Task/benchmark: Meta-survey — no benchmark of its own; covers SWE-Bench, DebugBench,
Multi-SWE-bench, GHRB among program-repair benchmarks.
Method: Systematic review (top-tier venues + arXiv/OpenReview, 2023-2025), taxonomy/pipeline
construction. No original experiments.
Ablation: None — "ablation" doesn't appear in the paper; doesn't analyze SWE-Debate or any
specific debate ablation.
Cost reporting: No empirical costs, but Section VIII.B explicitly diagnoses an "evaluation
crisis" (over-reliance on pass@k, no economic/operational metrics) and Section VIII.D states
current multi-agent SE frameworks "rely on simple coordination mechanisms" and calls for
benchmarks measuring "coordination efficiency, communication overhead" — independently names
the exact gap motivating A3062.
Relation to A3062: Moderate, background-only relevance. Surveys the graph-grounded code-
retrieval lineage (Code Graph Model, LingmaAgent, RepoUnderstander) A3062 already tracks, and
collaborative (non-adversarial) multi-agent SE frameworks (MAGIS, AgileCoder, MASAI,
Co-PatcheR) as contrast cases showing "multi-agent" in SE more often means role-specialized
pipelines than SWE-Debate-style debate. Its VIII.D text is citable as the field itself flagging
the coordination-cost evaluation gap, but performs no ablation and never touches debate
specifically — no evidence toward H1-H4.
Report section: Related Work — graph-grounded code retrieval background, multi-agent SE
taxonomy; also citable in Introduction for the "coordination-cost evaluation gap" claim.

## Agent Scaling Science — arXiv:2512.08296 (arXiv preprint, cs.AI, v3 Apr 2026)
Claim: Establishes quantitative "scaling principles" predicting when multi-agent coordination
helps vs hurts: controlled comparisons across 5 architectures (SAS; MAS-Independent;
MAS-Centralized/orchestrator; MAS-Decentralized = peer debate+voting; MAS-Hybrid), 3 LLM
families (OpenAI/Google/Anthropic), 6 agentic benchmarks (260 configs). Finds a
"capability-saturation" effect (multi-agent gains shrink/reverse once SAS baseline exceeds
~45% accuracy), a tool-coordination trade-off, and architecture-dependent error amplification
(Independent 17.2x, Centralized 4.4x, Decentralized ~22.7% avg error REDUCTION via
challenge-response verification). A fitted regression (R^2=0.373-0.413) predicts best
architecture for 87% of held-out configs.
Task/benchmark: BrowseComp-Plus, Finance-Agent, PlanCraft, Workbench, SWE-bench Verified
(FULL patch generation, not localization-only — deterministic 20-instance seed-42 subset),
Terminal-Bench.
Method: SAS and MAS matched on total reasoning-token budget (mean 4,800 tokens/trial) and
tool access, identical prompts/tools held fixed across architectures. Decentralized/debate
runs 3 agents x 3 rounds x 3 iterations/round; Centralized uses 3 sub-agents + 1 orchestrator.
Ablation: Explicitly compute-matched by design — described as "a structured ablation over two
coordination dimensions: (i) orchestrator presence, (ii) peer communication," varying only
topology while budget/tools/prompts held constant. Coarser than A3062 (one shared budget per
cell, not per-stage accounting or recall/selection split), but the closest published precedent
to A3062's core method found in this review.
Cost reporting: Substantive — USD cost per experiment with cost-performance Pareto plots,
coordination overhead as % of SAS tokens (0% SAS up to 515% Hybrid), success-per-1000-tokens,
95% bootstrap CIs (10,000 resamples) per cell (n=20 for SWE-bench Verified yields CI widths
~+-20pp), cluster-robust SEs invalidating several nominally-significant predictors, only 3/19
predictors survive Holm-Bonferroni correction.
Relation to A3062: High relevance — closest existing precedent to A3062's core method,
generalized across domains. Its SWE-bench Verified result is directly germane to H2: under
matched budget, EVERY architecture including Decentralized/peer-debate underperforms SAS
(Hybrid -2.1%, Centralized -3.1%, Decentralized -5.4%, Independent -14.9%), attributed to
capability saturation once SAS exceeds ~45% — independent, general evidence that
compute-matching can flip/erase a debate benefit. Says nothing about H1/H3 (no dependency-
graph grounding tested at all — confirmed no mention of LocAgent/CoSIL); can't speak to H4
since its SWE-bench task is full patch generation, conflating localization and repair. Useful
as a limitation-of-precedent citation: even this careful study manages only n=20 SWE-bench
instances with wide CIs, which A3062's 75-instance multi-seed design directly improves on for
this benchmark family.
Report section: Related Work — compute-matched evaluation precedents (alongside Tran & Kiela,
Inside the Scaffold); Discussion when interpreting H2; Limitations/Threats-to-validity as a
statistical-power comparator at small instance counts.

## LLM-based Issue Resolution Survey — arXiv:2601.11655 (arXiv preprint, cs.SE, Jan 2026)
Claim: First comprehensive survey of LLM-based "issue resolution" (SWE-bench-style task),
synthesizing 175 papers into a Data/Methods/Analysis taxonomy and open challenges.
Task/benchmark: Not empirical — surveys the SWE-bench task formalism and ~40 evaluation
datasets (SWE-bench, Verified/Lite, Multi-SWE-bench, SWE-PolyBench, SWE-Bench Pro).
Method: Taxonomizes training-free frameworks (single-agent, multi-agent, workflow) and tool/
memory modules; explicitly separates graph-based FL/code search — NAMING SWE-Debate, CoSIL,
RepoGraph, KGCompass, GraphLocator, OrcaLoca — from SBFL and BM25/AST-based retrieval.
Ablation: N/A — survey.
Cost reporting: Explicitly names "Lack of efficiency-aware evaluation" as a top field-wide
challenge — current issue-resolution work "mainly focus[es] on effectiveness metrics such as
resolve rates while overlooking efficiency metrics like API costs and inference time" —
plus catalogs data-leakage/single-run reliability problems (SWE-bench Illusion, contamination
studies).
Relation to A3062: High relevance as a positioning citation. Independently corroborates
A3062's overarching complaint — resolve-rate-only evaluation of graph/multi-agent
issue-resolution systems, INCLUDING SWE-DEBATE DIRECTLY — and supplies the taxonomy
distinguishing static-analysis graphs from other retrieval strategies A3062 relies on. Runs no
ablation, says nothing about H1-H4 directly.
Report section: Related Work/Background (positions the project in the issue-resolution
literature); Introduction motivation (external validation of "field doesn't report cost/rigor").

## OneFlow (Single-Agent MAS Baseline) — arXiv:2601.12307 (arXiv preprint, cs.MA, Jan 2026)
Claim: Homogeneous MAS (all agents = same base LLM) can be simulated by a single LLM via
multi-turn conversation with KV-cache reuse, matching or slightly exceeding MAS accuracy at
substantially lower cost; automatically-discovered heterogeneous workflows offer little
further gain over the best homogeneous single-agent baseline.
Task/benchmark: HumanEval, MBPP, GSM8K, MATH, HotpotQA, DROP, Shopping-MMLU, TravelPlanner. No
SWE-bench, FL, or code-repair task.
Method: Formalizes MAS as a directed graph of agents; proof sketch that a single LLM
role-playing agents in one conversation induces the same transcript distribution as separate
instances under determinism/shared-randomness assumptions, at lower cost via KV-cache reuse.
Proposes OneFlow, an MCTS-based automatic workflow-design algorithm with dual Designer+Critic
meta-LLMs.
Ablation: Compares manual baselines vs automatically-designed workflows (AFlow, OneFlow) vs
single-LLM executions of the same workflows, across 3 backbones. NOT compute-matched via token
budget in A3062's sense — matches by construction (same workflow, single- vs multi-instance
execution), not by independently equalizing spend.
Cost reporting: Per-instance USD cost for every config; on open-weight Qwen3-8B, measures
latency/throughput/tokens directly via vLLM — one of the more cost-transparent papers
reviewed. Mean +- std over 3 trials, not full bootstrap CIs.
Relation to A3062: Strong methodological parallel to H2 and A3062's cost-reporting complaint,
but in general reasoning/coding-completion, not FL or SWE-bench debugging. No bearing on H1.
Compute-matching mechanism (KV-cache role replay) differs from A3062's approach (extended
reasoning/best-of-N). Converging evidence, not a fallback benchmark/method source.
Report section: Related Work — compute-matched evaluation/debate skepticism (alongside Tran &
Kiela); supporting citation for H2 motivation.

## Entropy Perspective on MAS — arXiv:2602.04234 (arXiv preprint, cs.MA, v6 Jun 2026)
Claim: SAS outperforms MAS in ~43.3% of cases across open-source LLMs; MAS effectiveness is
governed largely by entropy dynamics set in the FIRST interaction round (peak/erratic entropy
universally harmful, stable low entropy helps); additional rounds frequently fail to improve —
sometimes harm — performance once round-1 misalignment has set in.
Task/benchmark: GSM8K, MATH500, AIME2024/25, HumanEval, MMLU, GAIA, FinanceAgent, on
open-weight LLaMA-3.1-8B/3.2-3B and Qwen3 models (chosen for full-vocabulary logprob access).
Method: A 245-feature hierarchical entropy set over 5 topologies (single, sequential,
centralized, debate [3 competitive agents], hybrid); XGBoost+LightGBM "Entropy Judger"
predicts per-sample correctness from entropy traces; SHAP interpretation; causal discovery
(PC/FCI) + DoWhy effect estimation testing whether entropy-correctness correlations are
causal.
Ablation: Genuinely factorial: model (5) x dataset (6+2) x topology (5) x rounds (R=2 vs R=5
on two datasets), including a "Controlled SAS vs MAS" appendix decomposing MAS entropy shift
into role-assignment vs inter-agent-interaction components, plus a genuine-improvement-vs-
anchoring decomposition (only ~6% of samples show genuine improvement from interaction vs
~83% "possible anchoring"). NOT compute-matched in token-budget terms (SAS gets 1 call/round
vs debate's 3, sequential's 4 — cost is measured, not equalized). No bootstrap CIs, but formal
significance tests (Wilcoxon, Cohen's d) on large samples.
Cost reporting: Total tokens, per-round/per-agent token counts, call counts, wall-clock
latency as first-class features; plots accuracy vs token cost across topologies/round-counts —
one of the few papers treating cost as core data.
Relation to A3062: Highly relevant to H2/H3 in spirit — its finding that debate's value is
concentrated in and largely fixed by round 1, with extra rounds rarely helping, directly
predicts a pattern A3062's round-nested (1/2/3) debate conditions could reveal. Its anchoring-
vs-genuine-improvement decomposition is a useful diagnostic template for whether A3062's
multi-agent condition does real debate work or just converges early. Different domain (no
SWE-bench FL), no graph-grounding factor (H1 out of scope), doesn't address H4, not
compute-matched in A3062's token-budget sense.
Report section: Related Work — multi-agent debate skepticism (alongside Du et al., Huang et
al., Cemri et al.); Discussion (external comparison point when interpreting A3062's own
debate-round-count results, especially if benefit concentrates at round 1).

## FJ-MoE (MAS are Mixtures of Experts) — arXiv:2605.25929 (ICML 2026 workshop, Jun 2026)
Claim: Multi-agent LLM deliberation can be formally cast as a mixture-of-experts system, where
the Friedkin-Johnsen opinion-dynamics model describes belief updates and induced routing
weights are input-dependent (unlike a fixed ensemble). MAS outperforms SAS/static ensembles
specifically when routing tracks true competence; when routing tracks confidence instead (a
proxy often miscalibrated), the advantage can evaporate or invert.
Task/benchmark: MMLU-Pro, BBQ, CSQA — general MCQA, no code/SWE-bench.
Method: 5 LLM agents (GPT-5.4 Mini, Qwen2.5-14B/72B) communicate over 5 rounds in a complete
graph; FJ model fit to each deliberation trace; equilibrium belief shown to equal a convex
combination of initial beliefs with input-dependent weights (= MoE). Confidence (entropy-
derived) identified as the dominant predictor of who becomes the "influencer" — more so than
actual competence.
Ablation: Varies diversifying prompts and model scale across 3 seeds; compares MAS vs
max-belief baseline vs a task-independent fixed-FJ ensemble. A mechanism ablation on what
drives routing, not on debate rounds or graph grounding — round count held fixed at 5.
Cost reporting: Reports GPU/wall-clock compute per experiment combination, no token counts or
dollar costs. Accuracy tables report mean +- std/CI across 3 seeds; no CIs for the core
theorem-verification results.
Relation to A3062: No direct empirical overlap (no code, no SWE-bench, no graph grounding).
Relevance is theoretical/mechanistic: gives a formal account of WHY debate sometimes helps and
sometimes doesn't (confidence-based, not competence-based, routing) — useful for interpreting
H2 (if debate's apparent gains come from routing to confident-not-necessarily-correct agents
rather than genuine information aggregation, a compute-matched baseline could recover much of
the same benefit) and H4 (its "local specialization" argument — debate helps most when agents
are complementary on disjoint input sub-regions — parallels debate's surviving benefit
concentrating on high-candidate-density instances). Explicitly cites Tran & Kiela and Cemri et
al., confirming this is a live, contemporaneous conversation A3062 is part of.
Report section: Related Work — multi-agent debate origins/skepticism (theoretical companion to
Du et al., Cemri et al., Tran & Kiela); brief Discussion citation for H2/H4 "routing vs genuine
information gain" framing.

## BLUiR — DOI:10.1109/ASE.2013.6693093 (ASE 2013, Palo Alto)
Claim: Modeling source code's STRUCTURE — separating identifiers by program construct (class/
method/variable/comment) rather than flat text — substantially improves classical IR-based
bug localization, even without historical similar-bug data. NOT spectrum-based FL (SBFL,
Abreu et al. — an execution/instrumentation-based technique cited in BLUiR's own bibliography
as a different class of method) — this is structured/field-typed information retrieval.
Task/benchmark: Same 4-project, ~3,400-bug benchmark as BugLocator (SWT, Eclipse 3.1, AspectJ,
ZXing). Recall@{1,5,10}, MRR, MAP.
Method: Parses each file's AST (Eclipse JDT) into 4 typed fields, indexes with Indri (BM25-
derived TF-IDF + length normalization), camel-case + verbatim identifier tokenization,
separately queries bug-report summary/description fields, sums scores across 8
(query-field x doc-field) combinations. No dependency graph — field-typed flat retrieval.
Ablation: Thorough for its era: stemmer choice, TF-IDF hyperparameters (tuned on one project,
blind-tested on others), full-identifier vs tokenized-only, structured vs unstructured
retrieval, with/without bug-similarity data — vs BugLocator/BugScout. Single deterministic
runs (no seeds/CIs needed for a non-stochastic IR method — a fundamentally different situation
from the LLM case).
Cost reporting: Retrieval RUNTIME overhead, not compute/inference cost — structured retrieval
costs 3x-12x more than flat retrieval but stays under 6 seconds/query, judged negligible
against developer time saved. No token/model/dollar concepts apply.
Relation to A3062: Little direct empirical relevance to H1-H4 — no LLM, no agents, no debate,
no dependency graph (its "structure" is shallow syntactic field-typing, not call/import
graphs). Value is purely historical: establishes pre-LLM file-localization accuracy (Top-1
~32% AspectJ, ~24% Eclipse, ~55% SWT — a concrete numeric anchor for "baseline" difficulty)
and shows the field's trajectory flat-text IR -> structured/field-typed IR (this paper) ->
static dependency graphs (LocAgent/CoSIL) -> LLM-agent-graph hybrids (SWE-Debate) — a useful
one-sentence lineage for the background section.
Report section: Background/Related Work — SWE-bench and fault localization (historical
precedent, pre-LLM baseline accuracy, flat->structured->graph trajectory). Not applicable to
ablation/results/discussion.

## MAS Capability Saturation — DOI:10.1038/s42256-026-01268-y (Nature Machine Intelligence, Jul 2026)
Claim: Whether multi-agent coordination beats a single strong agent depends predictably on
measurable properties — chiefly SAS baseline performance (a capability-saturation proxy) —
rather than a universal "more agents is all you need" scaling law. Derives an empirical ~45%
SAS-baseline threshold above which adding agents is unlikely to help, and a regression using
coordination metrics (overhead, message density, redundancy, error amplification) selecting
the best architecture in 87% of held-out configs.
Task/benchmark: BrowseComp-Plus, Finance Agent, PlanCraft, WorkBench, SWE-bench Verified (FULL
issue resolution, not localization-only), Terminal-Bench. 260 configs, 3 LLM families.
Method: Controlled comparison of 5 architectures (SAS, Independent, Decentralized/peer-debate
+voting, Centralized/orchestrator, Hybrid), holding prompts/tools/per-system compute/token
budgets constant ("matched per-system compute ceilings") to isolate architecture from
implementation/compute confounds. Measures coordination overhead, message density, redundancy
(embedding cosine similarity), coordination efficiency, trace-level error amplification; fits
a regression with interaction terms.
Ablation: Precisely a controlled, compute-matched architecture ablation, structurally
analogous to A3062's approach — varies coordination structure (A3062's "debate" factor
analogue) while holding compute fixed, and separately varies model capability/family. No
retrieval/dependency-graph factor at all (no H1 analogue). Per-benchmark distributions with
cluster-robust corrections (dataset-level clustering, Holm-Bonferroni across 19 predictors) —
real attention to the "single run, no seeds/CIs" problem A3062 targets.
Cost reporting: Extensive and central — coordination overhead as % increase relative to SAS
(Independent +58%, Decentralized +263%, Centralized +285%, Hybrid +515%), success-per-1000-
tokens by architecture/family, absolute $ per experiment/per 1% accuracy gain. Close to a
template for A3062's own cost-per-correctly-localized-instance metric.
Relation to A3062: The single most methodologically relevant of all papers reviewed — a
bigger, more general confirmation of A3062's core complaint, done at larger scale, cross-
domain, with cluster-robust statistics. Its SWE-bench Verified results show ALL MAS
architectures degrading relative to SAS (-13% to -1%), attributed to already-high SAS
baselines (>45%) leaving little coordination headroom — directly relevant to H2 and offers a
candidate mechanism (capability saturation) for WHY shrinkage happens, testable against
A3062's own compute-matched debate factor. Its task-decomposability/"information gain"
moderator concept is conceptually close to H4. IMPORTANT CAVEAT: does NOT touch fault
localization, graph grounding, or SWE-Debate specifically, and its SWE-bench use is at
whole-issue-resolution level — cannot be cited as evidence about H1 at all. A3062 should be
positioned as a domain-specific, factorial (2x2, not single-factor architecture comparison),
localization-focused instance of the same broader methodological correction, not a
reproduction or subset of this paper.
Report section: Related Work — compute-matched evaluation critiques (directly alongside Tran &
Kiela, Inside the Scaffold); Discussion/Introduction citation motivating why a compute-matched
factorial redo of SWE-Debate specifically is a needed, timely contribution given this paper's
independent convergence on the same critique at the whole-task level.

## SW Testing LLM Survey — DOI:10.1109/TSE.2024.3368208 (IEEE TSE, Apr 2024)
Claim: Systematic literature review of 102 studies (2019-2023) applying LLMs to software
testing, organized by testing task and by how the LLM is used; argues the field concentrates
in mid/late-lifecycle tasks (test generation, debug, repair) with unresolved challenges around
coverage, the test-oracle problem, leakage-free evaluation, and real-world adoption.
Task/benchmark: Not a single benchmark — surveys unit test generation, oracle/assertion
generation, system test input generation, bug analysis, debugging/fault localization, and
program repair across the underlying papers' own datasets (Defects4J, QuixBugs, HumanEval,
CodeSearchNet, etc).
Method: SLR (14,623 candidates -> 102 papers via inclusion/exclusion + 8-item quality
assessment), coded along a testing-task taxonomy and an LLM-usage taxonomy.
Ablation: N/A — survey, no ablation of its own.
Cost reporting: Not systematically tracked — no compute/cost dimension in its taxonomy; one
passing anecdotal remark about industrial teams worrying about compute/energy cost, not
measured.
Relation to A3062: Low relevance. Explicitly confirms NONE of its 102 surveyed papers use
multi-agent debate (no "multi-agent" category in its taxonomy at all) and explicitly flags
"graph prompting" as unexplored future work (0 papers) — graph-grounded and multi-agent-debate
approaches are entirely outside its corpus. Doesn't discuss cost-aware or compute-matched
evaluation as a concern. Background landscape material only, not evidence for H1-H4. Flag for
student review as peripheral — likely redundant with the SE-agent surveys already in the
review.
Report section: At most a single background citation in the Introduction; uncertain relevance
beyond that given overlap with already-reviewed surveys — needs student/supervisor judgment on
whether it earns a citation at all.

## LLMAO — arXiv:2310.01726 (ICSE '24, Apr 2024)
Claim: Line-level fault localization learned WITHOUT any test execution, coverage, or program
analysis — fine-tunes a small bidirectional adapter on top of a frozen pretrained code LLM's
hidden states.
Task/benchmark: Statement/line-level FL (Top-1/3/5, AUC-ROC) on Defects4J v1.2.0 (395 Java
bugs) + a held-out 226-bug v2.0.0 extension, BugsInPy (493 Python bugs), Devign (5,260 C
security-vulnerability lines).
Method: Frozen pretrained CodeGen (350M/6B/16B) extracts per-line hidden states -> lightweight
2-layer bidirectional Transformer adapter trained with BCE to output per-line buggy-probability
— only the adapter trains, base LLM never fine-tuned, no test information used at all.
Ablation: Removing pretraining (train adapter from scratch) and removing bidirectionality
(linear projection only) both collapse performance (Top-5: 46.3%->7.6% and 21.5%
respectively); sweeps pretrain size (350M/6B/16B, monotonic gains); cross-benchmark/language
generalization check. Single-configuration per cell, no seeds/CIs.
Cost reporting: Minimal and inconsistent — only coarse training wall-clock (e.g. 16B model:
20min-2hr depending on benchmark, single GPU), no token-level/inference-cost accounting, no
cost comparison against the SBFL/MBFL/MLFL baselines it beats despite those requiring wholly
different (hours-long) artifact generation.
Relation to A3062: Not multi-agent, not graph-grounded, not SWE-bench-style — doesn't test
H1-H3, no debate-density axis for H4. Main relevance is illustrative: exactly the kind of FL
comparison the FYP's methodological complaint targets (baselines of very different
computational character compared on accuracy alone, no cost normalization, single-config
cells). Worth citing as a lightweight/test-free alternative-paradigm contrast to SWE-Debate's
heavyweight multi-agent+graph approach to the same problem.
Report section: Fault localization background (alongside LocAgent, Agentless, CoSIL, LLM4FL,
BugLocator, BLUiR) as a test-free/lightweight-learned-FL family member; secondary citation in
the methodological-complaint discussion.

## AutoFL — arXiv:2308.05487 (draft ACM format, Jul 2024)
Claim: A single LLM given only one failing test, equipped with repo-navigation function-
calling (not the whole codebase in context), autonomously retrieves code and produces both a
FL ranking and a natural-language root-cause explanation — matches/beats FL techniques needing
full test suites or coverage, with far less input and rationales those techniques lack. NOTE:
this is the ORIGINAL AutoFL system — the same "AutoFL" cited as a baseline in LLM4FL's entry
above (arXiv:2409.13642), not a duplicate of it; both entries can stand independently.
Task/benchmark: Method-level FL (acc@k) on 798 real bugs (353 Defects4J v1.0 Java + 445
BugsInPy Python), plus a 60-bug/300-explanation manually-rated subset and a 16-developer
interview study.
Method: Two-stage prompting of a single LLM (GPT-3.5-turbo vs GPT-4 compared) with 4
repo-navigation functions (get_class_covered, get_method_covered, get_code_snippet,
get_comments, <=10 calls): stage 1 gathers context + produces explanation, stage 2 names the
culprit method(s). R=5 repeated runs merged via a self-consistency-style scoring scheme.
Ablation: Not factorial component ablation — sweeps aggregated-run count R (1-5, diminishing
returns past R~5; a single GPT-4 run can beat 5 aggregated GPT-3.5 runs) and LLM choice
(GPT-3.5 vs GPT-4); isolates tool-use's contribution via a zero-function-call "Test-GPT3.5"
baseline.
Cost reporting: Notably more cost-conscious than most FL papers reviewed — per-bug wall-clock
by phase for both models on both benchmarks (e.g. 87.24s/bug GPT-3.5 vs 310.35s/bug GPT-4 on
Defects4J), explicitly benchmarked against SBFL's reported 112s/bug; mean function calls/bug
(5.37), call count scales with bug difficulty (ANOVA). Main acc@k comparisons still
single-configuration point estimates, no seeds/CIs — R=5 aggregation is an accuracy design
feature, not a variance report.
Relation to A3062: The most relevant of this trio to A3062's actual argument. Single-agent
tool-use FL (no debate, no graph grounding) that explicitly trades inference compute (more
runs vs a stronger single model) against accuracy and reports the wall-clock cost — in spirit
close to H2, though it never constructs a genuinely compute/token-matched comparison (R=5
GPT-3.5 never pitted against a token-budget-equivalent single GPT-4 call). Says nothing about
H1/H3 (no graph, no multi-agent coordination).
Report section: Cost-aware evaluation section, as an earlier and more granular example
alongside SWE-Effi of treating inference compute/time as first-class; secondary citation in
the FL background section as a single-agent tool-use baseline contrasting with SWE-Debate's
multi-agent graph-grounded design for the same problem.

## Agent4SE Survey — DOI:10.1145/3796507 (ACM TOSEM, Just Accepted 2026)
Claim: First comprehensive survey of 124 papers on LLM-based AGENTS (distinct from standalone
LLMs) for SE, taxonomized by SE-lifecycle stage and by agent-architecture (planning/memory/
perception/action; multi-agent roles/topology/information-flow; human-agent collaboration).
Task/benchmark: Not a benchmark paper — catalogs benchmarks used by the 124 surveyed systems,
including the full SWE-bench family (SWE-bench/Lite/Lite-S/Verified/java-verified) for
maintenance/FL agents and Defects4J for repair.
Method: DBLP search (57 query combos, 10,362 hits) + snowballing + direct author feedback
(321 contacted) -> 124 final papers, dual-screened against explicit criteria.
Ablation: N/A (survey), but reports design choices from surveyed systems directly germane to
A3062: Section 4.5.1/Table 9 distinguishes multi-agent FL systems (AgentFL: 4 agents — test-
code reviewer, source-code reviewer, software architect, test engineer) from tool-augmented
single-agent systems (AutoFL); MAGIS derives its multi-agent team size directly from the
average number of suspicious files per SWE-bench issue (1.7) — concrete precedent for H4;
cites a prior finding that comprehensive-benchmark performance "will reach saturation
regardless of collaboration structure" (echoes MAS Capability Saturation, already in review);
catalogs 4 localization strategies (retrieval/navigation/spectrum/simulation-MCTS-based)
mapping onto A3062's "graph grounding" factor.
Cost reporting: DIRECTLY SUBSTANTIATES A3062's complaint at field scale: Section 6 states
"only 46.7% of the papers we surveyed have explicitly considered the efficiency of agents in
SE, reporting quantitative analyses of time, token consumption, monetary cost, and feedback
loops" — over half of 124 agentic SE papers report NO cost/efficiency data at all. Also notes
full SWE-bench eval is prohibitively costly (motivating Lite/Verified) and repeats OpenAI's
finding that 77.8% of SWE-bench tasks are solvable by an engineer within an hour, questioning
whether the benchmark's difficulty justifies heavy multi-agent spend.
Relation to A3062: High relevance as corroborating field-level evidence (not a comparator
system — Sept-2024 cutoff predates SWE-Debate/LocAgent/CoSIL entirely, none appear). The
<47%-report-cost statistic is exactly the independent, large-sample evidence that strengthens
"SWE-Debate's uncosted ablation is symptomatic of the field, not an isolated lapse." Its call
for "fine-grained metrics... rather than relying solely on final success rates" directly
anticipates A3062's recall/selection-precision split, which the survey notes no existing agent
evaluation performs. MAGIS's agent-count-from-candidate-density design is citable as prior,
informal support for H4. Use as a meta-level/framing citation, not a technical predecessor of
SWE-Debate's architecture.
Report section: Related Work/Motivation — anchors "this is a field-wide problem" (cite the
46.7% statistic and the fine-grained-metrics gap); MAGIS detail supports H4 discussion.

## LLM4SE SLR — DOI:10.1145/3695988 (ACM TOSEM 33(8), Dec 2024)
Claim: Kitchenham-style SLR of 395 primary studies (Jan 2017-Jan 2024) on LLMs (NOT
specifically agents) for SE — architectures used, dataset collection/pre-processing, tuning/
evaluation techniques, and 85 SE tasks across 6 SDLC phases.
Task/benchmark: Not a benchmark/system paper. Task distribution: software development 56.65%
(codegen/completion/summarization dominant), maintenance 22.71% (program repair largest at 35
studies), QA 15.14% (bug localization only 5 studies, fault localization only 3 — treated
narrowly as fault-inducing-test classification or bug-report-to-code matching, NOT
repository-level issue localization).
Method: Kitchenham SLR — quasi-gold-standard manual search of 6 top SE venues to derive a
search string, automated search across 7 databases (218,765 initial hits), 6-stage filtering +
10-criterion quality assessment (382 retained) + snowballing -> 395 studies.
Ablation: N/A — purely descriptive, no experiments.
Cost reporting: Only glancing engagement — notes LLM pretraining is computationally expensive
as background framing; lists "effort/cost prediction" as a minor task (2/395 studies). No
discussion of inference-time token cost, multi-agent overhead, or compute-matched evaluation
anywhere, consistent with its scope essentially excluding agentic multi-agent systems.
Relation to A3062: UNCERTAIN/LOW RELEVANCE — flag for student review. Corpus cutoff (Jan 2024)
predates essentially the entire multi-agent-debate-for-FL literature A3062 builds on (all
2025). "Agent" appears ~10 times in 79 pages, almost entirely inside reference titles
(MetaGPT, ChatDev, CodeAgent), not as a discussed category — no multi-agent-systems section,
no debate, no collaboration topology, no graph-grounded retrieval discussed anywhere. Its
fault/bug-localization categories are narrow, non-agentic, classification-style tasks (3 and 5
studies respectively) — a materially different problem framing from SWE-bench-style
repository-level localization. No content found bearing on H1-H4 or the compute-matching/
cost-reporting complaint specifically. Only plausible use: one more generic "LLMs applied
broadly across the SDLC" citation, already amply covered by the SE-agent surveys already in
the review.
Report section: Uncertain relevance, needs student/supervisor review — does not clearly anchor
any specific section; at most a passing introductory citation, redundant with surveys already
cited.

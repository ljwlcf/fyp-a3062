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

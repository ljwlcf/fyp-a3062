# smoke_localization_v1 runs (2026-10-01, gpu21)

| run | outcome | cause / fix |
|---|---|---|
| `20261001-131228` | crashed before any call | YAML date not JSON-serialisable in the manifest; runner fixed (`default=str`) |
| `20261001-131450` | error after stage 1 | pointed at RQ1's code-stripped graphs (`KeyError: 'start_line'`); config now uses `data/graphs_full` |
| `20261001-132745` | error at graph build | gpu21 has no system `git`; installed via conda |
| `20261001-133650` | **ok**, all 8 stages | the run reported in notes/results.md |
| `20261001-092851` | **ok**, all 8 stages | EEE cluster job 179270 (a6000, vLLM 0.30.0), after two job-script fixes (nvcc module; libstdc++ clash). Debate collapsed: 4/5 round-1 answers failed JSON parsing |

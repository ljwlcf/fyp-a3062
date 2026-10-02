# Running on the EEE GPU Cluster

Login node (no GPU) -> Slurm -> compute node. Installs and runs happen inside jobs, never on
the login node. Project folder: `/projects/fypA3062` (SSD, 150 GB); caches are redirected
there by `~/.bashrc`. Logs: `/projects/fypA3062/logs/`. Cluster rules: NTUEEECluster/docs,
`skill.md`.

1. Copy the code (on the Mac):
   `rsync -az --exclude papers --exclude 'data/repos*' --exclude data/graphs --exclude '__pycache__' ~/IM4080/FYP-A3062/ eee:~/FYP-A3062/`
2. One-time setup, a free CPU job (environments + model downloads):
   `sbatch ~/FYP-A3062/ablation/eee/setup_envs.sh`, then read `logs/setup-envs-<id>.out`.
3. Pre-build the full graphs the config needs (CPU job, free; otherwise the GPU job idles
   for minutes per instance while the pipeline clones and builds):
   `sbatch ~/FYP-A3062/ablation/eee/build_graphs_job.sh ablation/configs/<config>.yaml`
4. A run (GPU job; server and pipeline inside it). GPU rules (decisions.md 2026-10-02):
   decide the GPUs once per comparison with `G=$(ablation/eee/pick_gpu.sh <model> <GB> [n])`
   (32B/72B always 2x pro6000; 7B 2x pro6000 unless a fallback pair finishes clearly sooner),
   then `sbatch $G ...` for every arm, with `--export=ALL,PARALLEL=dp` for a 7B (two replicas).
   `sbatch ~/FYP-A3062/ablation/eee/run_localization_job.sh [config] [model]`
   Defaults: the smoke config and the 7B model on one a6000. Watch with `squeue --me`; read
   `logs/loc-<id>.out` (job) and `logs/vllm-<id>.log` (server).
   Longer runs need a longer limit: `sbatch --time=02:00:00 ...run_localization_job.sh ...`.
   Several instances run in parallel (`run.workers` in the config) against the one server.
5. Score: `python ablation/harness/score_localization.py ablation/results/<config>/<run id>`
   (writes `scores.jsonl` and `summary.json` next to the raw output; runs anywhere).
6. Results land in `~/FYP-A3062/ablation/results/<config name>/<run id>/`. Bring them home:
   `rsync -az --ignore-existing --exclude work eee:~/FYP-A3062/ablation/results/ ~/IM4080/FYP-A3062/ablation/results/`
   (`--ignore-existing`: results only flow home and never overwrite local files, e.g. scores)

Differences from MLDA (ablation/gpu21/README.md): no tmux (batch jobs survive logout); the
port is per job; vLLM 0.30.0 instead of 0.9.2 (driver supports CUDA 13); a GPU is billed in SU
only while a job runs; `HF_HUB_OFFLINE=1` in runs, so download models in setup first; the
run job loads `CUDA/13.0.0` + `GCC/13.3.0` because vLLM 0.30's FlashInfer sampler compiles a
kernel with nvcc on first use (compute nodes have no system CUDA).

Job scripts start with `#!/bin/bash -l` (login shell): `module` is a shell function set up at
login, so a job submitted from a non-interactive `ssh eee 'sbatch ...'` otherwise fails at once
with `module: command not found` (job 180174).

Long runs: if a job hits its time limit or dies, resubmit with `--resume <run_dir>` as an extra
argument (after config and model); it skips instances already in that run's raw.jsonl and
appends to the same run. Pass the same flags as the original (e.g. `--lenient-json`,
`--shuffle-seed N`), or it refuses (decisions.md 2026-10-02, main-experiment job structure).

Vote logprobs (candidate adaptive-debate trigger): add `--vote-logprobs 10` after config and model.
Off by default; it does not change outputs (decisions.md 2026-10-02).


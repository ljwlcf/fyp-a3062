# Running on the EEE GPU Cluster

Login node (no GPU) -> Slurm -> compute node. Installs and runs happen inside jobs, never on
the login node. Project folder: `/projects/fypA3062` (SSD, 150 GB); caches are redirected
there by `~/.bashrc`. Logs: `/projects/fypA3062/logs/`. Cluster rules: NTUEEECluster/docs,
`skill.md`.

1. Copy the code (on the Mac):
   `rsync -az --exclude papers --exclude 'data/repos*' --exclude data/graphs --exclude '__pycache__' ~/IM4080/FYP-A3062/ eee:~/FYP-A3062/`
2. One-time setup, a free CPU job (environments + model downloads):
   `sbatch ~/FYP-A3062/ablation/eee/setup_envs.sh`, then read `logs/setup-envs-<id>.out`.
3. A run (GPU job; server and pipeline inside it):
   `sbatch ~/FYP-A3062/ablation/eee/run_localization_job.sh [config] [model]`
   Defaults: the smoke config and the 7B model on one a6000. Watch with `squeue --me`; read
   `logs/loc-<id>.out` (job) and `logs/vllm-<id>.log` (server).
4. Results land in `~/FYP-A3062/ablation/results/<config name>/<run id>/`. Bring them home:
   `rsync -az --exclude work eee:~/FYP-A3062/ablation/results/ ~/IM4080/FYP-A3062/ablation/results/`

Differences from MLDA (ablation/gpu21/README.md): no tmux (batch jobs survive logout); the
port is per job; vLLM 0.30.0 instead of 0.9.2 (driver supports CUDA 13); a GPU is billed in SU
only while a job runs; `HF_HUB_OFFLINE=1` in runs, so download models in setup first.

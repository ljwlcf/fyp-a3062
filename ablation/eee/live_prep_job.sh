#!/bin/bash -l
# Prepare SWE-bench-Live on the cluster (CPU job, free): build the pinned dataset files, then the
# full code maps for a config's instances (e.g. the 40-instance pilot).
#   sbatch ablation/eee/live_prep_job.sh ablation/configs/live_pilot40_lenient_v1.yaml
#SBATCH --job-name=live-prep
#SBATCH --cpus-per-task=4
#SBATCH --time=08:00:00
#SBATCH --output=/projects/fypA3062/logs/%x-%j.out

set -eo pipefail
P=/projects/fypA3062
export TMPDIR=$P/.tmp/$SLURM_JOB_ID XDG_CACHE_HOME=$P/.tmp/cache CONDA_ENVS_PATH=$P/envs
mkdir -p "$TMPDIR"; trap 'rm -rf "$TMPDIR"' EXIT
module load Miniforge3
eval "$(conda shell.bash hook)"
conda activate swed
cd "$HOME/FYP-A3062"
python ablation/harness/swebench_live.py --split verified \
    --revision b51a86422e10cfd403beb4773e5a2947953e36ec --created-after 2024-09-19
python ablation/harness/build_full_graphs.py "${1:?usage: live_prep_job.sh <config>}"
du -sh data/repos data/graphs_live 2>/dev/null

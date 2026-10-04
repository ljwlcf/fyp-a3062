#!/bin/bash -l
# Pre-build full dependency graphs for a config on CPU (free), so GPU jobs never wait on them.
#   sbatch ~/FYP-A3062/ablation/eee/build_graphs_job.sh ablation/configs/<config>.yaml
#SBATCH --job-name=graphs
#SBATCH --cpus-per-task=16         # 3 GB RAM per CPU: 48 GB (huge repos, e.g. azure-sdk-for-python)
#SBATCH --time=03:00:00
#SBATCH --output=/projects/fypA3062/logs/%x-%j.out

set -eo pipefail
P=/projects/fypA3062
export TMPDIR=$P/.tmp/$SLURM_JOB_ID XDG_CACHE_HOME=$P/.tmp/cache CONDA_ENVS_PATH=$P/envs
export GRAPH_MEM_GB=40                 # per-graph cap (build_full_graphs.py), below the job's 48 GB
mkdir -p "$TMPDIR"; trap 'rm -rf "$TMPDIR"' EXIT
module load Miniforge3
eval "$(conda shell.bash hook)"
conda activate swed
cd "$HOME/FYP-A3062"
python ablation/harness/build_full_graphs.py "${1:?usage: build_graphs_job.sh <config>}"

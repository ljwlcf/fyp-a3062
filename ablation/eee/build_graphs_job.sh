#!/bin/bash
# Pre-build full dependency graphs for a config on CPU (free), so GPU jobs never wait on them.
#   sbatch ~/FYP-A3062/ablation/eee/build_graphs_job.sh ablation/configs/<config>.yaml
#SBATCH --job-name=graphs
#SBATCH --cpus-per-task=4
#SBATCH --time=03:00:00
#SBATCH --output=/projects/fypA3062/logs/%x-%j.out

set -eo pipefail
P=/projects/fypA3062
export TMPDIR=$P/.tmp/$SLURM_JOB_ID XDG_CACHE_HOME=$P/.tmp/cache CONDA_ENVS_PATH=$P/envs
mkdir -p "$TMPDIR"; trap 'rm -rf "$TMPDIR"' EXIT
module load Miniforge3
eval "$(conda shell.bash hook)"
conda activate swed
cd "$HOME/FYP-A3062"
python ablation/harness/build_full_graphs.py "${1:?usage: build_graphs_job.sh <config>}"

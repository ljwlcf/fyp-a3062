#!/bin/bash -l
# Download pinned model checkpoints into explicit folders (CPU job, free; run jobs are offline).
#   sbatch ablation/eee/download_models.sh <repo> <commit-sha> <dest-dir> [<repo> <sha> <dest> ...]
# Each model lands in <dest-dir> with a PINNED.txt recording repo and commit. Serve it with
#   run_localization_job.sh <config> <dest-dir>  and  SERVED_NAME=<repo>.
# Where (decisions.md 2026-10-02): SSD /projects/fypA3062/models for models that fit, the HDD
# folder for the ~145 GB 72B (the 150 GB SSD cannot hold it).
#SBATCH --job-name=download
#SBATCH --cpus-per-task=4
#SBATCH --time=06:00:00
#SBATCH --output=/projects/fypA3062/logs/%x-%j.out

set -eo pipefail
P=/projects/fypA3062
export TMPDIR=$P/.tmp/$SLURM_JOB_ID HF_HOME=$P/.tmp/hf XDG_CACHE_HOME=$P/.tmp/cache CONDA_ENVS_PATH=$P/envs
export HF_HUB_ENABLE_HF_TRANSFER=0
mkdir -p "$TMPDIR"; trap 'rm -rf "$TMPDIR"' EXIT
module load Miniforge3
eval "$(conda shell.bash hook)"
conda activate vllm

[ $(( $# % 3 )) -eq 0 ] && [ $# -gt 0 ] || { echo "usage: <repo> <sha> <dest> [...]"; exit 1; }
while [ $# -gt 0 ]; do
    repo=$1 sha=$2 dest=$3; shift 3
    echo "== $repo @ $sha -> $dest  ($(date))"
    mkdir -p "$dest"
    hf download "$repo" --revision "$sha" --local-dir "$dest" \
        --include "*.safetensors" "*.json" "*.txt" "*.model" "*.tiktoken" "LICENSE*" >/dev/null
    printf "repo: %s\ncommit: %s\ndownloaded: %s\n" "$repo" "$sha" "$(date -u +%FT%TZ)" > "$dest/PINNED.txt"
    du -sh "$dest"
done
echo "== done $(date)"

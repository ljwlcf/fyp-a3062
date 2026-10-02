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
    # One --include per pattern: after a single --include, further words are taken as file
    # NAMES, which silently skipped every weight file in job 180295.
    hf download "$repo" --revision "$sha" --local-dir "$dest" \
        --include "*.safetensors" --include "*.json" --include "*.txt" \
        --include "*.model" --include "*.tiktoken" --include "LICENSE*" > /dev/null
    # Only mark it pinned if every shard named in the index is present and non-empty.
    python - "$dest" <<'PY'
import json, os, sys
d = sys.argv[1]
idx = os.path.join(d, "model.safetensors.index.json")
shards = (sorted(set(json.load(open(idx))["weight_map"].values())) if os.path.exists(idx)
          else [f for f in os.listdir(d) if f.endswith(".safetensors")])
missing = [f for f in shards if not os.path.exists(os.path.join(d, f))
           or os.path.getsize(os.path.join(d, f)) == 0]
if not shards or missing:
    sys.exit(f"INCOMPLETE: {len(missing)} of {len(shards)} weight files missing, e.g. {missing[:3]}")
print(f"verified {len(shards)} weight files")
PY
    printf "repo: %s\ncommit: %s\ndownloaded: %s\n" "$repo" "$sha" "$(date -u +%FT%TZ)" > "$dest/PINNED.txt"
    du -sh "$dest"
done
echo "== done $(date)"

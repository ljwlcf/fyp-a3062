#!/bin/bash -l
# Localization run on the EEE GPU Cluster: vLLM server + pipeline inside ONE job.
# The server binds to 127.0.0.1 on a per-job port, serves only this job, and is killed
# when the job ends, however it ends.
#   sbatch ~/FYP-A3062/ablation/eee/run_localization_job.sh [config] [model]
#SBATCH --job-name=loc
#SBATCH --gres=gpu:a6000:1
#SBATCH --time=01:00:00
#SBATCH --output=/projects/fypA3062/logs/%x-%j.out

set -eo pipefail

P=/projects/fypA3062
REPO=$HOME/FYP-A3062
CONFIG=${1:-ablation/configs/smoke_localization_v1.yaml}
MODEL=${2:-Qwen/Qwen2.5-Coder-7B-Instruct}     # HF id, or a local weights dir (then set SERVED_NAME)
# Optional, via `sbatch --export=ALL,VAR=value,...`:
#   SERVED_NAME  name the server reports; must equal llm.model in the config (default: MODEL)
#   MAX_LEN      context length (default 32768). 65536 for real runs (decisions 2026-10-02).
#   ROPE_YARN    YaRN factor for models whose native context is shorter than MAX_LEN, e.g. 2
#   GPU_UTIL     vLLM --gpu-memory-utilization (default 0.90)
#   SEED         vLLM --seed (default 0). Distinguishes repeated passes; with concurrent requests
#                vLLM is not bit-reproducible, so a seed gives an independent sample, not a replay
#   PARALLEL     tp (default): one model split over all GPUs (tensor parallel; 32B/72B);
#                dp: one full replica per GPU (data parallel; small models), GPU rule 4
SERVED_NAME=${SERVED_NAME:-$MODEL}
MAX_LEN=${MAX_LEN:-32768}
GPU_UTIL=${GPU_UTIL:-0.90}
PARALLEL=${PARALLEL:-tp}
SEED=${SEED:-0}
export MODEL SERVED_NAME MAX_LEN ROPE_YARN GPU_UTIL PARALLEL SEED   # recorded in the run manifest
VLLM_EXTRA=()
yarn_overrides() {  # print vLLM --hf-overrides JSON enabling YaRN x$1 for model dir/id $2
    # vLLM 0.30 + transformers 5 read `rope_parameters` (formerly rope_scaling, now carrying
    # rope_theta too) and, for YaRN, expect max_position_embeddings ALREADY scaled; passing
    # only rope_scaling left the limit at 32k (job 180310). Values come from the model's own
    # config.json, so each model keeps its native length and rope_theta.
    python - "$1" "$2" <<'PY'
import json, os, sys
factor, model = float(sys.argv[1]), sys.argv[2]
path = os.path.join(model, "config.json")
if not os.path.exists(path):  # an HF id: read the cached copy
    from huggingface_hub import hf_hub_download
    path = hf_hub_download(model, "config.json")
c = json.load(open(path))
native = int(c["max_position_embeddings"])
theta = c.get("rope_theta") or (c.get("rope_parameters") or {}).get("rope_theta")
print(json.dumps({"max_position_embeddings": int(native * factor),
                  "rope_parameters": {"rope_type": "yarn", "factor": factor,
                                      "original_max_position_embeddings": native,
                                      "rope_theta": theta}}))
PY
}
shift $(( $# < 2 ? $# : 2 )); EXTRA=("$@")     # anything else goes to the runner, e.g. --workers 2
PORT=$((20000 + SLURM_JOB_ID % 10000))         # other users' jobs share the node
URL=http://127.0.0.1:$PORT/v1
VLLM_LOG=$P/logs/vllm-$SLURM_JOB_ID.log

export TMPDIR=$P/.tmp/$SLURM_JOB_ID
export PIP_CACHE_DIR=$P/.tmp/pip CONDA_PKGS_DIRS=$P/.tmp/conda
export HF_HOME=$P/.tmp/hf TRITON_CACHE_DIR=$P/.tmp/triton XDG_CACHE_HOME=$P/.tmp/cache
export CONDA_ENVS_PATH=$P/envs
export HF_HUB_OFFLINE=1                        # models were downloaded by setup_envs.sh
mkdir -p "$TMPDIR"

module load Miniforge3
export FLASHINFER_WORKSPACE_BASE=$P/.tmp     # FlashInfer's compiled-kernel cache, on the SSD
eval "$(conda shell.bash hook)"
# Use every GPU the job was given (pick_gpu.sh chooses them): split one model across them
# (tensor parallel) or run one replica per GPU (data parallel), per PARALLEL.
NGPU=$(echo "$CUDA_VISIBLE_DEVICES" | tr ',' '\n' | grep -c .)
case "$PARALLEL" in
    tp) PAR_ARGS=(--tensor-parallel-size "$NGPU") ;;
    dp) PAR_ARGS=(--data-parallel-size "$NGPU" --tensor-parallel-size 1) ;;
    *)  echo "PARALLEL must be tp or dp"; exit 1 ;;
esac
echo "== job $SLURM_JOB_ID on $(hostname), GPU(s) $CUDA_VISIBLE_DEVICES ($PARALLEL x $NGPU), $(date)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sort | uniq -c

# 1. Start the model server in the background.
# vLLM 0.30 samples with FlashInfer, which JIT-compiles a kernel on first use and needs nvcc
# (job 179268: "Could not find nvcc"). CUDA 13.0 matches torch 2.13+cu130; nvcc hands host
# code to g++, hence GCC. But the GCC module puts its older libstdc++ first on the library
# path, and the conda env's libs need the newer one (job 179269: CXXABI_1.3.15 not found).
# So: the modules, with conda's lib dir in front, apply to the server process only, and are
# unloaded again before the pipeline runs.
conda activate vllm
if [ -n "$ROPE_YARN" ]; then
    YARN_JSON=$(yarn_overrides "$ROPE_YARN" "$MODEL")
    VLLM_EXTRA+=(--hf-overrides "$YARN_JSON")
    echo "yarn overrides: $YARN_JSON"
fi
module load CUDA/13.0.0 GCC/13.3.0
export CUDA_HOME=${CUDA_HOME:-$EBROOTCUDA}
echo "nvcc $(command -v nvcc), CUDA_HOME=$CUDA_HOME"
echo "serving $MODEL as $SERVED_NAME, context $MAX_LEN, yarn ${ROPE_YARN:-none}, gpu util $GPU_UTIL, seed $SEED"
LD_LIBRARY_PATH="$CONDA_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    vllm serve "$MODEL" --served-model-name "$SERVED_NAME" --host 127.0.0.1 --port "$PORT" \
    --dtype bfloat16 "${PAR_ARGS[@]}" --max-model-len "$MAX_LEN" \
    --gpu-memory-utilization "$GPU_UTIL" --seed "$SEED" "${VLLM_EXTRA[@]}" > "$VLLM_LOG" 2>&1 &
VLLM_PID=$!
module unload GCC/13.3.0 CUDA/13.0.0
mem_peak() {  # whole job's peak RAM from its cgroup (v2, else v1), best effort
    local cg; cg=$(awk -F: '$1=="0"{print $3}' /proc/self/cgroup)
    for f in /sys/fs/cgroup$cg/memory.peak /sys/fs/cgroup/memory$cg/memory.max_usage_in_bytes; do
        [ -r "$f" ] && { awk '{printf "%.1f GB", $1/2^30}' "$f"; return; }; done; echo unknown; }
trap 'kill $VLLM_PID 2>/dev/null; wait $VLLM_PID 2>/dev/null; rm -rf "$TMPDIR"; echo "== server stopped $(date), job RAM peak $(mem_peak) of ${SLURM_MEM_PER_NODE:-?} MB"' EXIT
echo "vllm $(python -c 'import vllm; print(vllm.__version__)'), pid $VLLM_PID, log $VLLM_LOG"
conda deactivate

# 2. Wait for it to answer (up to 45 min: weights read from the HDD tier are slow), and stop
#    early if it crashed.
for _ in $(seq 540); do
    curl -sf "$URL/models" >/dev/null && break
    kill -0 $VLLM_PID 2>/dev/null || { echo "vLLM exited during startup:"; tail -30 "$VLLM_LOG"; exit 1; }
    sleep 5
done
curl -sf "$URL/models" >/dev/null || { echo "vLLM not up after 45 min"; tail -30 "$VLLM_LOG"; exit 1; }
echo "== server up $(date)"

# 3. Run the pipeline against it.
conda activate swed
cd "$REPO"
python ablation/harness/run_localization.py "$CONFIG" --base-url "$URL" "${EXTRA[@]}"
echo "== pipeline finished $(date)"

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
MODEL=${2:-Qwen/Qwen2.5-Coder-7B-Instruct}     # must match llm.model in the config
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
# Split the model over every GPU the job was given (pick_gpu.sh chooses the count).
NGPU=$(echo "$CUDA_VISIBLE_DEVICES" | tr ',' '\n' | grep -c .)
echo "== job $SLURM_JOB_ID on $(hostname), GPU(s) $CUDA_VISIBLE_DEVICES (tensor parallel $NGPU), $(date)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sort | uniq -c

# 1. Start the model server in the background.
# vLLM 0.30 samples with FlashInfer, which JIT-compiles a kernel on first use and needs nvcc
# (job 179268: "Could not find nvcc"). CUDA 13.0 matches torch 2.13+cu130; nvcc hands host
# code to g++, hence GCC. But the GCC module puts its older libstdc++ first on the library
# path, and the conda env's libs need the newer one (job 179269: CXXABI_1.3.15 not found).
# So: the modules, with conda's lib dir in front, apply to the server process only, and are
# unloaded again before the pipeline runs.
conda activate vllm
module load CUDA/13.0.0 GCC/13.3.0
export CUDA_HOME=${CUDA_HOME:-$EBROOTCUDA}
echo "nvcc $(command -v nvcc), CUDA_HOME=$CUDA_HOME"
LD_LIBRARY_PATH="$CONDA_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    vllm serve "$MODEL" --host 127.0.0.1 --port "$PORT" --dtype bfloat16 \
    --tensor-parallel-size "$NGPU" \
    --max-model-len 32768 --gpu-memory-utilization 0.90 --seed 0 > "$VLLM_LOG" 2>&1 &
VLLM_PID=$!
module unload GCC/13.3.0 CUDA/13.0.0
mem_peak() {  # whole job's peak RAM from its cgroup (v2, else v1), best effort
    local cg; cg=$(awk -F: '$1=="0"{print $3}' /proc/self/cgroup)
    for f in /sys/fs/cgroup$cg/memory.peak /sys/fs/cgroup/memory$cg/memory.max_usage_in_bytes; do
        [ -r "$f" ] && { awk '{printf "%.1f GB", $1/2^30}' "$f"; return; }; done; echo unknown; }
trap 'kill $VLLM_PID 2>/dev/null; wait $VLLM_PID 2>/dev/null; rm -rf "$TMPDIR"; echo "== server stopped $(date), job RAM peak $(mem_peak) of ${SLURM_MEM_PER_NODE:-?} MB"' EXIT
echo "vllm $(python -c 'import vllm; print(vllm.__version__)'), pid $VLLM_PID, log $VLLM_LOG"
conda deactivate

# 2. Wait for it to answer (up to 15 min), and stop early if it crashed.
for _ in $(seq 180); do
    curl -sf "$URL/models" >/dev/null && break
    kill -0 $VLLM_PID 2>/dev/null || { echo "vLLM exited during startup:"; tail -30 "$VLLM_LOG"; exit 1; }
    sleep 5
done
curl -sf "$URL/models" >/dev/null || { echo "vLLM not up after 15 min"; tail -30 "$VLLM_LOG"; exit 1; }
echo "== server up $(date)"

# 3. Run the pipeline against it.
conda activate swed
cd "$REPO"
python ablation/harness/run_localization.py "$CONFIG" --base-url "$URL" "${EXTRA[@]}"
echo "== pipeline finished $(date)"

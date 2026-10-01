#!/bin/bash
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
eval "$(conda shell.bash hook)"
echo "== job $SLURM_JOB_ID on $(hostname), GPU $CUDA_VISIBLE_DEVICES, $(date)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# 1. Start the model server in the background.
conda activate vllm
vllm serve "$MODEL" --host 127.0.0.1 --port "$PORT" --dtype bfloat16 \
    --max-model-len 32768 --gpu-memory-utilization 0.90 --seed 0 > "$VLLM_LOG" 2>&1 &
VLLM_PID=$!
trap 'kill $VLLM_PID 2>/dev/null; wait $VLLM_PID 2>/dev/null; rm -rf "$TMPDIR"; echo "== server stopped $(date)"' EXIT
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
python ablation/harness/run_localization.py "$CONFIG" --base-url "$URL"
echo "== pipeline finished $(date)"

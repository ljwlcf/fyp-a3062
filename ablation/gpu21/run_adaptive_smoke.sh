#!/bin/bash
# One-shot mechanics test of the adaptive arm (with --reuse-chains) on gpu21 (start in tmux; frees the GPU at the end).
#   tmux new -d -s adaptive "bash ~/FYP-A3062/ablation/gpu21/run_adaptive_smoke.sh <GPU>"
set -u
GPU=${1:?usage: run_adaptive_smoke.sh <free GPU index>}
cd ~/FYP-A3062
source ~/miniforge3/etc/profile.d/conda.sh
LOG=ablation/gpu21/adaptive_smoke.log; : > $LOG
conda activate vllm
CUDA_VISIBLE_DEVICES=$GPU vllm serve Qwen/Qwen2.5-Coder-7B-Instruct --host 127.0.0.1 --port 8765 \
    --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.90 --seed 0 >> $LOG.server 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null; wait $SERVER 2>/dev/null; echo "== server stopped $(date)" >> $LOG' EXIT
for i in $(seq 1 120); do curl -s http://127.0.0.1:8765/v1/models > /dev/null && break; sleep 10; done
echo "== server up $(date)" >> $LOG
conda activate swed
python ablation/harness/run_localization.py ablation/configs/smoke_adaptive_v1.yaml \
    --reuse-chains ablation/results/baseline_72b_lenient_v1/20261005-082019 >> $LOG 2>&1
echo "== pipeline finished $(date), exit $?" >> $LOG

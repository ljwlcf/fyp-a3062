#!/bin/bash
# One-time setup on the EEE GPU Cluster: both conda environments + model downloads.
# CPU-only job (free): the cluster forbids installs on login nodes.
#   sbatch ~/FYP-A3062/ablation/eee/setup_envs.sh
#SBATCH --job-name=setup-envs
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=/projects/fypA3062/logs/%x-%j.out

set -eo pipefail          # stop at the first failing command (no -u: conda's scripts trip it)

P=/projects/fypA3062
REPO=$HOME/FYP-A3062
export TMPDIR=$P/.tmp/$SLURM_JOB_ID
export PIP_CACHE_DIR=$P/.tmp/pip CONDA_PKGS_DIRS=$P/.tmp/conda
export HF_HOME=$P/.tmp/hf TRITON_CACHE_DIR=$P/.tmp/triton XDG_CACHE_HOME=$P/.tmp/cache
export CONDA_ENVS_PATH=$P/envs
mkdir -p "$TMPDIR"
trap 'rm -rf "$TMPDIR"' EXIT

module load Miniforge3
eval "$(conda shell.bash hook)"
echo "== $(hostname), $(date)"

# 1. Model server. The EEE driver (595) supports CUDA 13, so current vLLM works here,
#    unlike MLDA gpu21 (CUDA 12.7, pinned to 0.9.2). Pinned for reproducibility.
conda create -y -q -n vllm python=3.12
conda activate vllm
pip install -q "vllm==0.30.0"
python -c "import vllm, torch; print('vllm', vllm.__version__, '| torch', torch.__version__, 'cuda', torch.version.cuda)"
conda deactivate

# 2. Pipeline: same requirements as on MLDA.
conda create -y -q -n swed python=3.12
conda activate swed
command -v git >/dev/null || conda install -y -q -c conda-forge git
pip install -q -r "$REPO/ablation/gpu21/requirements-swed.txt"
(cd "$REPO" && python -c "import sys; sys.path[:0]=['swe-debate/localization','swe-debate']; import entity_localization_pipeline; print('imports ok')")
conda deactivate

# 3. Models (into $HF_HOME on the SSD). 7B = debugging model, as on MLDA.
conda activate vllm
for m in Qwen/Qwen2.5-Coder-7B-Instruct intfloat/multilingual-e5-large-instruct; do
    hf download "$m" >/dev/null || huggingface-cli download "$m" >/dev/null
    echo "downloaded $m"
done
pip cache purge -q || true

du -sh "$P"/envs/* "$HF_HOME"
echo "== setup finished $(date)"

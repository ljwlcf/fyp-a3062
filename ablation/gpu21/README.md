# Running on MLDA gpu21

gpu21 is one shared workstation (4x RTX 3090, 24 GB each). There is no job queue: you log
in and run things directly. MLDA rules: use at most 1-2 GPUs, free GPU memory when done,
keep only files you need (the disk is shared).

Everything below is typed by hand. Steps 1-4 are one-time setup; step 5 is every run.

## 1. Get the code onto gpu21 (from your Mac)

Add an alias so you can type `ssh gpu21`. In `~/.ssh/config` on the Mac:

```
Host gpu21
    HostName gpu21.dynip.ntu.edu.sg
    User s126mdg21_05
    IdentityFile ~/.ssh/id_ed25519
```

Copy the repo, minus the PDFs and the 700 MB of cloned repositories, then only the graph
the smoke test needs (all 75 graphs are 769 MB):

```bash
rsync -az --exclude papers --exclude 'data/repos*' --exclude data/graphs --exclude '__pycache__' ~/IM4080/FYP-A3062/ gpu21:~/FYP-A3062/
ssh gpu21 mkdir -p FYP-A3062/data/graphs
rsync -az ~/IM4080/FYP-A3062/data/graphs/sphinx-doc__sphinx-8269.pkl gpu21:~/FYP-A3062/data/graphs/
```

Re-run the first `rsync` whenever code changes on the Mac.

## 2. Check disk space and install conda (on gpu21)

Setup needs about 35 GB: two Python environments (~15 GB), the 7B model (~15 GB), the
embedding model (~2 GB).

```bash
df -h ~
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3
~/miniforge3/bin/conda init bash && source ~/.bashrc
```

## 3. Two environments, kept separate

vLLM and SWE-Debate pin different versions of torch, so each gets its own environment.

```bash
# the model server
conda create -n vllm python=3.12 -y && conda activate vllm
pip install vllm
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
vllm --version
```

The last two lines must print `True` and a version. gpu21's driver supports CUDA up to
12.7. If `is_available()` is `False` or you see "driver too old", the newest vLLM wants a
newer driver: `pip install "vllm<0.11"` and check again. Write the working version down;
it goes in the notes.

```bash
# the pipeline
conda create -n swed python=3.12 -y && conda activate swed
cd ~/FYP-A3062
pip install -r swe-debate/localization/requirements.txt
pip install transformers
python -c "import sys; sys.path[:0]=['swe-debate/localization','swe-debate']; import entity_localization_pipeline; print('imports ok')"
```

If the last line fails with `ModuleNotFoundError`, `pip install` the missing package and try
again. Note every package you add; requirements.txt is known to be incomplete.

## 4. Download the model once

```bash
conda activate vllm
huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct
```

## 5. Each run

Work inside `tmux` so a dropped connection does not kill the run.

```bash
tmux new -s fyp
nvidia-smi                       # pick a GPU with no processes, say 2
```

**Window 1: the model server.**

```bash
conda activate vllm
CUDA_VISIBLE_DEVICES=2 vllm serve Qwen/Qwen2.5-Coder-7B-Instruct \
    --host 127.0.0.1 --port 8765 --dtype bfloat16 \
    --max-model-len 32768 --gpu-memory-utilization 0.90 --seed 0
```

Wait for `Application startup complete`. Then `Ctrl-b c` opens a second window.

**Window 2: check the server, then run.**

```bash
curl -s http://127.0.0.1:8765/v1/models
conda activate swed
cd ~/FYP-A3062
python ablation/harness/run_localization.py ablation/configs/smoke_localization_v1.yaml
```

The last line per instance reads like
`sphinx-doc__sphinx-8269: ok in 412.3 s, 31 calls (0 failed, 0 hit max_tokens), ...`.
Output lands in `ablation/results/smoke_localization_v1/<run_id>/`: `raw.jsonl` (output,
tokens, every call), `manifest.json`, and `stage_cache/` (the pipeline's own per-stage
record, including every vote and debate turn).

**When done: free the GPU.** Go to window 1 (`Ctrl-b 0`), press `Ctrl-c`, then check
`nvidia-smi` shows no process of yours. `exit` closes tmux windows. To leave tmux running
and log out, `Ctrl-b d`; `tmux attach -t fyp` gets back in.

**Bring the results home (on the Mac):**

```bash
rsync -az gpu21:~/FYP-A3062/ablation/results/smoke_localization_v1/ ~/IM4080/FYP-A3062/ablation/results/smoke_localization_v1/
```

#!/bin/bash
# Print the sbatch GPU options for a run, by the GPU rules (decisions.md 2026-10-02, "GPU rules"):
#   1. all arms of one comparison use the same GPU model and count: run this ONCE per comparison
#      and reuse its output for every arm;
#   2. 32B / 72B (any model needing > 48 GB) always get 2 pro6000 on one node, no fallback;
#   3. smaller models (7B debugging) also default to 2 pro6000, unless a fallback pair
#      (2x 6000ada / l40, then a6000 / a40) would FINISH clearly sooner: estimated start
#      (sbatch --test-only, nothing submitted) + expected run time (past manifests,
#      ablation/harness/runtime_estimates.py); "clearly" = at least 30 min and 25% sooner;
#   4. the job script then uses tensor parallel for 32B/72B and two replicas for 7B
#      (PARALLEL=dp), which this script also prints as an --export hint on stderr.
# Run on the EEE login node from ~/FYP-A3062 (one sbatch --test-only per GPU pair).
#   ablation/eee/pick_gpu.sh <served-model> <GB_NEEDED> [N_INSTANCES=10]
# Output (stdout), e.g.:  --gres=gpu:pro6000:2 -C highmem
# Use:  sbatch $(ablation/eee/pick_gpu.sh Qwen/Qwen2.5-Coder-7B-Instruct 24) ... job.sh ...
model=${1:?usage: pick_gpu.sh <served-model> <GB_NEEDED> [N_INSTANCES]}; need=${2:?GB needed}
n=${3:-10}
pro="--gres=gpu:pro6000:2 -C highmem"

if [ "$need" -gt 48 ]; then
    echo "rule 2: ${need} GB model -> 2x pro6000, tensor parallel, no fallback" >&2
    echo "$pro"; exit 0
fi

est_start_min() {  # minutes until Slurm's estimated start for these sbatch GPU options
    local s
    s=$(sbatch --test-only $1 --time=04:00:00 --wrap true 2>&1 | grep -o "start at [0-9T:-]*" | cut -d" " -f3)
    [ -z "$s" ] && { echo 99999; return; }
    echo $(( ( $(date -u -d "$s" +%s) - $(date -u +%s) ) / 60 ))
}
per_inst() {  # expected minutes per instance on GPU model $1 for this served model (past runs)
    python3 ablation/harness/runtime_estimates.py "$model" 2>/dev/null | awk -F'\t' -v g="$1" \
        '$1 == g { split($6, a, " "); print a[1]; exit }'
}

# Our own running/pending jobs count against the ug per-model limit; a model whose limit they
# already fill cannot start until they finish, whatever Slurm's estimate says (its --test-only
# estimates are dominated by our own queue). Such a model is skipped.
own() { squeue --me -h -o "%b" | grep -o "gpu:$1:[0-9]*" | awk -F: '{n += $3} END {print n + 0}'; }
limit_of() { case "$1" in rtx5090) echo 1 ;; *) echo 2 ;; esac; }
blocked() { [ $(( $(own "$1") + 2 )) -gt "$(limit_of "$1")" ]; }

pro_run=$(per_inst pro6000); pro_run=${pro_run:-1}
slow=$(per_inst a6000); slow=${slow:-$(awk -v p="$pro_run" 'BEGIN{print p*4}')}
if blocked pro6000; then
    pro_finish=999999
    echo "2x pro6000: blocked, our own jobs hold the ug pro6000 limit ($(own pro6000) GPUs)" >&2
else
    pro_finish=$(( $(est_start_min "$pro") + $(awk -v r="$pro_run" -v n="$n" 'BEGIN{printf "%d", r*n}') ))
    echo "2x pro6000: estimated finish in ${pro_finish} min (start + ${pro_run} min/instance x $n)" >&2
fi
best="$pro"; best_finish=$pro_finish
for g in 6000ada l40 a6000 a40; do
    if blocked $g; then echo "2x $g: blocked by our own jobs" >&2; continue; fi
    r=$(per_inst $g); r=${r:-$slow}          # no history: assume a6000 speed (conservative)
    f=$(( $(est_start_min "--gres=gpu:$g:2") + $(awk -v r="$r" -v n="$n" 'BEGIN{printf "%d", r*n}') ))
    echo "2x $g: estimated finish in ${f} min (${r} min/instance)" >&2
    if { [ "$pro_finish" -eq 999999 ] || { [ "$f" -le $(( pro_finish - 30 )) ] && [ "$f" -le $(( pro_finish * 3 / 4 )) ]; }; } && [ "$f" -lt "$best_finish" ]; then
        best="--gres=gpu:$g:2"; best_finish=$f
    fi
done
echo "rule 3: choose '$best' (estimated finish ${best_finish} min); small model -> PARALLEL=dp" >&2
echo "$best"

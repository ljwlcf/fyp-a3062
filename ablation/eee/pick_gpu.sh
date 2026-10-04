#!/bin/bash
# Print the sbatch GPU options for a run, by the GPU rules (decisions.md 2026-10-04, pro6000 first):
#   1. all arms of one comparison use the same GPU model and count: run this ONCE per comparison
#      and reuse its output for every arm;
#   2. 32B / 72B (any model needing > 48 GB) get 2 pro6000 on one node under the normal ug QoS and
#      wait in the queue (main-experiment passes are chained there and must not be preempted);
#   3. smaller models (7B) also get 2 pro6000: under ug if our ug pro6000 limit is free, otherwise
#      under the killable QoS (override-limits-but-killable: separate limits, idle cards only,
#      requeued if a regular job needs them; the job script resumes after a requeue). Another card
#      model only on request: ALLOW_FALLBACK=1, then the fastest-finishing pair by sbatch
#      --test-only + run time from past manifests;
#   4. the job script uses tensor parallel for 32B/72B and two replicas for 7B (PARALLEL=dp).
# Our own ug running/pending jobs count against the ug per-model limit, so a model they already
# fill cannot start until they finish, whatever Slurm's estimate says.
# Run on the EEE login node from ~/FYP-A3062.
#   ablation/eee/pick_gpu.sh <served-model> <GB_NEEDED> [N_INSTANCES=10]
# Output (stdout), e.g.:  --gres=gpu:pro6000:2 -C highmem
#            or:          --qos=override-limits-but-killable --requeue --open-mode=append --gres=gpu:pro6000:2 -C highmem
# Use:  sbatch $(ablation/eee/pick_gpu.sh Qwen/Qwen2.5-Coder-7B-Instruct 24) ... job.sh ...
model=${1:?usage: pick_gpu.sh <served-model> <GB_NEEDED> [N_INSTANCES]}; need=${2:?GB needed}
n=${3:-10}
pro="--gres=gpu:pro6000:2 -C highmem"
killable="--qos=override-limits-but-killable --requeue --open-mode=append $pro"

own() { squeue --me -h -o "%q %b" | awk '$1 != "override-limits-but-killable"' \
        | grep -o "gpu:$1:[0-9]*" | awk -F: '{n += $3} END {print n + 0}'; }
limit_of() { case "$1" in rtx5090) echo 1 ;; *) echo 2 ;; esac; }
blocked() { [ $(( $(own "$1") + 2 )) -gt "$(limit_of "$1")" ]; }

if [ "$need" -gt 48 ]; then
    if blocked pro6000; then
        echo "rule 2: ${need} GB -> 2x pro6000 (ug); our own ug jobs hold the pro6000 limit, so it queues behind them" >&2
    else
        echo "rule 2: ${need} GB -> 2x pro6000 (ug), tensor parallel" >&2
    fi
    echo "$pro"; exit 0
fi

if ! blocked pro6000; then
    echo "rule 3: small model -> 2x pro6000 (ug), PARALLEL=dp" >&2
    echo "$pro"; exit 0
fi
if [ "${ALLOW_FALLBACK:-0}" != "1" ]; then
    echo "rule 3: ug pro6000 limit held by our own jobs -> 2x pro6000 under the killable QoS, PARALLEL=dp" >&2
    echo "$killable"; exit 0
fi

# ALLOW_FALLBACK=1: fastest-finishing non-pro6000 pair
est_start_min() {
    local s
    s=$(sbatch --test-only $1 --time=04:00:00 --wrap true 2>&1 | grep -o "start at [0-9T:-]*" | cut -d" " -f3)
    [ -z "$s" ] && { echo 99999; return; }
    echo $(( ( $(date -u -d "$s" +%s) - $(date -u +%s) ) / 60 ))
}
per_inst() {
    python3 ablation/harness/runtime_estimates.py "$model" 2>/dev/null | awk -F'\t' -v g="$1" \
        '$1 == g { split($6, a, " "); print a[1]; exit }'
}
best=""; best_finish=999999
for g in 6000ada l40 a6000 a40; do
    if blocked $g; then echo "2x $g: blocked by our own jobs" >&2; continue; fi
    r=$(per_inst $g); r=${r:-3.4}            # no history: a6000-class speed
    f=$(( $(est_start_min "--gres=gpu:$g:2") + $(awk -v r="$r" -v n="$n" 'BEGIN{printf "%d", r*n}') ))
    echo "2x $g: estimated finish in ${f} min (${r} min/instance)" >&2
    [ "$f" -lt "$best_finish" ] && { best="--gres=gpu:$g:2"; best_finish=$f; }
done
[ -z "$best" ] && { echo "no fallback pair available; using the killable pro6000" >&2; best="$killable"; }
echo "rule 3 (fallback requested): '$best'" >&2
echo "$best"

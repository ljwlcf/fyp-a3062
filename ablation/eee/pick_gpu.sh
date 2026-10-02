#!/bin/bash
# Print the best GPU that is free right now, as "<model>:<count>" for --gres=gpu:...,
# by the project's priority order (decisions.md 2026-10-02):
#   pro6000 > rtx5090 > 6000ada / l40 > a6000 / a40.
#   ablation/eee/pick_gpu.sh [GB_NEEDED=24]
# GB_NEEDED is the model's total GPU memory need (weights + KV cache). For each model, in
# priority order, the count is the FEWEST cards that cover it (ceil(GB_NEEDED / card GB)); the
# model qualifies if the ug QoS allows that many. The first qualifying model with that many free
# cards wins. If none has enough free, it queues on the first qualifying model. One sinfo call,
# light enough for a login node. Free counts go to stderr.
# Use:  sbatch --gres=gpu:$(ablation/eee/pick_gpu.sh 80) ...   (job script sets tensor parallel)
need=${1:-24}
#            model    GB  ug-limit
priority="pro6000  96 2
rtx5090  32 1
6000ada  48 2
l40      48 2
a6000    48 2
a40      48 2"

free=$(sinfo -N -h -O "Gres:40,GresUsed:50,StateCompact:12" | sort -u | awk '
  $3 ~ /drain|down|maint|fail|\*/ {next}
  $1 ~ /^gpu:/ {
    split($1, t, ":"); m = t[2]; tot = t[3]; sub(/\(.*/, "", tot)
    split($2, u, ":"); used = u[3]; sub(/\(.*/, "", used)
    f[m] += tot - used
  }
  END { for (m in f) print m, f[m] }')
echo "free now: $(echo $free | tr '\n' ' ')" >&2

first=""
while read -r model gb limit; do
    n=$(( (need + gb - 1) / gb ))              # fewest cards that cover the need
    [ "$n" -le "$limit" ] || continue           # QoS would refuse it
    [ -z "$first" ] && first="$model:$n"
    have=$(echo "$free" | awk -v m="$model" '$1 == m {print $2}')
    if [ "${have:-0}" -ge "$n" ]; then echo "$model:$n"; exit 0; fi
done <<< "$priority"

if [ -z "$first" ]; then echo "no GPU model can hold ${need} GB within the QoS limits" >&2; exit 1; fi
echo "no qualifying GPU free; queueing on $first" >&2
echo "$first"

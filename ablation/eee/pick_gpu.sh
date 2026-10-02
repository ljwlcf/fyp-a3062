#!/bin/bash
# Print the best GPU model that is free right now, by the project's priority order
# (decisions.md 2026-10-02): pro6000 > rtx5090 > 6000ada / l40 > a6000 / a40.
#   ablation/eee/pick_gpu.sh [GB_NEEDED=24] [N_GPUS=1]
# GB_NEEDED is the model's total GPU memory need (weights + KV cache); a GPU model qualifies
# if N_GPUS x its memory covers it and the ug QoS allows N_GPUS of it. Light enough for a
# login node (one sinfo call). Prints e.g. "pro6000"; free counts go to stderr.
# Use:  sbatch --gres=gpu:$(ablation/eee/pick_gpu.sh 24):1 ...
need=${1:-24}; n=${2:-1}
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
    [ $((gb * n)) -ge "$need" ] && [ "$n" -le "$limit" ] || continue
    [ -z "$first" ] && first=$model
    have=$(echo "$free" | awk -v m="$model" '$1 == m {print $2}')
    if [ "${have:-0}" -ge "$n" ]; then echo "$model"; exit 0; fi
done <<< "$priority"

echo "no qualifying GPU free; queueing on $first" >&2
echo "$first"

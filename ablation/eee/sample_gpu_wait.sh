#!/bin/bash
# Sample how long a 2-GPU job would wait on the EEE cluster, every 30 min, from the Mac.
# Measurement for decisions.md 2026-10-02 (GPU rules): is "32B/72B always on 2 pro6000" practical?
#   nohup caffeinate -i ablation/eee/sample_gpu_wait.sh [hours=24] [interval_min=30] &
#   ablation/eee/sample_gpu_wait.sh 0      # one sample, then exit (testing)
# Each sample appends one line per GPU pair to ablation/results/gpu_wait_v1/samples.tsv:
#   UTC time, SGT time, pair, nodes with >=2 free cards of that model (drained nodes excluded),
#   total free cards of that model, Slurm's estimated start (sbatch --test-only, nothing is
#   submitted), estimated wait in minutes.
# If EEE is unreachable (Mac off NTUSECURE/VPN, asleep, ssh failing) the sample is logged as
# "skipped" and sampling simply continues at the next slot: it never stops early.
hours=${1:-24}; every=${2:-30}
cd "$(dirname "$0")/../.." || exit 1
out=ablation/results/gpu_wait_v1/samples.tsv
[ -s "$out" ] || printf "utc\tsgt\tpair\tnodes_2free\tfree_cards\test_start_utc\test_wait_min\tstatus\n" > "$out"
end=$(( $(date +%s) + hours * 3600 )); once=$([ "$hours" -eq 0 ] && echo 1)
while [ -n "$once" ] || [ "$(date +%s)" -lt "$end" ]; do
    utc=$(date -u +%FT%T); sgt=$(TZ=Asia/Singapore date +%FT%T)
    res=$(ssh -o BatchMode=yes -o ConnectTimeout=20 eee '
      now=$(date -u +%s)
      sinfo -N -h -O "NodeList:20,Gres:40,GresUsed:50,StateCompact:12" | sort -u | awk "
        \$4 ~ /drain|down|maint|fail|\\*/ {next}
        \$2 ~ /^gpu:/ { split(\$2,t,\":\"); m=t[2]; tot=t[3]; sub(/\\(.*/,\"\",tot)
                        split(\$3,u,\":\"); used=u[3]; sub(/\\(.*/,\"\",used); f=tot-used
                        free[m]+=f; if (f>=2) n2[m]++ }
        END { for (m in free) print m, free[m], n2[m]+0 }" > /tmp/$USER.gpufree
      for pair in "pro6000:2 -C highmem" "pro6000:2" "6000ada:2" "l40:2" "a6000:2" "a40:2"; do
        g=${pair%% *}; c=""; [ "$pair" != "$g" ] && c=${pair#* }
        m=${g%%:*}; read -r _ fc n2 < <(grep "^$m " /tmp/$USER.gpufree || echo "$m 0 0")
        s=$(sbatch --test-only --gres=gpu:$g $c --time=02:00:00 --wrap true 2>&1 | grep -o "start at [0-9T:-]*" | cut -d" " -f3)
        if [ -n "$s" ]; then w=$(( ( $(date -u -d "$s" +%s 2>/dev/null || echo $now) - now ) / 60 )); [ $w -lt 0 ] && w=0; else s=NA; w=NA; fi
        printf "%s %s %s %s %s\n" "$(echo $pair | tr " " "_")" "$n2" "$fc" "$s" "$w"
      done' 2>/dev/null | grep -v "^EEE\|^Connecting\|^Relevant\|^- https\|^$")
    if [ -n "$res" ]; then
        while read -r pair n2 fc s w; do
            printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\tok\n" "$utc" "$sgt" "$pair" "$n2" "$fc" "$s" "$w" >> "$out"
        done <<< "$res"
    else
        printf "%s\t%s\tall\tNA\tNA\tNA\tNA\tskipped (EEE unreachable)\n" "$utc" "$sgt" >> "$out"
    fi
    [ -n "$once" ] && break
    sleep $(( every * 60 ))
done
echo "sampling finished $(date -u +%FT%T)" >&2

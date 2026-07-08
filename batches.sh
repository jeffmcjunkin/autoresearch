#!/bin/bash
# Run every numeric batch defined in targets.tsv, 5-way parallel each, in order. Skips batches whose
# modes already reached ROUNDS experiments (resumable). Frees worktrees + regenerates README between
# batches. Detached; monitor with: cat batches.log ; cat README.md
set -u
AR=/c/Users/jeff/Documents/autoresearch; HC=/c/Users/jeff/Documents/hashcat
ROUNDS="${ROUNDS:-6}"; RTIMEOUT="${RTIMEOUT:-1500}"
export GPU_LOCK="$AR/.gpu.lock"
nvidia-smi -i 0 -lgc 1710,1710 >/dev/null 2>&1
mkdir -p "$AR/logs"

exp_count(){ local f="$AR/results_$1.tsv"; [ -f "$f" ] && echo $(( $(wc -l < "$f") - 2 )) || echo 0; }

run_batch(){
  local n=$1; shift; local modes="$*"; local waited=0 done=0 total=0
  for M in $modes; do total=$((total+1)); done
  echo "[$(date '+%F %T')] === BATCH $n launch: $modes ===" | tee -a "$AR/batches.log"
  for M in $modes; do rm -f "$AR/logs/loop_$M.out"; done
  MODES="$modes" ROUNDS="$ROUNDS" RTIMEOUT="$RTIMEOUT" bash "$AR/parallel.sh" >> "$AR/batches.log" 2>&1
  while [ "$done" -lt "$total" ] && [ "$waited" -lt 21600 ]; do   # 6h/batch cap (slow container/KDF modes)
    sleep 30; waited=$((waited+30)); done=0
    for M in $modes; do grep -q "=== m$M complete" "$AR/logs/loop_$M.out" 2>/dev/null && done=$((done+1)); done
    bash "$AR/gen_readme.sh" >/dev/null 2>&1
  done
  echo "[$(date '+%F %T')] === BATCH $n done ($done/$total) ===" | tee -a "$AR/batches.log"
  for M in $modes; do git -C "$HC" worktree remove --force "$AR/wt_$M" 2>/dev/null; done
  git -C "$HC" worktree prune 2>/dev/null; bash "$AR/gen_readme.sh" >/dev/null 2>&1
}

for n in $(awk -F'\t' 'NR>1 && $2 ~ /^[0-9]+$/ {print $2}' "$AR/targets.tsv" | sort -un); do
  modes=$(awk -F'\t' -v b="$n" 'NR>1 && $2==b {print $1}' "$AR/targets.tsv" | tr '\n' ' ')
  alldone=1; for M in $modes; do [ "$(exp_count $M)" -ge "$ROUNDS" ] || alldone=0; done
  if [ "$alldone" = 1 ]; then echo "[$(date '+%T')] batch $n already complete, skip" | tee -a "$AR/batches.log"; continue; fi
  run_batch "$n" $modes
done
nvidia-smi -i 0 -rgc >/dev/null 2>&1
echo "[$(date '+%F %T')] === ALL BATCHES COMPLETE ===" | tee -a "$AR/batches.log"

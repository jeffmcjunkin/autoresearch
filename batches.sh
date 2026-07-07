#!/bin/bash
# Run 4 batches of 5 modes, each batch 5-way parallel. Waits between batches, frees worktrees,
# regenerates README.md live. Detached; monitor with: cat batches.log ; cat README.md
set -u
AR=/c/Users/jeff/Documents/autoresearch; HC=/c/Users/jeff/Documents/hashcat
ROUNDS="${ROUNDS:-6}"; RTIMEOUT="${RTIMEOUT:-1500}"
export GPU_LOCK="$AR/.gpu.lock"
nvidia-smi -i 0 -lgc 1710,1710 >/dev/null 2>&1
mkdir -p "$AR/logs"
B1="17300 17500 17700 17900 18000"      # SHA3/Keccak family (high yield)
B2="3000 1000 5500 5600 27000"          # LM / NTLM / NetNTLM
B3="19600 19700 18200 9700 9800"        # Kerberoasting / AS-REP / Office-2003
B4="9400 9500 9600 1100 2100"           # Office modern / MSCache

run_batch(){
  local n=$1; shift; local modes="$*"; local waited=0 done=0
  echo "[$(date '+%F %T')] === BATCH $n launch: $modes ===" | tee -a "$AR/batches.log"
  for M in $modes; do rm -f "$AR/logs/loop_$M.out"; done
  MODES="$modes" ROUNDS="$ROUNDS" RTIMEOUT="$RTIMEOUT" bash "$AR/parallel.sh" >> "$AR/batches.log" 2>&1
  while [ "$done" -lt 5 ] && [ "$waited" -lt 14400 ]; do   # 4h/batch safety cap
    sleep 30; waited=$((waited+30)); done=0
    for M in $modes; do grep -q "=== m$M complete" "$AR/logs/loop_$M.out" 2>/dev/null && done=$((done+1)); done
    bash "$AR/gen_readme.sh" >/dev/null 2>&1
  done
  echo "[$(date '+%F %T')] === BATCH $n done ($done/5) ===" | tee -a "$AR/batches.log"
  for M in $modes; do git -C "$HC" worktree remove --force "$AR/wt_$M" 2>/dev/null; done
  git -C "$HC" worktree prune 2>/dev/null
  bash "$AR/gen_readme.sh" >/dev/null 2>&1
}
run_batch 1 $B1
run_batch 2 $B2
run_batch 3 $B3
run_batch 4 $B4
nvidia-smi -i 0 -rgc >/dev/null 2>&1
echo "[$(date '+%F %T')] === ALL BATCHES COMPLETE ===" | tee -a "$AR/batches.log"

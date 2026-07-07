#!/bin/bash
# Bring up N parallel autoresearch loops (one per hash mode), each in its own hashcat worktree,
# GPU serialized by the shared mutex. Reuses drive.sh unchanged except HASHCAT_DIR.
set -u
AR=/c/Users/jeff/Documents/autoresearch
MAIN=/c/Users/jeff/Documents/hashcat
MODES=(${MODES:-600 1700 10800 6000 17600})     # the remaining modes; one loop each
ROUNDS="${ROUNDS:-6}"; RTIMEOUT="${RTIMEOUT:-1500}"
export GPU_LOCK="$AR/.gpu.lock"; rm -rf "$GPU_LOCK"          # start clean
nvidia-smi -i 0 -lgc 1710,1710 >/dev/null 2>&1
mkdir -p "$AR/logs"
echo "[$(date '+%T')] bringing up ${#MODES[@]} loops: ${MODES[*]}"
for M in "${MODES[@]}"; do
  wt="$AR/wt_$M"; BR="autoresearch/${M}-jul6"
  git -C "$MAIN" show-ref --verify --quiet "refs/heads/$BR" || git -C "$MAIN" branch "$BR" master
  if [ ! -d "$wt/OpenCL" ]; then
    git -C "$MAIN" worktree add -q "$wt" "$BR" || { echo "  m$M: worktree add failed"; continue; }
    cp "$MAIN/hashcat.exe" "$wt/"
    cp -r "$MAIN/modules" "$wt/"
  fi
  ndll=$(ls "$wt/modules"/*.dll 2>/dev/null | wc -l)
  HASHCAT_DIR="$wt" MODES="$M" ROUNDS="$ROUNDS" RTIMEOUT="$RTIMEOUT" GPU_LOCK="$GPU_LOCK" \
    nohup bash "$AR/drive.sh" >> "$AR/logs/loop_${M}.out" 2>&1 &
  echo "  m$M loop pid $! (worktree $wt, $ndll module dlls)"
  sleep 2
done
echo "[$(date '+%T')] all loops launched. monitor: cat drive.log ; ls results_*.tsv"

#!/bin/bash
# ==========================================================================================
# READ-ONLY eval harness for hashcat-kernel autoresearch (the prepare.py / evaluate_bpb analog).
# The agent MUST NOT modify this file. Ground-truth metric. HIGHER *_mhs is better; selftest MUST be PASS.
#   RESULT primary=11700 primary_mhs=188.9 second_mhs=NA selftest=PASS clock=1710
#
# Mode-agnostic: PRIMARY_MODE (required), SECOND_MODE (optional, ""), SELFTEST_MODES (optional).
# CONCURRENCY-SAFE: the whole benchmark section runs under a shared GPU mutex (GPU_LOCK), so parallel
# loops never contend on the GPU. Bakes in the traps: lock the clock, CLEAR the NVRTC cache per mode
# (header edits don't invalidate it), median-of-3, correctness FIRST.
# ==========================================================================================
set -u
HASHCAT="${HASHCAT_DIR:-/c/Users/jeff/Documents/hashcat}"
PRIMARY="${PRIMARY_MODE:?set PRIMARY_MODE}"
SECOND="${SECOND_MODE:-}"
SELFTEST_MODES="${SELFTEST_MODES:-}"
CLK=1710
GPU_LOCK="${GPU_LOCK:-/c/Users/jeff/Documents/autoresearch/.gpu.lock}"   # shared across parallel loops

gpu_lock () { local w=0
  until mkdir "$GPU_LOCK" 2>/dev/null; do
    if [ -f "$GPU_LOCK/ts" ] && [ $(( $(date +%s) - $(cat "$GPU_LOCK/ts" 2>/dev/null || echo 0) )) -gt 300 ]; then rm -rf "$GPU_LOCK"; continue; fi
    sleep 1; w=$((w+1)); [ "$w" -gt 900 ] && break
  done; date +%s > "$GPU_LOCK/ts" 2>/dev/null; }
gpu_unlock () { rm -rf "$GPU_LOCK" 2>/dev/null; }

cd "$HASHCAT" || { echo "RESULT error=no_hashcat_dir"; exit 1; }
nvidia-smi -i 0 -lgc ${CLK},${CLK} >/dev/null 2>&1

median3 () {   # median-of-3 H/s; cache cleared first (mandatory for header edits); warm-up discarded
  local m=$1 pad s vals=() sorted n
  pad=$(printf 'm%05d' "$m")
  rm -f kernels/${pad}_a*.kernel kernels/${pad}-*.kernel 2>/dev/null
  for i in 1 2 3 4; do
    s=$(timeout 150 ./hashcat.exe -b -m "$m" -d 1 -D 2 --machine-readable --quiet 2>/dev/null | grep "^1:$m:" | cut -d: -f6)
    [ -n "$s" ] && vals+=("$s")
  done
  [ "${#vals[@]}" -lt 2 ] && { echo "FAIL"; return; }
  sorted=$(printf '%s\n' "${vals[@]:1}" | sort -n); n=$(printf '%s\n' "$sorted" | grep -c .)
  printf '%s\n' "$sorted" | sed -n "$(((n+1)/2))p"
}
to_mhs () { awk -v x="$1" 'BEGIN{ if (x ~ /^[0-9]+$/) printf "%.1f", x/1e6; else print "FAIL" }'; }

gpu_lock                                        # ---- exclusive GPU section ----
praw=$(median3 "$PRIMARY")
st="PASS"; [ "$praw" = "FAIL" ] && st="FAIL:$PRIMARY"
sout="NA"
if [ -n "$SECOND" ]; then sraw=$(median3 "$SECOND"); [ "$sraw" = "FAIL" ] && st="FAIL:$SECOND"; sout=$(to_mhs "$sraw"); fi
for m in $SELFTEST_MODES; do
  rm -f kernels/$(printf 'm%05d' "$m")_a*.kernel kernels/$(printf 'm%05d' "$m")-*.kernel 2>/dev/null
  r=$(timeout 150 ./hashcat.exe -b -m "$m" -d 1 -D 2 2>&1)
  if echo "$r" | grep -qiE 'self-test failed|aborting' || ! echo "$r" | grep -qE 'Speed'; then st="FAIL:$m"; fi
done
gpu_unlock                                      # ---- end exclusive section ----

echo "RESULT primary=$PRIMARY primary_mhs=$(to_mhs "$praw") second_mhs=$sout selftest=$st clock=${CLK}"

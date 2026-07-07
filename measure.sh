#!/bin/bash
# ==========================================================================================
# READ-ONLY eval harness for hashcat-kernel autoresearch (the prepare.py / evaluate_bpb analog).
# The agent MUST NOT modify this file. Ground-truth metric. HIGHER *_mhs is better; selftest MUST be PASS.
#   RESULT primary=11700 primary_mhs=188.9 second_mhs=NA selftest=PASS clock=1710
#
# Mode-agnostic: PRIMARY_MODE (required), SECOND_MODE (optional, "" to skip),
# SELFTEST_MODES (optional extra blast-radius self-tests). Bakes in the hard-won traps:
#   - locks the GPU clock (thermal drift > any real win)
#   - CLEARS the NVRTC kernel cache per mode (hashcat does NOT invalidate cache on #included-header edits)
#   - median-of-3 (discards the compile/warm-up run)
#   - correctness FIRST: any self-test failure => selftest=FAIL:<mode>
# ==========================================================================================
set -u
HASHCAT="${HASHCAT_DIR:-/c/Users/jeff/Documents/hashcat}"
PRIMARY="${PRIMARY_MODE:?set PRIMARY_MODE}"
SECOND="${SECOND_MODE:-}"
SELFTEST_MODES="${SELFTEST_MODES:-}"
CLK=1710

cd "$HASHCAT" || { echo "RESULT error=no_hashcat_dir"; exit 1; }
nvidia-smi -i 0 -lgc ${CLK},${CLK} >/dev/null 2>&1

median3 () {   # median-of-3 H/s for a mode; cache cleared first (mandatory for header edits); warm-up discarded
  local m=$1 pad s vals=() sorted n
  pad=$(printf 'm%05d' "$m")
  rm -f kernels/${pad}_a*.kernel kernels/${pad}-*.kernel 2>/dev/null
  for i in 1 2 3 4; do
    s=$(timeout 150 ./hashcat.exe -b -m "$m" -d 1 -D 2 --machine-readable --quiet 2>/dev/null | grep "^1:$m:" | cut -d: -f6)
    [ -n "$s" ] && vals+=("$s")
  done
  [ "${#vals[@]}" -lt 2 ] && { echo "FAIL"; return; }
  sorted=$(printf '%s\n' "${vals[@]:1}" | sort -n)
  n=$(printf '%s\n' "$sorted" | grep -c .)
  printf '%s\n' "$sorted" | sed -n "$(((n+1)/2))p"
}
to_mhs () { awk -v x="$1" 'BEGIN{ if (x ~ /^[0-9]+$/) printf "%.1f", x/1e6; else print "FAIL" }'; }

praw=$(median3 "$PRIMARY")
st="PASS"; [ "$praw" = "FAIL" ] && st="FAIL:$PRIMARY"
sout="NA"
if [ -n "$SECOND" ]; then sraw=$(median3 "$SECOND"); [ "$sraw" = "FAIL" ] && st="FAIL:$SECOND"; sout=$(to_mhs "$sraw"); fi
for m in $SELFTEST_MODES; do
  rm -f kernels/$(printf 'm%05d' "$m")_a*.kernel kernels/$(printf 'm%05d' "$m")-*.kernel 2>/dev/null
  r=$(timeout 150 ./hashcat.exe -b -m "$m" -d 1 -D 2 2>&1)
  if echo "$r" | grep -qiE 'self-test failed|aborting' || ! echo "$r" | grep -qE 'Speed'; then st="FAIL:$m"; fi
done
echo "RESULT primary=$PRIMARY primary_mhs=$(to_mhs "$praw") second_mhs=$sout selftest=$st clock=${CLK}"

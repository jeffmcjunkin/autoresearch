#!/bin/bash
# ==========================================================================================
# READ-ONLY eval harness for hashcat RC4-kernel autoresearch (the prepare.py / evaluate_bpb analog).
# The agent MUST NOT modify this file. It is the ground-truth metric.
#
# Emits ONE greppable line (the val_bpb analog). HIGHER *_mhs is better. selftest MUST be PASS.
#   RESULT primary=13100 primary_mhs=1447.1 second=9700 second_mhs=1134.0 selftest=PASS clock=1710
#
# Bakes in the traps learned the hard way:
#   - locks the GPU clock (thermal drift > any real win)
#   - CLEARS the NVRTC kernel cache per mode (hashcat does NOT invalidate cache on #included-header edits)
#   - median-of-3 (discards the compile/warm-up run)
#   - correctness FIRST: any self-test failure across the shared-helper blast radius => selftest=FAIL
# ==========================================================================================
set -u
HASHCAT="${HASHCAT_DIR:-/c/Users/jeff/Documents/hashcat}"
PRIMARY="${PRIMARY_MODE:-13100}"          # Kerberoasting (RC4-HMAC, 16-byte key) = flagship metric
SECOND="${SECOND_MODE:-9700}"             # Office MD5+RC4 (5-byte key) = different rc4_init variant + regression guard
SELFTEST_MODES="${SELFTEST_MODES:-18200 7500 9800}"   # more of the shared-helper blast radius
CLK=1710

cd "$HASHCAT" || { echo "RESULT error=no_hashcat_dir"; exit 1; }
nvidia-smi -i 0 -lgc ${CLK},${CLK} >/dev/null 2>&1     # idempotent clock lock

# median-of-3 H/s for a mode, cache cleared first (mandatory for header edits), warm-up discarded
median3 () {
  local m=$1 pad s vals=() sorted n
  pad=$(printf 'm%05d' "$m")
  rm -f kernels/${pad}_a*.kernel 2>/dev/null
  for i in 1 2 3 4; do
    s=$(timeout 120 ./hashcat.exe -b -m "$m" -d 1 -D 2 --machine-readable --quiet 2>/dev/null | grep "^1:$m:" | cut -d: -f6)
    [ -n "$s" ] && vals+=("$s")
  done
  [ "${#vals[@]}" -lt 2 ] && { echo "FAIL"; return; }
  sorted=$(printf '%s\n' "${vals[@]:1}" | sort -n)      # drop first (compile/warm-up)
  n=$(printf '%s\n' "$sorted" | grep -c .)
  printf '%s\n' "$sorted" | sed -n "$(((n+1)/2))p"
}

to_mhs () { awk -v x="$1" 'BEGIN{ if (x ~ /^[0-9]+$/) printf "%.1f", x/1e6; else print "FAIL" }'; }

praw=$(median3 "$PRIMARY"); sraw=$(median3 "$SECOND")
st="PASS"
[ "$praw" = "FAIL" ] && st="FAIL:$PRIMARY"
[ "$sraw" = "FAIL" ] && st="FAIL:$SECOND"
for m in $SELFTEST_MODES; do
  rm -f kernels/$(printf 'm%05d' "$m")_a*.kernel 2>/dev/null
  r=$(timeout 120 ./hashcat.exe -b -m "$m" -d 1 -D 2 2>&1)
  if echo "$r" | grep -qiE 'self-test failed|aborting' || ! echo "$r" | grep -qE 'Speed'; then st="FAIL:$m"; fi
done

echo "RESULT primary=$PRIMARY primary_mhs=$(to_mhs "$praw") second=$SECOND second_mhs=$(to_mhs "$sraw") selftest=$st clock=${CLK}"

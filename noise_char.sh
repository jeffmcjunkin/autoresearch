#!/bin/bash
# Wait for the 14-mode GPT-5.6 batch to finish, then characterize the harness noise floor:
# measure a FIXED (master) kernel many times and report mean/stddev/CV/2sigma-band per mode.
# If the 2sigma band is well under the ~1-2% loop noise band, we've been discarding real small wins.
AR=/c/Users/jeff/Documents/autoresearch; HC=/c/Users/jeff/Documents/hashcat
MODES14="17400 17600 17800 11700 11800 31100 9700 17700 18000 17500 17300 17900 10500 18200"

# --- 1. wait for the batch (all 14 'complete' markers stamped this hour) ---
while :; do
  d=0
  for M in $MODES14; do grep -qE "2026-07-09 1[34]:.*m$M complete" "$AR/drive.log" && d=$((d+1)); done
  [ "$d" -ge 14 ] && break
  sleep 20
done
echo "[$(date '+%T')] batch complete ($d/14) — starting noise characterization"

# --- 2. repeated measurement of the unchanged master kernel ---
cd "$HC"; git checkout -q master 2>/dev/null
nvidia-smi -i 0 -lgc 1710,1710 >/dev/null 2>&1
mspeed(){ uv run "$AR/ar.py" measure -m "$1" 2>/dev/null | grep -oE 'primary_mhs=[^ ]+' | cut -d= -f2; }
stat(){ awk -v M=$1 '{v[NR]=$1;s+=$1;ss+=$1*$1;if(NR==1||$1<mn)mn=$1;if(NR==1||$1>mx)mx=$1}
  END{n=NR;m=s/n;sd=sqrt(ss/n-m*m);
  printf "m%-6s n=%d mean=%.3f sd=%.4f CV=%.3f%%  min=%.3f max=%.3f range=%.3f%%  2sigma-band=+/-%.2f%%\n",
  M,n,m,sd,sd/m*100,mn,mx,(mx-mn)/m*100,2*sd/m*100}' "$AR/noise_$1.txt"; }

: > "$AR/noise_summary.txt"
for spec in "31100 40" "17400 30" "10500 25"; do
  set -- $spec; M=$1; N=$2
  : > "$AR/noise_$M.txt"
  for i in $(seq 1 "$N"); do mspeed "$M" >> "$AR/noise_$M.txt"; done
  stat "$M" | tee -a "$AR/noise_summary.txt"
done
nvidia-smi -i 0 -rgc >/dev/null 2>&1
echo "NOISE-CHAR-DONE $(date '+%T')"

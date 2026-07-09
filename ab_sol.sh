#!/bin/bash
# Wait for the noise characterization to finish, then interleaved clean A/B (vs master = total gain
# over stock) of the 9 GPT-5.6-Sol candidate wins. Same method that separated real wins from drift.
AR=/c/Users/jeff/Documents/autoresearch; HC=/c/Users/jeff/Documents/hashcat
while ! grep -q "NOISE-CHAR-DONE" "$AR/logs/noise_char.log" 2>/dev/null; do sleep 20; done
echo "[$(date '+%T')] noise char done — starting A/B of 5.6 candidates"
cd "$HC" || exit 1
nvidia-smi -i 0 -lgc 1710,1710 >/dev/null 2>&1
m(){ uv run "$AR/ar.py" measure -m "$1" 2>/dev/null | grep -oE 'primary_mhs=[^ ]+' | cut -d= -f2; }
: > "$AR/ab_sol_raw.txt"
for M in 11800 11700 10500 18200 18000 17400 17900 17600 17500; do
  git checkout -q master 2>/dev/null;               b1=$(m "$M")
  git checkout -q "autoresearch/$M-jul6" 2>/dev/null; w1=$(m "$M")
  git checkout -q master 2>/dev/null;               b2=$(m "$M")
  git checkout -q "autoresearch/$M-jul6" 2>/dev/null; w2=$(m "$M")
  echo "$M $b1 $w1 $b2 $w2" >> "$AR/ab_sol_raw.txt"
done
git checkout -q master 2>/dev/null
nvidia-smi -i 0 -rgc >/dev/null 2>&1
echo "=== GPT-5.6 A/B (avg of 2 interleaved master/win = TOTAL gain over stock) ===" > "$AR/ab_sol.txt"
awk '{b=($2+$4)/2; w=($3+$5)/2; d=(b>0)?(w-b)/b*100:0;
  printf "m%-6s base=%.3f win=%.3f  total-delta=%+.2f%%  %s\n",$1,b,w,d,(d>=1.0?"** CONFIRMED":"within-noise")}' \
  "$AR/ab_sol_raw.txt" >> "$AR/ab_sol.txt"
echo "AB-SOL-DONE $(date '+%T')" >> "$AR/ab_sol.txt"
cat "$AR/ab_sol.txt"

cd /c/Users/jeff/Documents/hashcat
AR=/c/Users/jeff/Documents/autoresearch
m(){ uv run "$AR/ar.py" measure -m "$1" 2>/dev/null | grep -oE 'primary_mhs=[^ ]+' | cut -d= -f2; }
: > "$AR/ab_all_raw.txt"
# interleaved master/win x2 to average out GPU drift (the thing that faked 110/2600)
for M in 10500 6221 9700 9800 9200 3000 18200 17300 17500 17700 17900 18000; do
  git checkout -q master 2>/dev/null;               b1=$(m $M)
  git checkout -q autoresearch/$M-jul6 2>/dev/null;  w1=$(m $M)
  git checkout -q master 2>/dev/null;               b2=$(m $M)
  git checkout -q autoresearch/$M-jul6 2>/dev/null;  w2=$(m $M)
  echo "$M $b1 $w1 $b2 $w2" | tee -a "$AR/ab_all_raw.txt"
done
git checkout -q master 2>/dev/null
echo "=== SUMMARY (avg of 2 interleaved A/B) ===" > "$AR/ab_all.txt"
awk '{b=($2+$4)/2; w=($3+$5)/2; d=(b>0)?(w-b)/b*100:0;
  printf "m%-6s base=%.4f win=%.4f  delta=%+.2f%%  %s\n",$1,b,w,d,(d>=1.0?"** CONFIRMED":(d<=-1.0?"REGRESSION":"within-noise"))}' \
  "$AR/ab_all_raw.txt" >> "$AR/ab_all.txt"
echo "AB-ALL-DONE $(date '+%T')" >> "$AR/ab_all.txt"

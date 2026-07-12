#!/bin/bash
# Detached wrap-up: interleaved re-A/B of every survey candidate (drift-free, main repo), then fold the
# verified survivors into README.md and commit + push. Self-contained so it finishes after the host leaves.
HC=/c/Users/jeff/Documents/hashcat; AR=/c/Users/jeff/Documents/autoresearch
PY=$(command -v python || echo /c/Python311/python)
cd "$HC" || exit 1
nvidia-smi -i 0 -lgc 1710,1710 >/dev/null 2>&1
: > "$AR/survey_verify.txt"
while read -r M; do
  [ -n "$M" ] || continue
  if ! git checkout -q "autoresearch/$M-survey" 2>/dev/null; then
    printf '%s\tNOBRANCH\t-\n' "$M" >> "$AR/survey_verify.txt"; continue
  fi
  r=$(uv run "$AR/ar.py" measure -m "$M" --ab --hashcat-dir "$HC" --bench-dir "$HC" 2>/dev/null | grep '^RESULT')
  d=$(echo "$r" | grep -oE 'delta_pct=[^ ]+' | cut -d= -f2)
  st=$(echo "$r" | grep -oE 'selftest=[^ ]+' | cut -d= -f2)
  printf '%s\t%s\t%s\n' "$M" "${d:-ERR}" "${st:-ERR}" >> "$AR/survey_verify.txt"
  echo "[$(date '+%T')] m$M verified delta_pct=${d:-ERR} selftest=${st:-ERR}"
done < "$AR/cand_modes.txt"
git checkout -q master 2>/dev/null
nvidia-smi -i 0 -rgc >/dev/null 2>&1
"$PY" "$AR/survey_readme.py"
cd "$AR"
git add README.md survey_verify.txt survey_readme.py wrapup.sh results_*_survey.tsv 2>/dev/null
git commit -q -m "Survey wrap-up: interleaved re-A/B of $(wc -l < "$AR/cand_modes.txt") candidates; verified survivors in README

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git push origin HEAD 2>&1 | tail -2
echo "WRAPUP-DONE $(date '+%F %T')"

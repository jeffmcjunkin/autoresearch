#!/bin/bash
# ==========================================================================================
# Autoresearch driver: for each target hash mode, run ROUNDS fresh `claude -p` invocations,
# each doing ONE experiment per program.md. Sequential (single GPU). Per-mode results_<M>.tsv.
# Launched as a detached script; it (not the human) invokes claude -p. Uses the claude.ai
# subscription (ANTHROPIC_API_KEY is unset per-invocation so the claude.ai login takes over).
# ==========================================================================================
set -u
AR=/c/Users/jeff/Documents/autoresearch
HC=/c/Users/jeff/Documents/hashcat
ROUNDS="${ROUNDS:-30}"
RTIMEOUT="${RTIMEOUT:-1200}"          # seconds per round
CLK=1710
LOG="$AR/drive.log"
mkdir -p "$AR/logs"

# 12 targets (ranked; Tier A table/mem-bound, B modeled, C likely-roofline-confirm)
MODES="${MODES:-11700 11800 6900 6100 31100 17400 17800 600 1700 10800 6000 17600}"

# per-mode baseline branch (default master=stock; 6100 extends the landed Whirlpool win)
baseline_for () { case "$1" in 6100) echo "perf-whirlpool-single-table";; *) echo "master";; esac; }

say () { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# strip Claude Code guard vars so `claude -p` runs as a fresh top-level agent
run_claude () { env -u ANTHROPIC_API_KEY -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u CLAUDE_CODE_CHILD_SESSION \
                    -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_EXECPATH \
                    timeout "$RTIMEOUT" claude -p "$1" --dangerously-skip-permissions --add-dir "$HC" < /dev/null; }

nvidia-smi -i 0 -lgc ${CLK},${CLK} >/dev/null 2>&1
say "=== driver start: modes=[$MODES] rounds=$ROUNDS timeout=${RTIMEOUT}s clock=${CLK} ==="

for M in $MODES; do
  BR="autoresearch/${M}-jul6"; BASE=$(baseline_for "$M"); RF="$AR/results_${M}.tsv"
  # clean current tree, create/checkout this mode's branch
  git -C "$HC" reset --hard HEAD -q 2>/dev/null; git -C "$HC" clean -fdq OpenCL/ 2>/dev/null
  git -C "$HC" show-ref --verify --quiet "refs/heads/$BR" || git -C "$HC" branch "$BR" "$BASE" 2>/dev/null
  git -C "$HC" checkout -q "$BR" 2>/dev/null || { say "m$M: cannot checkout $BR — skip"; continue; }

  # baseline row
  if [ ! -f "$RF" ]; then
    printf 'commit\tprimary_mhs\tsecond_mhs\tselftest\tstatus\tdescription\n' > "$RF"
    R=$(cd "$HC" && PRIMARY_MODE=$M bash "$AR/measure.sh" 2>/dev/null | grep '^RESULT')
    pm=$(echo "$R" | grep -oE 'primary_mhs=[0-9.]+|primary_mhs=FAIL' | cut -d= -f2)
    st=$(echo "$R" | grep -oE 'selftest=[^ ]+' | cut -d= -f2)
    printf '%s\t%s\tNA\t%s\tkeep\tbaseline (%s)\n' "$(git -C "$HC" rev-parse --short HEAD)" "${pm:-FAIL}" "${st:-FAIL}" "$BASE" >> "$RF"
    say "m$M: baseline primary_mhs=${pm:-FAIL} selftest=${st:-FAIL} (base=$BASE)"
  fi

  PROMPT="You are ONE round of autonomous hashcat GPU-kernel autoresearch. Read $AR/program.md and follow it EXACTLY. TARGET_MODE=$M. hashcat repo: $HC on branch $BR (already checked out, tree clean). Your experiment log: $AR/results_${M}.tsv (read it first for prior experiments and the current best primary_mhs; never repeat a tried idea). Do EXACTLY ONE experiment: pick one untried idea, edit that mode's kernel(s) in $HC (find them with grep), commit in $HC, run 'PRIMARY_MODE=$M bash $AR/measure.sh 2>/dev/null | grep RESULT', decide keep/discard by the ~1-2% noise band with selftest MUST be PASS, append exactly ONE tab-separated row (commit, primary_mhs, second_mhs, selftest, status, description) to $AR/results_${M}.tsv, and 'git -C $HC reset --hard HEAD~1' if you discard/it-was-wrong. Then STOP. One experiment only. Do NOT spawn subagents, do NOT run parallel GPU commands, do NOT change the GPU clock, do NOT edit measure.sh or program.md."

  existing=$(( $(wc -l < "$RF" 2>/dev/null || echo 2) - 2 )); [ "$existing" -lt 0 ] && existing=0   # experiments so far (minus header + baseline)
  remaining=$(( ROUNDS - existing )); [ "$remaining" -lt 0 ] && remaining=0                          # ROUNDS is a TARGET TOTAL
  say "m$M: $existing experiments logged, doing $remaining more to reach target $ROUNDS"
  for k in $(seq 1 "$remaining"); do
    n=$(( existing + k ))
    git -C "$HC" reset --hard HEAD -q 2>/dev/null; git -C "$HC" clean -fdq OpenCL/ 2>/dev/null   # drop any crashed-round leftovers (HEAD = last kept)
    rlog="$AR/logs/m${M}_r${n}.log"
    say "m$M round $n/$ROUNDS -> $rlog"
    run_claude "$PROMPT" > "$rlog" 2>&1
    rc=$?
    tail_last=$(tail -n 1 "$RF" 2>/dev/null | cut -f2,5,6 | tr '\t' ' ')
    say "m$M round $n done (rc=$rc); last log row: $tail_last"
  done
  best=$(awk -F'\t' 'NR>1 && $5=="keep"{print $2}' "$RF" | sort -n | tail -1)
  say "=== m$M complete: best kept primary_mhs=$best ==="
done

nvidia-smi -i 0 -rgc >/dev/null 2>&1
say "=== driver done ==="

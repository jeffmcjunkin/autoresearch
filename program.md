# autoresearch — hashcat GPU kernels

An adaptation of karpathy/autoresearch's autonomous-experiment loop to hashcat OpenCL kernel
optimization. Instead of editing `train.py` to lower `val_bpb`, you edit a hash mode's kernels to
**raise H/s** without breaking correctness. This file is the method; a driver (`drive.py`) invokes a
fresh headless agent (`codex exec` or `claude -p`) for each round, so **each invocation does EXACTLY
ONE experiment, then stops.**
(The original LLM-training program.md is in git history; the README documents that demo.)

## Per-round inputs (passed by the driver)
- `TARGET_MODE` — the hashcat `-m` number you are optimizing this run.
- hashcat repo at `$HASHCAT_DIR` (default `/c/Users/jeff/Documents/hashcat`) on branch
  `autoresearch/<TARGET_MODE>-jul6`. You edit kernels THERE and commit THERE.
- `results_<TARGET_MODE>.tsv` in THIS repo — the experiment log. **Read it first**: it holds every
  prior experiment (what was tried, keep/discard) and the current best `primary_mhs`. Do not repeat
  a tried idea.

## Parallel runs (shared GPU)
When multiple loops run at once, the GPU is shared. The metric harness serializes itself via a mutex, but
any DIRECT GPU command you run (ncu, `./hashcat.exe -b`) MUST go through the wrapper: `uv run <AR>/ar.py gpu -- <cmd>`
— otherwise it can corrupt another loop's benchmark. Pass `--hashcat-dir <your worktree>` to the harness.
Never run a raw GPU command in a parallel run.

## The metric (READ-ONLY harness — never modify `ar.py` / `measure.sh`)
`uv run <AR>/ar.py measure -m <TARGET_MODE> --ab` runs an **interleaved A/B**: it benchmarks your
candidate (HEAD) against the prior best (HEAD~1) **back-to-back in the main repo**, and prints a
`RESULT` line with a drift-free `delta_pct`. It locks the clock (1710 MHz) and **clears the NVRTC
kernel cache** each measure (hashcat does NOT invalidate cache on `#included`-header edits — measuring
a header edit without this silently shows NO change). **`selftest` MUST be `PASS`** — a faster-but-wrong
kernel is a failure, not a win. The measured noise floor is ~0.1% (2σ), so the driver keeps at
**delta_pct ≥ +0.3%** — do NOT use the old ~1–2% band; it discards real small wins. (Verify a claimed
win's correctness independently with `-a 3` on the mode's a3 kernel — `-a 0` runs the unchanged a0 kernel.)

## Correctness is a HARD gate (the key difference from LLM autoresearch)
A wrong kernel silently cracks nothing; the metric alone won't catch it. `selftest=PASS` (the mode's
built-in known-vector crack, run by the benchmark) is mandatory every round. Prefer value-identical
changes (removing a provably-redundant op, algebraic identities on disjoint bit-fields) — they can't
change results. Algorithmic changes (restructuring a transform, table tricks) are higher-risk: reason
carefully about correctness and rely on the self-test.

## Find the bottleneck, then pick a lever
Profile once with `ncu` if unsure (see recipe below). Match the lever to the bottleneck:
- **Latency-bound, shared-memory (RC4-like: low ALU%, IPC ~1.5, occupancy capped by per-thread state):**
  shorten the data-dependent address/dependency chain; cut shared-mem ops. *Worked win:* RC4 `KEY8`
  rewrote a `+`-composition of disjoint bit-fields as `|` so the base folds into one LOP3 (+4.6%).
  *Non-win:* eliminating a "redundant" shared load — ptxas already CSEs it. Unrolling latency-bound
  loops usually REGRESSES (register/I-cache pressure).
- **Table-based (Whirlpool/Streebog/GOST: lookup tables in shared/constant mem, memory/LSU-bound):**
  shrink the shared-memory table footprint to raise occupancy. *Worked win:* Whirlpool's 8 tables are
  rotations of one (`MTk[x]==ROTR64(MT0[x],8k)`) — store only MT0 (2KB vs 16KB), derive the rest via
  rotate; freed occupancy → +7%. Look for the same algebraic table structure in Streebog/GOST.
- **Register-pressure / 64-bit-word (SHA-512/BLAKE2b/Keccak: 236-255 regs, ~16% occupancy):** often
  already at roofline at the AUTOTUNED vector width (my forced-vec8 survey over-stated headroom here).
  Reducing registers to lift occupancy usually nets ~0 on these latency-bound ARX chains — verify with
  ncu at the real config before spending rounds.
- **Instruction selection:** verify each step lowers to minimal fused ops (LOP3/IADD3/SHF), no stray
  MOV/IMAD in the hot loop (`cuobjdump -sass kernels/<cached file>`).
- Do NOT chase the 32-bit MD/SHA1/SHA2-256/NTLM family — proven at roofline.

`ncu` recipe (full-launch, avoids autotune micro-probes): get the mode's example hash via
`./hashcat.exe -m <M> --example-hashes --machine-readable --backend-ignore-cuda --backend-ignore-opencl --backend-ignore-hip --quiet`,
then `ncu --launch-skip 3 --launch-count 1 --kernel-name regex:m<M>_s --section SpeedOfLight --section Occupancy --section ComputeWorkloadAnalysis ./hashcat.exe -m <M> -a 3 hf ?b?b?b?b?b?b?b -d1 -D2 --self-test-disable --backend-vector-width 8 -n 64 -u 1024 -T 256 --force --runtime 10 --potfile-disable`.

## The one round you run this invocation
1. `cd $HASHCAT_DIR`; confirm on branch `autoresearch/<TARGET_MODE>-jul6`, tree clean. Read
   `results_<TARGET_MODE>.tsv` for prior experiments + current best.
2. Pick ONE untried idea (grep the mode's kernels; find the shared hash header via `grep -rl`).
3. Edit the kernel(s); `git -C $HASHCAT_DIR commit -am "<desc>"`.
4. `uv run <AR>/ar.py measure -m <TARGET_MODE> --ab` and read its `RESULT` line (`delta_pct` = drift-free gain vs prior best).
5. Decide and log ONE row to `results_<TARGET_MODE>.tsv` (TAB-separated):
   `commit<TAB>primary_mhs<TAB>second_mhs<TAB>selftest<TAB>status<TAB>description`
   - RESULT missing or `selftest=FAIL` → `crash`/`wrong`: `git -C $HASHCAT_DIR reset --hard HEAD~1`.
   - `delta_pct ≥ +0.3` AND `selftest=PASS` → `keep` (leave the commit).
   - else (equal/worse) → `discard`: `git -C $HASHCAT_DIR reset --hard HEAD~1`.
6. **STOP.** Do not loop, do not spawn subagents, do not run parallel GPU commands (single GPU;
   the clock is held externally — do not touch it). The driver starts the next round.
   If you conclude the mode is at roofline (ncu ≥~95% of achievable pipe, minimal instructions,
   several principled discards), still log a row saying so and stop.

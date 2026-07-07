# autoresearch — hashcat RC4 kernels

An adaptation of karpathy/autoresearch's autonomous-experiment loop to GPU kernel optimization.
Instead of editing `train.py` to lower `val_bpb`, you edit hashcat's RC4 OpenCL kernels to **raise
H/s** on the RC4-based hash modes, without breaking correctness. RC4 is shared by ~18 modes
(Kerberos etype23 13100/18200/7500, MS Office 9700/9800/..., PDF 10400/10500/25400, ...), so a win
in the shared helper lifts all of them. (The original LLM-training program.md is preserved in git
history; the README documents that demo.)

## The two repos
- **This repo (the research org):** `program.md` (these instructions), `measure.sh` (READ-ONLY eval
  harness — the ground-truth metric), `results.tsv` (experiment log), `run.log` (last eval output).
- **hashcat (the code under test):** `$HASHCAT_DIR` (default `/c/Users/jeff/Documents/hashcat`), on
  branch `autoresearch/rc4-jul6`, based on the already-landed KEY8 win (PR #4712). You edit kernels
  THERE and commit THERE; you log results HERE.

## Setup (once)
1. Confirm hashcat is on branch `autoresearch/rc4-jul6` with a clean tree, KEY8 `|`-form present in
   `OpenCL/inc_cipher_rc4.cl`.
2. Run `bash measure.sh > run.log 2>&1` to establish the **baseline** metric; record it as the first
   `results.tsv` row (status `keep`, description `baseline (KEY8)`).

## What you edit
- `OpenCL/inc_cipher_rc4.cl` — the shared RC4 helper (KSA `rc4_init_*`, PRGA `rc4_next`, `rc4_swap`,
  the `KEY8`/`KEY32` shared-memory S-box addressing). **This is the highest-leverage file** (affects
  all RC4 modes). Its `IS_CPU` branch is a separate simple path — keep it correct but it's not the GPU target.
- Optionally the per-mode `OpenCL/mNNNNN_a3-{optimized,pure}.cl` if a win is mode-specific.
- NOT `measure.sh`, NOT the hashcat test harness (`tools/test.pl`, `tools/test_modules/*.pm`) — those
  are ground truth.

## The metric (READ-ONLY harness — do not modify `measure.sh`)
`bash measure.sh > run.log 2>&1` then `grep '^RESULT' run.log`. It:
- locks the GPU clock to 1710 MHz (thermal drift is bigger than any real win),
- **clears the NVRTC kernel cache per mode** — hashcat does NOT invalidate its cache when an
  `#included` header changes, so a header edit measured without a cache clear silently shows NO change
  (this exact trap produced a false "no win" during the KEY8 work),
- benchmarks median-of-3 (warm-up discarded) for the primary mode (13100) and a second mode (9700,
  a different `rc4_init` variant), and
- runs a correctness self-test across the shared-helper blast radius (18200/7500/9800).
Metric = `primary_mhs` (higher is better). **`selftest` MUST be `PASS`** — a faster-but-wrong kernel
is a failure, not a win. Noise band is ~1–2%; only keep deltas beyond it.

## Correctness is a HARD gate (the key difference from LLM autoresearch)
A wrong kernel silently cracks nothing — the metric alone will not catch it. So:
- Every experiment: `selftest=PASS` in the RESULT line is mandatory.
- Before you `keep` (commit + advance), run the FULL functional sweep for a candidate win (independent
  `test.pl`/`.pm` reference hashes, `-a 3`, vector widths 1/2/4/8, pure+optimized). It must be all-pass.
  Value-identical changes (e.g. removing a provably-redundant load) are low-risk; algorithmic changes
  need the full sweep.

## RC4 optimization levers (priors — don't rediscover these)
The RC4 KSA/PRGA is **latency-bound** on the shared-memory S-box (ncu on 13100: ~69% compute, ALU pipe
~49%, IPC ~1.5, ~21% occupancy, stalls split ~ execution-dependency + MIO/shared-scoreboard). Occupancy
is capped by the 256-byte S-box/thread (8 KB/warp), so raising occupancy is NOT available. The lever is
**cutting shared-memory ops / shortening the dependency chain**:
- **Redundant S-box loads.** In `rc4_init_*`, `j += GET_KEY8(S,i)+d; rc4_swap(S,i,j)` — but `rc4_swap`
  re-reads `S[i]` that was just read. Same pattern in `rc4_next` (`b += GET_KEY8(S,a); rc4_swap(S,a,b)`).
  Passing the already-loaded value into the swap removes one `LDS` per iteration (256 in the KSA). Provably
  value-identical (nothing writes `S[i]` between the two reads).
- **KEY8 addressing** (already optimized — the landed win). Don't re-do it.
- **Instruction selection / IADD3 fusion** on the `j`/`b` accumulator chain.
- **Unroll** (`_unroll` is off by default). Historically neutral-to-negative on latency-bound kernels
  (register/I-cache cost) — measure, don't assume.
- **Invariant precompute**: confirm nothing constant is recomputed in the inner loop.
Do NOT chase the 32-bit MD/SHA/NTLM family — the survey proved it's already at the roofline.

## Output / logging
`results.tsv` (TAB-separated), header + columns:
```
commit	primary_mhs	second_mhs	selftest	status	description
```
- `commit` = short hash of the hashcat commit for this experiment
- `primary_mhs` / `second_mhs` from the RESULT line (0 for crash/wrong)
- `selftest` = PASS / FAIL:<mode>
- `status` = `keep` | `discard` | `wrong` | `crash`
- `description` = what the experiment tried
Do NOT commit `results.tsv` or `run.log` in the hashcat repo; log them here in the research repo.

## The loop (never stop once started)
LOOP:
1. Note the hashcat branch/commit.
2. Edit a kernel in `$HASHCAT_DIR` with one experimental idea.
3. `git -C $HASHCAT_DIR commit -am "<desc>"`.
4. `bash measure.sh > run.log 2>&1`; `grep '^RESULT' run.log`.
5. If RESULT missing or `selftest=FAIL`: it's `wrong`/`crash` — log it, `git -C $HASHCAT_DIR reset --hard HEAD~1`.
6. If `primary_mhs` improved beyond the ~1–2% noise band AND `selftest=PASS`: run the full sweep; if it
   passes, `keep` (advance — leave the commit); log it.
7. Else (equal/worse/failed-sweep): `discard` — `git -C $HASHCAT_DIR reset --hard HEAD~1`; log it.
8. Repeat. If you run out of ideas, profile with `ncu` to re-read the bottleneck, combine near-misses,
   or move the primary metric to another RC4 mode. **Stopping rule:** if `ncu` shows the KSA/PRGA at
   ≥~95% of its achievable pipe with minimal instruction count, declare RC4 at roofline and report.

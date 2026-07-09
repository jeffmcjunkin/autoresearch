#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# ==========================================================================================
# ar.py — hashcat-kernel autoresearch, one OS-agnostic Python CLI (replaces the *.sh scripts).
# Pure stdlib; run via `uv run ar.py <cmd> ...`. External processes it drives: hashcat / nvidia-smi
# / ncu (the GPU work), git (VCS), codex|claude (the agent) — inherent, not portable.
#
# Subcommands:
#   measure   READ-ONLY metric harness: GPU-mutex + median-of-3 + selftest -> a RESULT line.  [agent + driver]
#   gpu       run one command under the shared GPU mutex (agent's ad-hoc ncu / hashcat -b).    [agent]
#   drive     per-mode round loop: N fresh agent invocations, each ONE experiment per program.md.
#   parallel  bring up one worktree + driver per mode (GPU serialized by the mutex).
#   batches   run every numeric batch in targets.tsv, 5-way parallel each, resumable.
#   readme    regenerate README.md from results_<M>.tsv + branches + targets.tsv.
#   validate  plumbing smoke test for the selected engine.
#
# The metric harness is GROUND TRUTH — the agent MUST NOT edit ar.py.
# ==========================================================================================
import argparse, csv, datetime, glob, os, shutil, subprocess, sys, time

AR   = os.path.dirname(os.path.abspath(__file__))
AR_F = AR.replace("\\", "/")
ARPY = os.path.abspath(__file__).replace("\\", "/")
CLK  = 1710
MODEL, EFFORT = "gpt-5.5", "xhigh"          # hard-coded per request
DEFAULT_MODES = "11700 11800 6900 6100 31100 17400 17800 600 1700 10800 6000 17600"

def env(k, d=None): return os.environ.get(k, d)
def HC_default():   return env("HASHCAT_DIR", "C:/Users/jeff/Documents/hashcat").replace("\\", "/")
def LOCK_default(): return env("GPU_LOCK", AR_F + "/.gpu.lock").replace("\\", "/")

def nw():
    """Windows: launch the child with NO console window (CREATE_NO_WINDOW + SW_HIDE). Fresh
    STARTUPINFO per call (subprocess mutates it). No-op off Windows."""
    if os.name != "nt": return {}
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0                       # SW_HIDE
    return {"creationflags": 0x08000000, "startupinfo": si}   # CREATE_NO_WINDOW

# ---- tool resolution -------------------------------------------------------------------
def which_or(name, *fallbacks):
    p = shutil.which(name)
    if p: return p
    for f in fallbacks:
        if os.path.exists(f): return f
    return None

def need(name, *fallbacks):
    p = which_or(name, *fallbacks)
    if not p: sys.exit(f"ar.py: required tool '{name}' not found")
    return p

def resolve_uv():
    return need("uv", os.path.expanduser("~/.local/bin/uv.exe"), os.path.expanduser("~/.local/bin/uv")).replace("\\", "/")

def resolve_gitbash():
    """Git-for-Windows bash (never System32 WSL bash). Only used to keep the agent's env sane; ar.py
    itself needs no bash."""
    b = env("BASH_BIN")
    if b and os.path.exists(b): return b
    if os.name != "nt": return which_or("bash")
    roots = []
    g = shutil.which("git")
    if g:
        d = os.path.dirname(g); roots += [os.path.dirname(d), os.path.dirname(os.path.dirname(d))]
    roots += [r"C:\Program Files\Git", r"C:\Program Files (x86)\Git"]
    for r in roots:
        for c in (os.path.join(r, "bin", "bash.exe"), os.path.join(r, "usr", "bin", "bash.exe")):
            if os.path.exists(c): return c
    w = shutil.which("bash")
    return w if (w and "ystem32" not in w) else None

def codex_launcher():
    """[node, codex.js] — matches the npm shim; node.exe is a real PE so no shell/escaping needed."""
    js = env("CODEX_JS")
    if not js:
        c = shutil.which("codex")
        if c: js = os.path.join(os.path.dirname(c), "node_modules", "@openai", "codex", "bin", "codex.js")
    node = shutil.which("node")
    if js and os.path.exists(js) and node: return [node, js]
    c = shutil.which("codex")
    if c and os.name != "nt": return [c]
    sys.exit("ar.py: cannot locate codex (set CODEX_JS)")

# ---- logging ---------------------------------------------------------------------------
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def say(msg, logfile=None):
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    if logfile:
        try:
            with open(logfile, "a", encoding="utf-8", newline="\n") as f: f.write(line + "\n")
        except OSError: pass

# ---- GPU mutex (byte-compatible with the bash mkdir mutex; safe to mix during migration) ----
def gpu_lock(lock):
    w = 0
    while True:
        try:
            os.mkdir(lock); break
        except FileExistsError:
            ts = os.path.join(lock, "ts")
            try:
                if os.path.exists(ts) and time.time() - int(open(ts).read() or 0) > 1200:
                    shutil.rmtree(lock, ignore_errors=True); continue
            except (OSError, ValueError): pass
            time.sleep(1); w += 1
            if w > 900: break
    try:
        with open(os.path.join(lock, "ts"), "w") as f: f.write(str(int(time.time())))
    except OSError: pass

def gpu_unlock(lock):
    shutil.rmtree(lock, ignore_errors=True)

def set_clock(lock_on):
    try:
        subprocess.run(["nvidia-smi", "-i", "0"] + (["-lgc", f"{CLK},{CLK}"] if lock_on else ["-rgc"]),
                       capture_output=True, **nw())
    except FileNotFoundError: pass

# ---- the metric (port of measure.sh) ---------------------------------------------------
def _clear_cache(hc, mode):
    pad = f"m{mode:05d}"
    for pat in (f"kernels/{pad}_a*.kernel", f"kernels/{pad}-*.kernel"):
        for f in glob.glob(os.path.join(hc, pat)):
            try: os.remove(f)
            except OSError: pass

def _median3(hc, mode):
    _clear_cache(hc, mode)
    vals = []
    for _ in range(4):                      # 4 runs, warm-up (first) discarded
        try:
            r = subprocess.run([os.path.join(hc, "hashcat.exe"), "-b", "-m", str(mode),
                                "-d", "1", "-D", "2", "--machine-readable", "--quiet"],
                               cwd=hc, capture_output=True, text=True, timeout=240, **nw())
        except subprocess.TimeoutExpired:
            continue
        for ln in r.stdout.splitlines():
            if ln.startswith(f"1:{mode}:"):
                parts = ln.split(":")
                if len(parts) >= 6 and parts[5].isdigit(): vals.append(int(parts[5]))
                break
    if len(vals) < 2: return None
    rest = sorted(vals[1:]); n = len(rest)
    return rest[(n + 1) // 2 - 1]            # median, 1-indexed (n+1)//2 as in measure.sh

def _selftest_ok(hc, mode):
    _clear_cache(hc, mode)
    try:
        r = subprocess.run([os.path.join(hc, "hashcat.exe"), "-b", "-m", str(mode), "-d", "1", "-D", "2"],
                           cwd=hc, capture_output=True, text=True, timeout=240, **nw())
    except subprocess.TimeoutExpired:
        return False
    out = (r.stdout or "") + (r.stderr or "")
    low = out.lower()
    if "self-test failed" in low or "aborting" in low: return False
    return "Speed" in out

def _fmt_mhs(v):
    """MH/s string that preserves precision for slow modes — sub-MH/s never rounds to 0.0 (which
    made VeraCrypt/scrypt/LUKS/KDF unmeasurable). Down to ~1 H/s stays distinguishable."""
    if not isinstance(v, int): return "FAIL"
    m = v / 1e6
    if m >= 100: return f"{m:.1f}"
    if m >= 1:   return f"{m:.3f}"
    if m > 0:    return f"{m:.6f}"
    return "0.0"

def do_measure(mode, second=None, selftest_modes=(), lock=None, hc=None):
    """Returns dict(primary, primary_mhs, second_mhs, selftest, clock). Serialized on the GPU mutex."""
    hc = hc or HC_default(); lock = lock or LOCK_default()
    set_clock(True)
    gpu_lock(lock)
    try:
        praw = _median3(hc, mode)
        st = "PASS" if praw is not None else f"FAIL:{mode}"
        sout = "NA"
        if second:
            sraw = _median3(hc, second)
            if sraw is None: st = f"FAIL:{second}"
            sout = _fmt_mhs(sraw)
        for m in selftest_modes:
            if not _selftest_ok(hc, int(m)): st = f"FAIL:{m}"
    finally:
        gpu_unlock(lock)
    return dict(primary=mode, primary_mhs=_fmt_mhs(praw), second_mhs=sout, selftest=st, clock=CLK)

def result_line(d):
    return (f"RESULT primary={d['primary']} primary_mhs={d['primary_mhs']} "
            f"second_mhs={d['second_mhs']} selftest={d['selftest']} clock={d['clock']}")

# ---- git / tsv helpers -----------------------------------------------------------------
def git(hc, *args):
    return subprocess.run([need("git"), "-C", hc, *args], capture_output=True, text=True, **nw())

def results_path(mode, tag):
    return os.path.join(AR, f"results_{mode}.tsv" if tag == "jul6" else f"results_{mode}_{tag}.tsv")

def baseline_branch(mode):
    return "perf-whirlpool-single-table" if str(mode) == "6100" else "master"

# ---- the round prompt (agent-facing; NO bash — uses `uv run ar.py`) --------------------
def build_prompt(M, hc, br, rf_f, lock):
    uv = resolve_uv()
    measure_cmd = f"{uv} run {ARPY} measure --mode {M} --hashcat-dir {hc} --gpu-lock {lock}"
    gpu_cmd     = f"{uv} run {ARPY} gpu --gpu-lock {lock} -- <your GPU command>"
    return (
        f"You are ONE round of autonomous hashcat GPU-kernel autoresearch. Read {AR_F}/program.md and "
        f"follow it EXACTLY. TARGET_MODE={M}. hashcat repo: {hc} on branch {br} (already checked out, tree "
        f"clean) — edit kernels and commit THERE. Your experiment log: {rf_f} (read it FIRST for prior "
        f"experiments and the current best primary_mhs; never repeat a tried idea). Do EXACTLY ONE "
        f"experiment: pick one untried idea, find that mode's kernel(s) with grep and edit them in {hc}, "
        f"'git -C {hc} commit -am <desc>', then BENCHMARK by running EXACTLY this command (it locks the GPU "
        f"internally and prints a RESULT line):\n    {measure_cmd}\n"
        f"Read its RESULT line. Decide keep/discard by the ~1-2% noise band with selftest MUST be PASS. "
        f"Append EXACTLY ONE tab-separated row (commit<TAB>primary_mhs<TAB>second_mhs<TAB>selftest<TAB>status"
        f"<TAB>description) to {rf_f}; if you discard or it was wrong/crashed, also "
        f"'git -C {hc} reset --hard HEAD~1'. Then STOP — one experiment only, do NOT spawn subagents. Any "
        f"DIRECT GPU command (ncu, ./hashcat.exe -b) MUST be serialized via the mutex — run it as:\n    "
        f"{gpu_cmd}\nnever run a raw GPU command. Do NOT change the GPU clock, do NOT edit measure.sh, "
        f"ar.py, or program.md."
    )

def run_agent(prompt, rlog, engine, hc, rtimeout):
    e = os.environ.copy()
    gb = resolve_gitbash()
    prepend = os.pathsep.join([p for p in (os.path.dirname(resolve_uv()),
                                           os.path.dirname(gb) if gb else None) if p])
    e["PATH"] = prepend + os.pathsep + e.get("PATH", "")     # agent finds uv (+ git-bash) first
    if engine == "codex":
        argv = codex_launcher() + ["exec", prompt, "-m", MODEL, "-c", f"model_reasoning_effort={EFFORT}",
                                   "--dangerously-bypass-approvals-and-sandbox", "-C", hc]
    elif engine == "claude":
        argv = [need("claude"), "-p", prompt, "--dangerously-skip-permissions", "--add-dir", hc]
        for k in ("ANTHROPIC_API_KEY", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION",
                  "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_EXECPATH"):
            e.pop(k, None)
    else:
        sys.exit(f"ar.py: unknown engine {engine}")
    with open(rlog, "w", encoding="utf-8", errors="replace") as out:
        try:
            return subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                  timeout=rtimeout, cwd=hc, env=e, **nw()).returncode
        except subprocess.TimeoutExpired:
            out.write(f"\n[ar.py] TIMEOUT after {rtimeout}s\n"); return 124

# ========================================================================================
# subcommands
# ========================================================================================
def cmd_measure(a):
    d = do_measure(a.mode, a.second, (a.selftest.split() if a.selftest else ()),
                   lock=a.gpu_lock, hc=a.hashcat_dir)
    print(result_line(d))

def cmd_gpu(a):
    if not a.command: sys.exit("ar.py gpu: nothing after --")
    gpu_lock(a.gpu_lock)
    try:
        rc = subprocess.run(a.command, cwd=a.hashcat_dir, **nw()).returncode
    finally:
        gpu_unlock(a.gpu_lock)
    sys.exit(rc)

def cmd_drive(a):
    hc, lock, tag = a.hashcat_dir, a.gpu_lock, a.run_tag
    modes = a.modes.split()
    os.makedirs(os.path.join(AR, "logs"), exist_ok=True)
    drive_log = os.path.join(AR, "drive.log")
    set_clock(True)
    say(f"=== driver start: engine={a.engine} model={MODEL}/{EFFORT} modes=[{' '.join(modes)}] "
        f"rounds={a.rounds} timeout={a.rtimeout}s tag={tag} ===", drive_log)
    for M in modes:
        Mi = int(M); br = f"autoresearch/{M}-{tag}"; base = baseline_branch(M)
        rf = results_path(M, tag); rf_f = rf.replace("\\", "/")
        git(hc, "reset", "--hard", "HEAD", "-q"); git(hc, "clean", "-fdq", "OpenCL/")
        if git(hc, "show-ref", "--verify", "--quiet", f"refs/heads/{br}").returncode != 0:
            git(hc, "branch", br, base)
        if git(hc, "checkout", "-q", br).returncode != 0:
            say(f"m{M}: cannot checkout {br} — skip", drive_log); continue
        if not os.path.exists(rf):
            with open(rf, "w", encoding="utf-8", newline="\n") as f:
                f.write("commit\tprimary_mhs\tsecond_mhs\tselftest\tstatus\tdescription\n")
            d = do_measure(Mi, lock=lock, hc=hc)
            head = git(hc, "rev-parse", "--short", "HEAD").stdout.strip()
            with open(rf, "a", encoding="utf-8", newline="\n") as f:
                f.write(f"{head}\t{d['primary_mhs']}\tNA\t{d['selftest']}\tkeep\tbaseline ({base})\n")
            say(f"m{M}: baseline primary_mhs={d['primary_mhs']} selftest={d['selftest']} (base={base})", drive_log)
        with open(rf, encoding="utf-8") as f:
            existing = max(0, sum(1 for _ in f) - 2)
        remaining = max(0, a.rounds - existing)
        say(f"m{M}: {existing} experiments logged, doing {remaining} more to reach target {a.rounds}", drive_log)
        prompt = build_prompt(M, hc, br, rf_f, lock)
        for k in range(1, remaining + 1):
            n = existing + k
            git(hc, "reset", "--hard", "HEAD", "-q"); git(hc, "clean", "-fdq", "OpenCL/")
            rlog = os.path.join(AR, "logs", f"m{M}_r{n}.log")
            say(f"m{M} round {n}/{a.rounds} -> {rlog}", drive_log)
            rc = run_agent(prompt, rlog, a.engine, hc, a.rtimeout)
            last = ""
            try:
                rows = [l for l in open(rf, encoding="utf-8").read().splitlines() if l.strip()]
                if rows:
                    c = rows[-1].split("\t"); last = " ".join(c[i] for i in (1, 4, 5) if i < len(c))
            except OSError: pass
            say(f"m{M} round {n} done (rc={rc}); last row: {last}", drive_log)
        best = None
        for l in open(rf, encoding="utf-8").read().splitlines()[1:]:
            c = l.split("\t")
            if len(c) > 4 and c[4] == "keep":
                try: v = float(c[1]); best = v if best is None else max(best, v)
                except ValueError: pass
        say(f"=== m{M} complete: best kept primary_mhs={best} ===", drive_log)
    set_clock(False)
    say("=== driver done ===", drive_log)

def cmd_parallel(a):
    hc, lock, tag = a.hashcat_dir, a.gpu_lock, a.run_tag
    modes = a.modes.split()
    os.makedirs(os.path.join(AR, "logs"), exist_ok=True)
    shutil.rmtree(lock, ignore_errors=True)
    set_clock(True)
    say(f"bringing up {len(modes)} loops: {' '.join(modes)}")
    for M in modes:
        wt = os.path.join(AR, f"wt_{M}"); br = f"autoresearch/{M}-{tag}"
        if git(hc, "show-ref", "--verify", "--quiet", f"refs/heads/{br}").returncode != 0:
            git(hc, "branch", br, baseline_branch(M))
        if not os.path.isdir(os.path.join(wt, "OpenCL")):
            if git(hc, "worktree", "add", "-q", wt, br).returncode != 0:
                say(f"  m{M}: worktree add failed"); continue
            shutil.copy(os.path.join(hc, "hashcat.exe"), wt)
            shutil.copytree(os.path.join(hc, "modules"), os.path.join(wt, "modules"), dirs_exist_ok=True)
        loop_log = os.path.join(AR, "logs", f"loop_{M}.out")
        argv = [resolve_uv(), "run", ARPY, "drive", "--modes", M, "--rounds", str(a.rounds),
                "--rtimeout", str(a.rtimeout), "--engine", a.engine, "--run-tag", tag,
                "--hashcat-dir", wt.replace("\\", "/"), "--gpu-lock", lock]
        with open(loop_log, "a", encoding="utf-8") as out:
            p = subprocess.Popen(argv, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 cwd=AR, **nw())
        ndll = len(glob.glob(os.path.join(wt, "modules", "*.dll")))
        say(f"  m{M} loop pid {p.pid} (worktree {wt}, {ndll} module dlls)")
        time.sleep(2)
    say("all loops launched. monitor: cat drive.log ; ls results_*.tsv")

def _read_targets(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
    batches = {}
    for r in rows:
        if r["batch"].isdigit(): batches.setdefault(int(r["batch"]), []).append(r["mode"])
    return batches

def _exp_count(mode, tag):
    f = results_path(mode, tag)
    if not os.path.exists(f): return 0
    return max(0, sum(1 for _ in open(f, encoding="utf-8")) - 2)

def _parse_batch_filter(s):
    if not s: return None
    out = []                                        # ordered: batches run in the order given
    for part in s.replace(" ", "").split(","):
        if "-" in part:
            lo, hi = part.split("-"); out += list(range(int(lo), int(hi) + 1))
        elif part:
            out.append(int(part))
    return out

def cmd_batches(a):
    hc = a.hashcat_dir
    targets = a.targets or os.path.join(AR, "targets.tsv")
    batches = _read_targets(targets)
    wanted = _parse_batch_filter(getattr(a, "batches", None))
    pause = getattr(a, "batch_pause", 0)
    set_clock(True)
    ran_prev = False
    for n in (wanted if wanted is not None else sorted(batches)):
        if n not in batches: continue
        modes = batches[n]
        if all(_exp_count(M, a.run_tag) >= a.rounds for M in modes):
            say(f"batch {n} already complete, skip"); continue
        if ran_prev and pause > 0:                      # pace the 5-hour usage window
            say(f"pausing {pause}s before batch {n} (usage-window pacing)")
            time.sleep(pause)
        say(f"=== BATCH {n} launch: {' '.join(modes)} ===")
        for M in modes:
            open(os.path.join(AR, "logs", f"loop_{M}.out"), "w").close()
        ns = argparse.Namespace(modes=" ".join(modes), rounds=a.rounds, rtimeout=a.rtimeout,
                                engine=a.engine, run_tag=a.run_tag, hashcat_dir=hc, gpu_lock=a.gpu_lock)
        os.makedirs(os.path.join(AR, "logs"), exist_ok=True)
        cmd_parallel(ns)
        waited = 0
        while waited < 21600:
            time.sleep(30); waited += 30
            done = sum(1 for M in modes
                       if os.path.exists(os.path.join(AR, "logs", f"loop_{M}.out"))
                       and f"=== m{M} complete" in open(os.path.join(AR, "logs", f"loop_{M}.out"),
                                                        encoding="utf-8", errors="replace").read())
            cmd_readme(argparse.Namespace())
            if done >= len(modes): break
        say(f"=== BATCH {n} done ===")
        for M in modes:
            git(hc, "worktree", "remove", "--force", os.path.join(AR, f"wt_{M}"))
        git(hc, "worktree", "prune"); cmd_readme(argparse.Namespace())
        ran_prev = True
    set_clock(False)
    say("=== ALL BATCHES COMPLETE ===")

VERIFIED = {"17400", "17600", "17800", "11700", "11800", "31100"}   # clean-GPU A/B + correctness
REJECTED = {"6100"}                                                 # win did not reproduce

def _readme_stats(mode):
    f = results_path(mode, "jul6")
    if not os.path.exists(f): return None
    rows = list(csv.reader(open(f, encoding="utf-8"), delimiter="\t"))[1:]
    if not rows: return None
    try:
        base = float(rows[0][1])
        if base == 0: return None                       # slow modes whose baseline rounds to 0.0 MH/s
        keeps = [float(r[1]) for r in rows[1:] if len(r) > 4 and r[4] == "keep"]
        best = max(keeps + [base])
        return dict(base=base, best=best, delta=(best - base) / base * 100, exps=len(rows) - 1)
    except (ValueError, IndexError, ZeroDivisionError):
        return None

def cmd_readme(a):
    hc = HC_default()
    def branch(m):
        ok = git(hc, "rev-parse", "--verify", "--quiet", f"autoresearch/{m}-jul6").returncode == 0
        return f"autoresearch/{m}-jul6" if ok else "-"
    def mhs(x):
        return f"{x/1e6:.1f}" if x >= 1e6 else (f"{x/1e3:.1f}k" if x >= 1e3 else f"{x:.1f}")
    tg = {r["mode"]: r for r in csv.DictReader(open(os.path.join(AR, "targets.tsv"), encoding="utf-8"), delimiter="\t")}
    rows = []
    for m, t in tg.items():
        s = _readme_stats(m); br = branch(m)
        if s is None:
            status = "pending" if t["batch"] in "1234" else "-"; delta = ""; bb = ""
        else:
            v = "✅" if m in VERIFIED else ("❌ rejected" if m in REJECTED else "")
            e = s["exps"]; newb = t["batch"].isdigit()
            if s["delta"] >= 1.0:
                status = (f'WIN +{s["delta"]:.1f}%' + (f" (partial {e}/6)" if newb and e < 6 else "") + f" {v}").strip()
            elif e == 0:  status = "NOT-RUN (spend-limit)"
            elif newb and e < 6: status = f"in-progress {e}/6"
            else: status = f"roofline {v}".strip()
            delta = f'+{s["delta"]:.1f}%' if s["delta"] >= 1.0 else ("—" if e == 0 else "~0%")
            bb = f'{mhs(s["base"])} → {mhs(s["best"])}'
        rows.append((t["batch"], m, t["name"], t["category"], delta, bb, status, br))
    order = {"PR": 0, "C": 1, "1": 2, "2": 3, "3": 4, "4": 5}
    rows.sort(key=lambda r: (order.get(r[0], 9),
                             -(float(r[4].rstrip("%").lstrip("+")) if r[4].startswith("+") else -1)))
    out = ["# hashcat kernel autoresearch — progress\n",
           "Autonomous agent optimization loops (`ar.py`, see `program.md`). Each win lives on branch "
           "`autoresearch/<mode>-jul6` in the hashcat repo; per-experiment logs are `results_<mode>.tsv`. "
           "Regenerate with `uv run ar.py readme`.\n",
           "Legend: ✅ = verified on clean-GPU A/B + correctness; ❌ = did not reproduce; batches C=first "
           "campaign, 1–4=current run.\n",
           "| Batch | Mode | Name | Category | Δ | MH/s (base→best) | Status | Branch |",
           "|---|---|---|---|---|---|---|---|"]
    for b, m, n, c, d, bb, st, br in rows:
        out.append(f"| {b} | {m} | {n} | {c} | {d} | {bb} | {st} | `{br}` |")
    nwin = sum(1 for r in rows if r[6].startswith("WIN"))
    out.append(f"\n**Totals:** {nwin} wins. Verified-real: {len(VERIFIED)}. Rejected: {len(REJECTED)}.")
    open(os.path.join(AR, "README.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"README.md regenerated: {len(rows)} modes, {nwin} wins")

def cmd_validate(a):
    tok = "PLUMBING_OK"
    prompt = f"Reply with exactly this token and nothing else: {tok}"
    rlog = os.path.join(AR, "logs", "validate.log")
    os.makedirs(os.path.dirname(rlog), exist_ok=True)
    rc = run_agent(prompt, rlog, a.engine, HC_default(), 120)
    out = open(rlog, encoding="utf-8", errors="replace").read()
    ok = tok in out
    print(f"[validate engine={a.engine}] {'OK' if ok else 'FAIL'} (rc={rc}) - see {rlog}")
    sys.exit(0 if ok else 1)

# ---- CLI -------------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(prog="ar.py", description="hashcat-kernel autoresearch CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure", help="GPU-mutex median-of-3 benchmark -> RESULT line")
    m.add_argument("-m", "--mode", type=int, required=True)
    m.add_argument("--second", type=int, default=None)
    m.add_argument("--selftest", default="")
    m.add_argument("--hashcat-dir", default=HC_default())
    m.add_argument("--gpu-lock", default=LOCK_default())
    m.set_defaults(fn=cmd_measure)

    g = sub.add_parser("gpu", help="run a command under the shared GPU mutex")
    g.add_argument("--hashcat-dir", default=HC_default())
    g.add_argument("--gpu-lock", default=LOCK_default())
    g.add_argument("command", nargs=argparse.REMAINDER, help="-- <command ...>")
    g.set_defaults(fn=cmd_gpu)

    def add_loop_args(x, with_modes=True):
        if with_modes: x.add_argument("--modes", default=env("MODES", DEFAULT_MODES))
        x.add_argument("--rounds", type=int, default=int(env("ROUNDS", "6")))
        x.add_argument("--rtimeout", type=int, default=int(env("RTIMEOUT", "1200")))
        x.add_argument("--engine", default=env("ENGINE", "codex").lower(), choices=["codex", "claude"])
        x.add_argument("--run-tag", default=env("RUN_TAG", "jul6"))
        x.add_argument("--hashcat-dir", default=HC_default())
        x.add_argument("--gpu-lock", default=LOCK_default())

    d = sub.add_parser("drive", help="per-mode round loop"); add_loop_args(d); d.set_defaults(fn=cmd_drive)
    pa = sub.add_parser("parallel", help="one worktree+driver per mode"); add_loop_args(pa); pa.set_defaults(fn=cmd_parallel)
    b = sub.add_parser("batches", help="run all numeric batches in targets.tsv"); add_loop_args(b, with_modes=False)
    b.add_argument("--targets", default=None)
    b.add_argument("--batches", default=None, help="subset, e.g. 5-14 or 5,7,9 (default: all)")
    b.add_argument("--batch-pause", type=int, default=0, help="seconds to sleep between batches (usage-window pacing)")
    b.set_defaults(fn=cmd_batches)

    r = sub.add_parser("readme", help="regenerate README.md"); r.set_defaults(fn=cmd_readme)
    v = sub.add_parser("validate", help="agent plumbing smoke test")
    v.add_argument("--engine", default=env("ENGINE", "codex").lower(), choices=["codex", "claude"])
    v.set_defaults(fn=cmd_validate)

    a = p.parse_args()
    if a.cmd == "gpu" and a.command and a.command[0] == "--": a.command = a.command[1:]
    a.fn(a)

if __name__ == "__main__":
    main()

import os, re
AR = os.path.dirname(os.path.abspath(__file__))
def rd(p):
    try: return open(p, encoding="utf-8", errors="replace").read().splitlines()
    except OSError: return []
ver, selftest = {}, {}
for ln in rd(os.path.join(AR, "survey_verify.txt")):
    p = ln.split("\t")
    if len(p) >= 3:
        try: ver[p[0]] = float(p[1].replace("+", ""))
        except ValueError: ver[p[0]] = None
        selftest[p[0]] = p[2]
loop, desc = {}, {}
for ln in rd(os.path.join(AR, "cand_table.txt")):
    p = ln.split("\t")
    if len(p) >= 3:
        try: loop[p[1]] = float(p[0])
        except ValueError: pass
        desc[p[1]] = p[2].split("delta_pct=")[0].strip().rstrip(";").strip()
name = {}
for ln in rd(os.path.join(AR, "targets_survey.tsv")):
    p = ln.split("\t")
    if len(p) >= 4 and p[0] != "mode": name[p[0]] = p[3]

# eval-gaming tell: a fast-path gated on the benchmark's FIXED input dimension (length/salt/block-count)
GAMED = re.compile(r"benchmark|pw_len|salt_len|single-block|largeblock|len ?\d|"
                   r"(one|two|three|four|five|six|seven|eight|nine|ten|\d+)[- ]byte|"
                   r"short.*(fast path|update)|fast path for", re.I)
surv = [m for m in ver if ver.get(m) is not None and ver[m] >= 0.3 and selftest.get(m) == "PASS"]
general = sorted([m for m in surv if not GAMED.search(desc.get(m, ""))], key=lambda m: -ver[m])
gamed   = sorted([m for m in surv if GAMED.search(desc.get(m, ""))], key=lambda m: -ver[m])
rej = sorted([m for m in ver if m not in surv], key=lambda x: int(x) if x.isdigit() else 0)

def row(m): return f"| {m} | {name.get(m,'')} | +{ver[m]:.2f}% | +{loop.get(m,0):.1f}% | {desc.get(m,'')} |"
out = ["\n\n## Survey: 508-mode 1-round sweep (GPT-5.6-sol, interleaved driver)\n",
       f"One interleaved-A/B round on each not-previously-explored hash mode surfaced **{len(ver)} loop candidates**. "
       f"A clean re-A/B (drift-free, main-repo, self-test gated) confirms **{len(surv)}** reproduce as a real speedup "
       f"on hashcat's benchmark; **{len(rej)}** were drift/autotune noise and are dropped.\n",
       "> ⚠️ **Important caveat — the benchmark is a single fixed vector.** `hashcat -b` and the self-test both use "
       "**one length and one salt**. A candidate can get \"faster\" by special-casing *that* input (a fast-path for "
       "`pw_len<=64`, a `salt_len=8` block, or literally \"for benchmark salt\") — it reproduces on the A/B and passes "
       "self-test (same vector), but does **not** generalize to real hashes of other lengths/salts. Those are separated "
       "below as **benchmark-conditioned**; treat their Δ as *upper-bound / benchmark-only*. Proving generality needs "
       "`-a 3` over varied lengths/salts + an independent reference (done for the SHA3/Keccak/SM3/Streebog family — "
       "all real; see above).\n",
       f"### General optimizations — {len(general)} (input-agnostic; most likely real)\n",
       "| Mode | Name | verified Δ | loop Δ | idea |", "|---|---|---|---|---|"]
out += [row(m) for m in general]
out += [f"\n### Benchmark-conditioned — {len(gamed)} (fast-paths gated on the fixed benchmark input; generality UNVERIFIED)\n",
        "| Mode | Name | Δ (benchmark-only) | loop Δ | idea |", "|---|---|---|---|---|"]
out += [row(m) for m in gamed]
out.append(f"\n_Dropped ({len(rej)}, did not reproduce on clean A/B): " + ", ".join(rej) + "._\n")
open(os.path.join(AR, "README.md"), "a", encoding="utf-8").write("\n".join(out) + "\n")
print(f"survivors={len(surv)} (general={len(general)}, benchmark-conditioned={len(gamed)}), dropped={len(rej)}")

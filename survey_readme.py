import os
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
        desc[p[1]] = p[2]
name = {}
for ln in rd(os.path.join(AR, "targets_survey.tsv")):
    p = ln.split("\t")
    if len(p) >= 4 and p[0] != "mode": name[p[0]] = p[3]
surv = sorted([m for m in ver if ver.get(m) is not None and ver[m] >= 0.3 and selftest.get(m) == "PASS"],
              key=lambda m: -ver[m])
rej = [m for m in ver if m not in surv]
out = ["\n\n## Survey: 508-mode 1-round sweep (GPT-5.6-sol, interleaved driver)\n",
       f"One interleaved-A/B round on each not-previously-explored hash mode surfaced {len(ver)} loop candidates; "
       f"a clean re-A/B (drift-free, benchmarked in the main repo, self-test gated) confirms **{len(surv)} as real** "
       "(verified Δ ≥ +0.3%). Wins live on `autoresearch/<mode>-survey`. Raw loop deltas over-state (autotune/drift); "
       "the **verified Δ** column is authoritative.\n",
       "| Mode | Name | verified Δ | loop Δ | idea |", "|---|---|---|---|---|"]
for m in surv:
    out.append(f"| {m} | {name.get(m,'')} | **+{ver[m]:.2f}%** | +{loop.get(m,0):.1f}% | {desc.get(m,'').strip()} |")
out.append(f"\n_{len(rej)} candidates did not survive clean A/B (autotune ghosts / drift / passthrough): "
           + ", ".join(sorted(rej, key=lambda x: int(x) if x.isdigit() else 0)) + "._\n")
open(os.path.join(AR, "README.md"), "a", encoding="utf-8").write("\n".join(out) + "\n")
print(f"README appended: {len(surv)} verified survivors of {len(ver)} candidates")

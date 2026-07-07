#!/bin/bash
# Regenerate README.md from the source of truth: results_<M>.tsv + git branches + targets.tsv.
# Run anytime; no dependence on any agent's context.
AR=/c/Users/jeff/Documents/autoresearch
HC=/c/Users/jeff/Documents/hashcat
python3 - "$AR" "$HC" <<'PY'
import sys,os,subprocess,csv,glob
AR,HC=sys.argv[1],sys.argv[2]
VERIFIED={'17400','17600','17800','11700','11800','31100'}   # clean-GPU A/B + correctness confirmed
REJECTED={'6100'}                                            # win did not reproduce on clean A/B
def sh(*a):
    try: return subprocess.run(a,cwd=HC,capture_output=True,text=True).stdout.strip()
    except: return ""
# manifest
tg={}
for r in csv.DictReader(open(os.path.join(AR,'targets.tsv')),delimiter='\t'):
    tg[r['mode']]={'batch':r['batch'],'cat':r['category'],'name':r['name']}
def stats(m):
    f=os.path.join(AR,f'results_{m}.tsv')
    if not os.path.exists(f): return None
    rows=[r for r in csv.reader(open(f),delimiter='\t')][1:]
    if not rows: return None
    base=rows[0][1]; keeps=[r[1] for r in rows[1:] if len(r)>4 and r[4]=='keep']
    try:
        b=float(base); best=max([float(k) for k in keeps]+[b]); d=(best-b)/b*100
    except: return None
    return dict(base=b,best=best,delta=d,exps=len(rows)-1)
def branch(m):
    return f'autoresearch/{m}-jul6' if sh('git','rev-parse','--verify','--quiet',f'autoresearch/{m}-jul6') else '-'
def mhs(x):
    return f'{x/1e6:.1f}' if x>=1e6 else (f'{x/1e3:.1f}k' if x>=1e3 else f'{x:.1f}')
rows=[]
for m,t in tg.items():
    s=stats(m); br=branch(m)
    if s is None:
        status='pending' if t['batch'] in '1234' else '-'; delta='';basebest=''
    else:
        v='✅' if m in VERIFIED else ('❌ rejected' if m in REJECTED else '')
        if s['delta']>=1.0: status=f'WIN +{s["delta"]:.1f}% {v}'.strip()
        else: status=f'roofline {v}'.strip()
        delta=f'+{s["delta"]:.1f}%' if s['delta']>=1.0 else '~0%'
        basebest=f'{mhs(s["base"])} → {mhs(s["best"])}'
    rows.append((t['batch'],m,t['name'],t['cat'],delta,basebest,status,br))
order={'PR':0,'C':1,'1':2,'2':3,'3':4,'4':5}
rows.sort(key=lambda r:(order.get(r[0],9), -(float(r[4].rstrip('%').lstrip('+')) if r[4].startswith('+') else -1)))
out=[]
out.append('# hashcat kernel autoresearch — progress\n')
out.append('Autonomous `claude -p` optimization loops (see `program.md`, `drive.sh`, `parallel.sh`). Each win lives on branch `autoresearch/<mode>-jul6` in the hashcat repo; per-experiment logs are `results_<mode>.tsv`. Regenerate this file with `bash gen_readme.sh`.\n')
out.append('**Landed PRs** (already submitted, verified): RC4 S-box `KEY8` — [hashcat#4712](https://github.com/hashcat/hashcat/pull/4712) (+4.6% Kerberoasting, +8% Office, all RC4 modes); Whirlpool single-table — [hashcat#4713](https://github.com/hashcat/hashcat/pull/4713) (+7%).\n')
out.append('Legend: ✅ = win verified on clean-GPU A/B + correctness; ❌ = win did not reproduce; batches C=first campaign, 1–4=current run.\n')
out.append('| Batch | Mode | Name | Category | Δ | MH/s (base→best) | Status | Branch |')
out.append('|---|---|---|---|---|---|---|---|')
for b,m,n,c,d,bb,st,br in rows:
    out.append(f'| {b} | {m} | {n} | {c} | {d} | {bb} | {st} | `{br}` |')
nwin=sum(1 for r in rows if r[6].startswith('WIN'))
out.append(f'\n**Totals:** {nwin} wins across {len([r for r in rows if r[4] or r[6]!="pending"])} evaluated modes. Verified-real: {len(VERIFIED)}. Rejected: {len(REJECTED)}.')
open(os.path.join(AR,'README.md'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(f'README.md regenerated: {len(rows)} modes, {nwin} wins')
PY

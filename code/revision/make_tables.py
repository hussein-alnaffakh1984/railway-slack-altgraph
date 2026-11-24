import statistics as st, json
from analyse import load, wtl, share, EPS
out = {}; tot = dict(cases=0, cert=0, certT=[0, 0, 0], ncT=[0, 0, 0], T=[0, 0, 0], S=[0, 0, 0], helped=0, certopt=0, certstrict=0)
lines = []
for fam, label in (('station', 'perturbed station'), ('junction', 'junction'), ('corridor', 'corridor')):
    R, sk = load(fam); n = len(R)
    U = [r['uniform'] for r in R]; T = [r['targeted'] for r in R]; S = [r['sequential'] for r in R]
    C = [r for r in R if r['cert']]; NC = [r for r in R if not r['cert']]
    H = [r for r in R if r['L0'] - r['optimal'] > EPS]
    f = lambda rows, a, b: wtl([r[a] for r in rows], [r[b] for r in rows])
    sh = {k: 100 * st.mean(share(r, k) for r in H) for k in ('uniform', 'targeted', 'sequential')}
    d = dict(instances=len({r['inst'] for r in R}), discarded=sk, cases=n, m=R[0]['m'], pairs=sorted({int(r['pairs']) for r in R}), budgets=sorted({r['budget'] for r in R}),
             cert=len(C), certTU=f(C, 'targeted', 'uniform'), ncTU=f(NC, 'targeted', 'uniform'), TU=f(R, 'targeted', 'uniform'), SU=f(R, 'sequential', 'uniform'), ST=f(R, 'sequential', 'targeted'),
             helped=len(H), share=sh, certopt=sum(abs(r['targeted'] - r['optimal']) <= EPS for r in C),
             Topt=sum(abs(r['targeted'] - r['optimal']) <= EPS for r in R), Sopt=sum(abs(r['sequential'] - r['optimal']) <= EPS for r in R), Uopt=sum(abs(r['uniform'] - r['optimal']) <= EPS for r in R),
             fail0=sum(r['first_fail_theta'] == '0' for r in NC), nobind=sum(r['n_binding0'] == '0' for r in R),
             sharecert={k: 100 * st.mean(share(r, k) for r in H if r['cert']) for k in ('uniform', 'targeted', 'sequential')} if any(r['cert'] for r in H) else None,
             sharenc={k: 100 * st.mean(share(r, k) for r in H if not r['cert']) for k in ('uniform', 'targeted', 'sequential')} if any(not r['cert'] for r in H) else None,
             helped_cert=sum(r['cert'] for r in H), helped_nc=sum(not r['cert'] for r in H))
    out[fam] = d
    lines.append(f"{label} & {d['cases']} & {d['cert']} & {d['certTU'][0]}/{d['certTU'][1]}/{d['certTU'][2]} & {d['ncTU'][0]}/{d['ncTU'][1]}/{d['ncTU'][2]} & {d['SU'][0]}/{d['SU'][1]}/{d['SU'][2]} & {d['helped']} & {sh['uniform']:.0f} / {sh['targeted']:.0f} / {sh['sequential']:.0f}\\\\")
    tot['cases'] += n; tot['cert'] += len(C); tot['helped'] += len(H); tot['certopt'] += d['certopt']; tot['certstrict'] += d['certTU'][0]
    for k, v in (('certT', d['certTU']), ('ncT', d['ncTU']), ('T', d['TU']), ('S', d['SU'])):
        tot[k] = [a + b for a, b in zip(tot[k], v)]
allR = sum((load(f)[0] for f in ('station', 'junction', 'corridor')), [])
H = [r for r in allR if r['L0'] - r['optimal'] > EPS]
tot['share'] = {k: 100 * st.mean(share(r, k) for r in H) for k in ('uniform', 'targeted', 'sequential')}
lines.append(f"all & {tot['cases']} & {tot['cert']} & {'/'.join(map(str, tot['certT']))} & {'/'.join(map(str, tot['ncT']))} & {'/'.join(map(str, tot['S']))} & {tot['helped']} & {tot['share']['uniform']:.0f} / {tot['share']['targeted']:.0f} / {tot['share']['sequential']:.0f}\\\\")
out['total'] = tot
open('table_families.tex', 'w').write('\n'.join(lines) + '\n')
json.dump(out, open('summary.json', 'w'), indent=1)
print('\n'.join(lines)); print(json.dumps(out, indent=1))

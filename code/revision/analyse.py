"""Summaries of results_{published,station,junction,corridor}.csv for the paper and the supplement."""
import csv, sys, statistics as st, collections
EPS = 1e-6
def load(f):
    try: rows = list(csv.DictReader(open(f"results_{f}.csv")))
    except FileNotFoundError: return [], 0
    skipped = sum(r['budget'] == '0' for r in rows)
    rows = [r for r in rows if r['budget'] != '0']
    for r in rows:
        for k in ('L0', 'uniform', 'targeted', 'sequential', 'optimal'): r[k] = float(r[k])
        r['budget'] = int(r['budget']); r['cert'] = r['certificate'] == 'True'
    return rows, skipped
def wtl(a, b):   # a better / equal / worse than b (smaller is better)
    return sum(x < y - EPS for x, y in zip(a, b)), sum(abs(x - y) <= EPS for x, y in zip(a, b)), sum(x > y + EPS for x, y in zip(a, b))
def share(r, k):
    den = r['L0'] - r['optimal']
    return None if den <= EPS else (r['L0'] - r[k]) / den
def summary(name, rows, skipped, out=sys.stdout):
    if not rows: return
    n = len(rows); inst = len({r['inst'] for r in rows})
    print(f"\n=== {name}: {inst} instances ({skipped} discarded: no secondary delay), {n} cases ===", file=out)
    for B in sorted({r['budget'] for r in rows}) + ['all']:
        R = [r for r in rows if B == 'all' or r['budget'] == B]
        U = [r['uniform'] for r in R]; T = [r['targeted'] for r in R]; S = [r['sequential'] for r in R]; O = [r['optimal'] for r in R]
        cert = [r for r in R if r['cert']]
        helped = [r for r in R if r['L0'] - r['optimal'] > EPS]
        sh = {k: [share(r, k) for r in helped] for k in ('uniform', 'targeted', 'sequential')}
        print(f"budget {B}: cases {len(R)}; certificate holds {len(cert)}; "
              f"targeted vs uniform (better/equal/worse) {wtl(T, U)}; sequential vs uniform {wtl(S, U)}; sequential vs targeted {wtl(S, T)}; "
              f"targeted optimal in {sum(abs(t - o) <= EPS for t, o in zip(T, O))}, sequential optimal in {sum(abs(t - o) <= EPS for t, o in zip(S, O))}, "
              f"uniform optimal in {sum(abs(t - o) <= EPS for t, o in zip(U, O))}; cases where flexibility can help {len(helped)}; "
              f"mean share of achievable reduction: uniform {st.mean(sh['uniform']) if helped else float('nan'):.3f}, "
              f"targeted {st.mean(sh['targeted']) if helped else float('nan'):.3f}, sequential {st.mean(sh['sequential']) if helped else float('nan'):.3f}", file=out)
        viol = [r for r in cert if r['targeted'] > r['uniform'] + EPS]
        print(f"    certificate holds -> targeted <= uniform in all {len(cert)} (violations {len(viol)}); strictly better in {sum(r['targeted'] < r['uniform'] - EPS for r in cert)}; "
              f"targeted = optimal allocation in {sum(abs(r['targeted'] - r['optimal']) <= EPS for r in cert)} of them", file=out)
        nc = [r for r in R if not r['cert']]
        print(f"    certificate fails ({len(nc)}): targeted vs uniform {wtl([r['targeted'] for r in nc], [r['uniform'] for r in nc])}; "
              f"fails already at theta=0 in {sum(r['first_fail_theta'] == '0' for r in nc)}", file=out)
if __name__ == '__main__':
    for f in ('published', 'station', 'junction', 'corridor'):
        rows, sk = load(f); summary(f, rows, sk)

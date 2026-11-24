"""Slack-allocation experiments of the revised paper.
usage: python slack_experiments.py {station|junction|corridor} [nproc]
Policies at equal total budget Phi (m = number of flexible departure arcs):
  uniform     phi_k = Phi/m
  targeted    whole budget on b, the lowest-index arc binding at the zero-slack optimum returned by the
              solver (if no departure arc is binding there: the arc with the largest beta)
  sequential  budget released in equal steps, each step to the arc chosen by the same rule at the current allocation
  optimal     min over all allocations (MILP with phi as variables)
certificate   exact check of the hypothesis of Theorem 1 on the segment uniform -> Phi e_b (Proposition 2)."""
import sys, csv, time
from fractions import Fraction as Fr
from multiprocessing import Pool
sys.path.insert(0, '..')
from ag import AG, segment, certificate
import families as fam

def pick(ag, phi, sel):
    L, be = ag.beta(phi, sel)
    binding = [k for k in range(ag.m) if be[k] == L]
    return (binding[0] if binding else max(range(ag.m), key=lambda k: (be[k], -k))), binding

def run_case(args):
    family, key, budgets, step = args
    t0 = time.time()
    ag = {'station': lambda: fam.perturbed_station(key), 'junction': lambda: fam.junction(key),
          'corridor': lambda: fam.corridor(*key), 'published': lambda: fam.dariano()}[family]()
    m = ag.m
    small = len(ag.pairs) <= 6
    if small:                                    # exhaustive enumeration (exact rational arithmetic)
        def value(phi): return min(v for v, s in ag.enumerate(phi))
        def solve(phi, scale=1):
            en = ag.enumerate(phi); L = min(v for v, s in en); return L, min(s for v, s in en if v == L)
        def btest(phi, L, ks):
            for v, s in ag.enumerate(phi):
                if v == L:
                    LL, be = ag.beta(phi, s)
                    if any(be[k] == LL for k in ks): return True
            return False
    else:
        solve = ag.solve
        def value(phi): return ag.solve(phi, scale=m * m)[0]
        def btest(phi, L, ks): return ag.binding_in_some_optimum(phi, L, ks, scale=m * m)
    zero = [Fr(0)] * m
    L0, sel0 = solve(zero)
    b, bind0 = pick(ag, zero, sel0)
    rows = []
    if family in ('station', 'junction') and L0 <= 0:      # nothing to recover: no secondary delay at zero flexibility
        return [dict(family=family, inst=ag.name, m=m, pairs=len(ag.pairs), budget=0, L0=float(L0), b='', n_binding0=len(bind0), uniform='', targeted='', sequential='', optimal='', opt_phi='', certificate='', first_fail_theta='', grid_points='', seq_targets='', secs=0, max_solve_s=0)]
    for Phi in budgets:
        Lu, _ = solve([Fr(Phi, m)] * m, scale=m)
        Lt, _ = solve([Fr(Phi) if k == b else Fr(0) for k in range(m)])
        phi = list(zero); used = 0; moves = []
        while used < Phi:
            L, sel = solve(phi, scale=1)
            k, _ = pick(ag, phi, sel)
            phi[k] += step; used += step; moves.append(k)
        Ls, _ = solve(phi)
        Lo, phio = ag.optimal_allocation(Phi)
        holds, thfail, g = certificate(ag, Phi, b, btest, value)
        rows.append(dict(family=family, inst=ag.name, m=m, pairs=len(ag.pairs), budget=Phi, L0=float(L0), b=ag.flex[b][0],
                         n_binding0=len(bind0), uniform=float(Lu), targeted=float(Lt), sequential=float(Ls),
                         optimal=round(Lo, 4), opt_phi=' '.join(f"{p:.2f}" for p in phio),
                         certificate=holds, first_fail_theta=('' if thfail is None else str(thfail)),
                         grid_points=m * Phi + 1, seq_targets=''.join(str(k) for k in moves), secs=round(time.time() - t0, 1), max_solve_s=round(AG.max_solve_seconds, 2)))
    return rows

SPECS = {
    'published': ([None], (10, 20, 25), 1),
    'station': (list(range(1, 301)), (10, 20), 1),
    'junction': (list(range(1, 101)), (20, 40), 2),
    'corridor': ([(k, s, seed) for seed in (1, 2, 3, 4) for k, s in ((3, 2), (4, 2), (5, 2), (5, 3), (6, 2))], (4, 8, 16), 1),
}
if __name__ == '__main__':
    family = sys.argv[1]; nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    keys, budgets, step = SPECS[family]
    out = (sys.argv[3] if len(sys.argv) > 3 else "") + f"results_{family}.csv"; w = None
    with Pool(nproc) as pool, open(out, 'w', newline='') as fh:
        for rows in pool.imap(run_case, [(family, k, budgets, step) for k in keys]):
            for r in rows:
                if w is None:
                    w = csv.DictWriter(fh, fieldnames=list(r)); w.writeheader()
                w.writerow(r); fh.flush()
            print(rows[0]['inst'], [(r['budget'], r['uniform'], r['targeted'], r['sequential'], r['optimal'], r['certificate']) for r in rows], rows[-1]['secs'], flush=True)

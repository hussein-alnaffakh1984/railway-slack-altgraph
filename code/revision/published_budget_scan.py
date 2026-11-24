"""Published instance: for every integer budget Phi = 1..50, uniform / targeted / opposite / optimal allocation
(exact: L*(Phi-x, x) is piecewise affine in x with breakpoints at multiples of 1/2) and the exact certificate."""
import sys, csv; sys.path.insert(0, '..')
from fractions import Fraction as Fr
from ag import segment, certificate
import families as fam
ag = fam.dariano(); V = lambda phi: min(v for v, s in ag.enumerate(phi))
def btest(phi, L, ks):
    for v, s in ag.enumerate(phi):
        if v == L:
            LL, be = ag.beta(phi, s)
            if any(be[k] == LL for k in ks): return True
    return False
rows = []; same = 0; cert = 0
for Phi in range(1, 51):
    u = V([Fr(Phi, 2)] * 2); t = V([0, Phi]); o = V([Phi, 0])
    best = min((V([Fr(Phi) - Fr(j, 2), Fr(j, 2)]), Fr(j, 2)) for j in range(2 * Phi + 1))
    holds, th, g = certificate(ag, Phi, 1, btest, V)
    mono = all(g[a] >= g[b] for a, b in zip(sorted(g), sorted(g)[1:])) if holds else None
    same += t == best[0]; cert += holds
    rows.append((Phi, float(u), float(t), float(o), float(best[0]), float(best[1]), holds, '' if th is None else str(th), 2 * Phi + 1))
    if Phi in (10, 20, 25, 30, 50): print(rows[-1], 'g non-increasing on grid:', mono)
csv.writer(open('published_budget_scan.csv', 'w', newline='')).writerows([('budget', 'uniform', 'targeted_B', 'opposite_A', 'optimal', 'optimal_phiB', 'certificate', 'first_fail_theta', 'grid_points')] + rows)
print(f"budgets 1..50: targeted = optimal allocation in {same}; certificate holds in {cert}; fails at budgets {[r[0] for r in rows if not r[6]]}")
print("targeted strictly better than uniform at budgets:", sum(r[2] < r[1] for r in rows), "equal:", sum(r[2] == r[1] for r in rows), "worse:", sum(r[2] > r[1] for r in rows))

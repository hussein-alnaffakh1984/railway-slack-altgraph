"""Big-M check on the MILPs of the allocation experiments: optimum at the uniform allocation with M, 2M, 10M
(junction family, budget 20; corridor family, maximum lateness, budget 8), compared with each other and,
for the published station, with exhaustive enumeration."""
import sys; sys.path.insert(0, '..')
from fractions import Fraction as Fr
import families as fam
ok = True; n = 0
cases = [(fam.junction(s), 20) for s in range(1, 101)] + [(fam.corridor(k, s, seed), 8) for seed in (1, 2, 3, 4) for k, s in ((3, 2), (4, 2), (5, 2), (5, 3), (6, 2))]
for ag, Phi in cases:
    phi = [Fr(Phi, ag.m)] * ag.m
    v = [ag.solve(phi, scale=ag.m, Mfac=f)[0] for f in (1, 2, 10)]
    n += 1; ok &= len(set(v)) == 1
    if len(set(v)) != 1: print("MISMATCH", ag.name, v)
ag = fam.dariano()
for d in (0, 10, 25):
    e = min(v for v, s in ag.enumerate([d, d])); v = [ag.solve([d, d], Mfac=f)[0] for f in (1, 2, 10)]; n += 1; ok &= set(v) == {e}
print(f"{n} instances (100 junction, 20 corridor, 3 published): optimum identical with M, 2M, 10M: {ok}")

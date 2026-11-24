"""Compares the two independent runs of the slack experiments (results_*.csv and run2/results_*.csv):
every objective value, target, certificate outcome and sequential move sequence must be identical."""
import csv, sys
cols = ('inst', 'budget', 'L0', 'b', 'n_binding0', 'uniform', 'targeted', 'sequential', 'optimal', 'certificate', 'first_fail_theta', 'grid_points', 'seq_targets')
ok = True
for fam in ('published', 'station', 'junction', 'corridor'):
    a = list(csv.DictReader(open(f'results_{fam}.csv'))); b = list(csv.DictReader(open(f'run2/results_{fam}.csv')))
    same = len(a) == len(b) and all(all(x[c] == y[c] for c in cols) for x, y in zip(a, b))
    mx = max(float(r.get('max_solve_s') or 0) for r in b)
    print(f"{fam}: {len(a)} rows, identical: {same}; longest single solver call in run 2: {mx:.2f} s (limit 120 s)")
    ok &= same
print("both runs identical:", ok)

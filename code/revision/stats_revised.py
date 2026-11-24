"""Descriptive statistics of the constructive rules on the 20 benchmark instances, and the one
inferential comparison that is meaningful: AMCC versus FCFS (paired, two-sided exact Wilcoxon)."""
import csv, statistics as st, sys
from scipy.stats import wilcoxon
rows = list(csv.DictReader(open('../benchmark_20_instances.csv')))
opt = [float(r['opt']) for r in rows]; am = [float(r['amcc']) for r in rows]; fc = [float(r['fcfs']) for r in rows]
gap = lambda a: [100 * (x - o) / o for x, o in zip(a, opt)]
for name, a in (('AMCC', am), ('FCFS', fc)):
    g = sorted(gap(a)); q = st.quantiles(g, n=4, method='inclusive')
    print(f"{name}: optimal on {sum(x == o for x, o in zip(a, opt))}/20; gap mean {st.mean(g):.2f}%, median {st.median(g):.2f}%, "
          f"IQR [{q[0]:.2f}, {q[2]:.2f}]%, max {max(g):.1f}%; absolute excess mean {st.mean(x - o for x, o in zip(a, opt)):.2f}, max {max(x - o for x, o in zip(a, opt)):.0f} time units")
d = [f - a for f, a in zip(fc, am)]; nz = [x for x in d if x != 0]
res = wilcoxon(fc, am, alternative='two-sided', zero_method='wilcox', method='exact')
pos = sum(x > 0 for x in d); neg = sum(x < 0 for x in d); zero = sum(x == 0 for x in d)
import numpy as np
from scipy.stats import rankdata
r = rankdata([abs(x) for x in nz]); Wp = sum(ri for ri, x in zip(r, nz) if x > 0); Wm = sum(ri for ri, x in zip(r, nz) if x < 0)
rb = (Wp - Wm) / (len(nz) * (len(nz) + 1) / 2)
walsh = sorted((d[i] + d[j]) / 2 for i in range(len(d)) for j in range(i, len(d)))
print(f"FCFS - AMCC (makespan, time units): FCFS worse on {pos}, equal on {zero}, better on {neg} of 20 instances; "
      f"median difference {st.median(d):.1f}, Hodges-Lehmann estimate {st.median(walsh):.2f}, mean {st.mean(d):.2f}")
print(f"two-sided exact Wilcoxon signed-rank: n={len(nz)} non-zero pairs, W+={Wp:.0f}, W-={Wm:.0f}, p={res.pvalue:.2e}; matched-pairs rank-biserial r={rb:.2f}")

"""Statistics on the 20 benchmark instances actually reported (benchmark_20_instances.csv):
mean, SD (sample and population), max of heuristic gaps; exact one-sided Wilcoxon signed-rank tests."""
import csv, statistics as st
from scipy.stats import wilcoxon
rows=list(csv.DictReader(open('benchmark_20_instances.csv')))
opt=[float(r['opt']) for r in rows]; am=[float(r['amcc']) for r in rows]; fc=[float(r['fcfs']) for r in rows]
ag=[float(r['amcc_gap']) for r in rows]; fg=[float(r['fcfs_gap']) for r in rows]
print(f"instances: {len(rows)}  sizes: {sorted(set(r['inst'].split('#')[0] for r in rows))}")
for name,g in (("AMCC",ag),("FCFS",fg)):
    print(f"{name}: mean {st.mean(g):.2f}%  SD(sample) {st.stdev(g):.2f}%  SD(pop) {st.pstdev(g):.2f}%  max {max(g):.1f}%  nonzero {sum(x>0 for x in g)}")
def wx(a,b,label):
    d=[x-y for x,y in zip(a,b)]; nz=[x for x in d if x!=0]
    res=wilcoxon(a,b,alternative='greater',zero_method='wilcox',method='exact')
    print(f"{label}: n_nonzero={len(nz)}  W+={res.statistic:.0f}  exact one-sided p={res.pvalue:.2e}")
wx(am,opt,"AMCC > optimum"); wx(fc,opt,"FCFS > optimum"); wx(fc,am,"FCFS > AMCC")

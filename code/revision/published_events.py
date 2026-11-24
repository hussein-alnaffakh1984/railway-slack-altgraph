"""Complete event-by-event comparison with Table 1 of D'Ariano, Pacciarelli, Pranzo (2005).
Published values typed from their Table 1 (columns 'B&B solution delta = 0, 10, 25')."""
import sys, csv; sys.path.insert(0, '..')
from ag import longest
import families as fam
PUB = {  # delta: train: (t3|t6, t4|t7, tstop, t8, tout)
    0:  dict(A=(107, 160, 170, 190, 205), B=(95, 105, 115, 160, 175), C=(112, 137, None, 175, 190)),
    10: dict(A=(107, 150, 160, 180, 195), B=(95, 105, 115, 150, 165), C=(112, 137, None, 165, 180)),
    25: dict(A=(107, 135, 145, 165, 180), B=(95, 105, 115, 135, 150), C=(112, 137, None, 180, 195)),
}
PUB_SEC = {0: dict(Aexit=41, Bexit=0, Cexit=13, Astop=41, Bstop=0), 10: dict(Aexit=31, Bexit=-10, Cexit=3, Astop=31, Bstop=0),
           25: dict(Aexit=16, Bexit=-25, Cexit=18, Astop=16, Bstop=0)}
NODES = dict(A=('A0', 'A1', 'A2', 'A3', 'A*'), B=('B0', 'B1', 'B2', 'B3', 'B*'), C=('C0', 'C1', None, 'C2', 'C*'))
LAB = dict(A=('t3', 't4', 'tstop', 't8', 'tout'), B=('t3', 't4', 'tstop', 't8', 'tout'), C=('t6', 't7', None, 't8', 'tout'))
INPUT = {('A', 't3'), ('B', 't3'), ('C', 't6')}
ag = fam.dariano()
rows = []; ok = True; n_in = n_out = 0
for d in (0, 10, 25):
    en = ag.enumerate([d, d]); L = min(v for v, s in en)
    opt = [s for v, s in en if v == L]
    assert len(opt) == 1, "optimal selection is unique at the published flexibilities"
    t = longest(ag.arcs([d, d], opt[0]))
    for tr in 'ABC':
        for nd, lab, pub in zip(NODES[tr], LAB[tr], PUB[d][tr]):
            if nd is None: continue
            kind = 'input' if (tr, lab) in INPUT else 'output'
            n_in += kind == 'input'; n_out += kind == 'output'
            ok &= t[nd] == pub
            rows.append((d, tr, lab, kind, t[nd], pub, t[nd] == pub))
    due = {v: -w for v, w in ag.due}
    sec = dict(Aexit=t['A*'] - due['A*'], Bexit=t['B*'] - due['B*'], Cexit=t['C*'] - due['C*'], Astop=t['A2'] - due['A2'], Bstop=t['B2'] - due['B2'])
    for k, v in sec.items():
        ok &= v == PUB_SEC[d][k]; rows.append((d, k[0], 'secondary delay at ' + k[1:], 'output', v, PUB_SEC[d][k], v == PUB_SEC[d][k]))
    print(f"delta={d:>2}: L*={L}  unique optimum; max secondary {max(sec.values())}")
csv.writer(open('published_event_times.csv', 'w', newline='')).writerows([('delta', 'train', 'event', 'kind', 'this_paper', 'published', 'equal')] + rows)
print(f"event times compared: {n_in} inputs + {n_out} model outputs; secondary delays compared: 15; all equal: {ok}")

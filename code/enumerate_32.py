"""Enumerate ALL 2^5 selections of the five-pair alternative graph of D'Ariano et al. (2005), Fig. 3
(A/B pairs on sections 3, 4, 8; A/C and B/C on 8), with Table-1 arc weights and the published min-dwells.
Reports feasible count and the optimal maximum secondary delay; also the equal-budget points of paper Table 3."""
import itertools
def lp(arcs):
    N={x for u,v,w in arcs for x in (u,v)}|{'0'};NEG=float('-inf');d={n:NEG for n in N};d['0']=0
    for _ in range(len(N)+3):
        for u,v,w in arcs:
            if d[u]!=NEG and d[u]+w>d[v]: d[v]=d[u]+w
    for u,v,w in arcs:
        if d[u]!=NEG and d[u]+w>d[v]: return None
    return d
def fixed(dA,dB):
    return [('0','A3',107),('A3','A4',12),('A4','ASt',10),('ASt','A8',20),('A8','A*',15),
            ('0','B3',95),('B3','B4',10),('B4','BSt',10),('BSt','B8',20),('B8','B*',15),
            ('0','C6',112),('C6','C7',25),('C7','C8',25),('C8','C*',15),('0','A8',115-dA),('0','B8',160-dB)]
pa={'ASt':95,'A*':130,'BSt':115,'B*':175,'C*':160}
pairs=[(('B4','A3',0),('A4','B3',0)),(('B8','A4',0),('A8','B4',0)),(('B*','A8',0),('A*','B8',0)),
       (('C*','A8',0),('A*','C8',0)),(('C*','B8',0),('B*','C8',0))]
def opt(dA,dB):
    f=fixed(dA,dB); t0=lp(f); due=[(k,'n',-max(t0[k],pa[k])) for k in pa]; best=None; nf=0
    for sel in itertools.product([0,1],repeat=5):
        g=lp(f+[pairs[i][sel[i]] for i in range(5)]+due)
        if g: nf+=1; best=g['n'] if best is None else min(best,g['n'])
    return best,nf
if __name__=="__main__":
    for d in (0,10,25): print(f"delta={d:>2}: optimum {opt(d,d)[0]}  (feasible selections {opt(d,d)[1]} of 32)")
    for Phi in (10,20,25): print(f"budget {Phi}: uniform {opt(Phi/2,Phi/2)[0]}  targeted {opt(0,Phi)[0]}")

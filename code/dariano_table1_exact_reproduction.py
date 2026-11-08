import itertools
# Add the shared single PLATFORM (Stop) to the no-overtaking order of A,B.
# A,B keep one consistent order across blocks 3, 4 (incl. the stop) and 8; the arc B8->ASt / A8->BSt is implied by B8->A4 / A8->B4 and kept for readability.
delA,delC=47,17
def fixed(delta):
    return [('0','A3',60+delA),('A3','A4',12),('A4','ASt',10),('ASt','A8',20),('A8','Aex',15),
            ('0','B3',95),      ('B3','B4',10),('B4','BSt',10),('BSt','B8',20),('B8','Bex',15),
            ('0','C6',95+delC), ('C6','C7',25),('C7','C8',25),('C8','Cex',15),
            ('0','A8',115-delta),('0','B8',160-delta)]
planned_a={'ASt':95,'Aex':130,'BSt':115,'Bex':175,'Cex':160}
def lp(arcs):
    nodes={x for u,v,w in arcs for x in (u,v)}|{'0'}; NEG=float('-inf')
    d={n:NEG for n in nodes}; d['0']=0
    for _ in range(len(nodes)+3):
        for u,v,w in arcs:
            if d[u]!=NEG and d[u]+w>d[v]: d[v]=d[u]+w
    for u,v,w in arcs:
        if d[u]!=NEG and d[u]+w>d[v]: return None
    return d
def order_arcs(oAB,oAC,oBC):
    a=[]
    if oAB==0:   # B before A on 3, 4 (incl. the stop) and 8; the arc B8->ASt / A8->BSt is implied by B8->A4 / A8->B4 and kept for readability
        a+=[('B4','A3',0),('B8','A4',0),('B8','ASt',0),('Bex','A8',0)]
    else:        # A before B
        a+=[('A4','B3',0),('A8','B4',0),('A8','BSt',0),('Aex','B8',0)]
    a+= [('Cex','A8',0)] if oAC==0 else [('Aex','C8',0)]
    a+= [('Cex','B8',0)] if oBC==0 else [('Bex','C8',0)]
    return a
def solve(delta):
    f=fixed(delta); t0=lp(f); mod={k:max(t0[k],planned_a[k]) for k in planned_a}
    due=[(k,'n',-mod[k]) for k in mod]; best=None;bd=None
    for oAB,oAC,oBC in itertools.product([0,1],repeat=3):
        d=lp(f+order_arcs(oAB,oAC,oBC)+due)
        if d is None: continue
        if best is None or d['n']<best: best=d['n']; bd=d
    sec={X:bd[{'A':'Aex','B':'Bex','C':'Cex'}[X]]-mod[{'A':'Aex','B':'Bex','C':'Cex'}[X]] for X in 'ABC'}
    seq=''.join(sorted('ABC',key=lambda X:bd[{'A':'A8','B':'B8','C':'C8'}[X]]))
    return best,seq,sec,bd
print("delta | my max-sec  seq |  exits A,B,C   |  PAPER: max  seq  exits")
papr={0:(41,'BCA',(205,175,190)),10:(31,'BCA',(195,165,180)),25:(18,'BAC',(180,150,195))}
allok=True
for delta in [0,10,25]:
    mx,seq,sec,bd=solve(delta); pm,ps,pe=papr[delta]
    ex=(bd['Aex'],bd['Bex'],bd['Cex'])
    ok = (mx==pm and seq==ps); allok&=ok
    print(f"  {delta:>2}  |   {mx:>3}      {seq} | {ex} |  {pm}  {ps} {pe}  {'<== MATCH' if ok else 'differs'}")
print("\nper-train secondary (mine) vs paper (A,B,C):")
paper_sec={0:(41,0,13),10:(31,-10,3),25:(16,-25,18)}
for delta in [0,10,25]:
    s=solve(delta)[2]; print(f"  delta={delta:>2}: mine A={s['A']},B={s['B']},C={s['C']}  | paper {paper_sec[delta]}")
print("\nALL THREE MATCH:" , allok)

import itertools
# BTF on the REAL D'Ariano (2005) instance (exact model from the validated reproduction).
# Flexibility delta lets a train depart the platform earlier: (0,A8)=115-dA, (0,B8)=160-dB.
# Bottleneck = block section 8 (the merge / min cut). The PLATFORM feeds it.
# Question: which train's flexibility relieves the bottleneck for late train A?
delA,delC=47,17
def fixed(dA,dB):
    return [('0','A3',60+delA),('A3','A4',12),('A4','ASt',10),('ASt','A8',20),('A8','Aex',15),
            ('0','B3',95),('B3','B4',10),('B4','BSt',10),('BSt','B8',20),('B8','Bex',15),
            ('0','C6',95+delC),('C6','C7',25),('C7','C8',25),('C8','Cex',15),
            ('0','A8',115-dA),('0','B8',160-dB)]
pa={'ASt':95,'Aex':130,'BSt':115,'Bex':175,'Cex':160}
def lp(arcs):
    N={x for u,v,w in arcs for x in (u,v)}|{'0'};NEG=float('-inf');d={n:NEG for n in N};d['0']=0
    for _ in range(len(N)+3):
        for u,v,w in arcs:
            if d[u]!=NEG and d[u]+w>d[v]: d[v]=d[u]+w
    for u,v,w in arcs:
        if d[u]!=NEG and d[u]+w>d[v]: return None
    return d
def oarc(oAB,oAC,oBC):
    a=[('B4','A3',0),('B8','A4',0),('B8','ASt',0),('Bex','A8',0)] if oAB==0 else \
      [('A4','B3',0),('A8','B4',0),('A8','BSt',0),('Aex','B8',0)]
    a+=[('Cex','A8',0)] if oAC==0 else [('Aex','C8',0)]
    a+=[('Cex','B8',0)] if oBC==0 else [('Bex','C8',0)]
    return a
def maxsec(dA,dB):
    f=fixed(dA,dB);t0=lp(f);mod={k:max(t0[k],pa[k]) for k in pa};due=[(k,'n',-mod[k]) for k in mod]
    best=None
    for o in itertools.product([0,1],repeat=3):
        g=lp(f+oarc(*o)+due)
        if g and (best is None or g['n']<best): best=g['n']
    return best
print("BTF on the real D'Ariano (2005) instance -- max secondary delay (s):")
print(f"{'delta':>6}{'uniform (A&B)':>15}{'BTF: B only':>14}{'A only':>9}{'budget uni/BTF':>16}")
for d in [0,5,10,15,20,25]:
    uni=maxsec(d,d); bonly=maxsec(0,d); aonly=maxsec(d,0)
    print(f"{d:>6}{uni:>15}{bonly:>14}{aonly:>9}{('%d / %d'%(2*d,d)):>16}")
print("\nReading: B is the on-time LEADER feeding the section-8 bottleneck; A is the late follower.")
print("If 'B only' == 'uniform', then flexibility on A is wasted and BTF gives the full")
print("benefit at half the timetable-flexibility budget, ON THE REAL PUBLISHED INSTANCE.")

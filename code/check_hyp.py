"""Hypothesis of Theorem 1 on the published instance, with the exact 'on some longest path' test:
arc (0,dep_k) is binding iff  w(0,dep_k) + longest(dep_k -> n) == longest(0 -> n)."""
import itertools
src=open("btf_on_dariano.py").read().split('print("BTF on')[0]; ns={}; exec(src,ns)
fixed,pa,lp,oarc=ns['fixed'],ns['pa'],ns['lp'],ns['oarc']
def lp_from(arcs,src_node):
    N={x for u,v,w in arcs for x in (u,v)}; NEG=float('-inf'); d={n:NEG for n in N}; d[src_node]=0
    for _ in range(len(N)+3):
        for u,v,w in arcs:
            if d[u]!=NEG and d[u]+w>d[v]: d[v]=d[u]+w
    return d
def analyse(dA,dB):
    f=fixed(dA,dB); t0=lp(f); mod={k:max(t0[k],pa[k]) for k in pa}; due=[(k,'n',-mod[k]) for k in mod]
    res=[]
    for o in itertools.product([0,1],repeat=3):
        arcs=f+oarc(*o)+due; g=lp(arcs)
        if not g: continue
        L=g['n']; bind={}
        for tr,node,w in (('A','A8',115-dA),('B','B8',160-dB)):
            bind[tr]= abs(w+lp_from(arcs,node)['n']-L)<1e-9
        res.append((L,o,bind['A'],bind['B']))
    best=min(r[0] for r in res); return best,[r for r in res if r[0]==best]
if __name__=="__main__":
    ok=True
    print("budget theta (phiA,phiB)  L*  #opt  A-binding(any opt)  B-binding(all opt)")
    for Phi in (10,20,25):
        for th in (0,0.25,0.5,0.75,1.0):
            dA=Phi/2*(1-th); dB=Phi/2+th*Phi/2
            best,opt=analyse(dA,dB); anyA=any(r[2] for r in opt); allB=all(r[3] for r in opt)
            ok&=not anyA
            print(f"{Phi:>5} {th:<5} ({dA:>5},{dB:>5}) {best:>6} {len(opt):>4}   {anyA!s:<6}  {allB}")
    print("Hypothesis (no optimal selection has A's departure arc on a longest path) holds at all points:",ok)
    for Phi in (10,20,25): print(f"equal budget {Phi}: uniform={analyse(Phi/2,Phi/2)[0]} targeted={analyse(0,Phi)[0]}")

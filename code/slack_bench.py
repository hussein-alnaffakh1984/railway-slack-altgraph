"""Targeted vs uniform timetable slack on the 20 benchmark instances (exact, max-lateness objective).
Slack phi_k lowers train k's release arc (0 -> first node) from rho_k to rho_k - phi_k (a station departure window).
Objective: max_k (exit_k - due_k). Exact optimum by MILP (CBC)."""
import railsched as rs, pulp, itertools, sys
def solve(inst, phi, time_limit=60):
    F=[('0',inst.node(k,0),inst.release[k]-phi[k]) for k in range(inst.K)]
    F+=[a for a in inst.fixed_arcs() if a[0]!='0']
    A=inst.alt_pairs(); due=inst.due_dates()
    nodes=sorted({x for u,v,w in F for x in (u,v)}|{u for p in A for a in p for u in a[:2]})
    M=sum(sum(r) for r in inst.run)+max(inst.release)+10
    m=pulp.LpProblem("L",pulp.LpMinimize)
    t={nd:pulp.LpVariable(f"t_{nd}") for nd in nodes}; lam=pulp.LpVariable("lam")
    x=[pulp.LpVariable(f"x{i}",cat="Binary") for i in range(len(A))]
    m+=lam
    m+=t['0']==0
    for u,v,w in F: m+=t[v]-t[u]>=w
    for i,(e1,e2) in enumerate(A):
        m+=t[e1[1]]-t[e1[0]]>=e1[2]-M*(1-x[i]); m+=t[e2[1]]-t[e2[0]]>=e2[2]-M*x[i]
    # exit of train k = t[n] contributions: last node + run; use explicit exit var per train
    for k in range(inst.K):
        last=inst.node(k,inst.R-1); m+=lam>=t[last]+inst.run[k][inst.R-1]-due[k]
    m.solve(pulp.PULP_CBC_CMD(msg=0,timeLimit=time_limit))
    st=pulp.LpStatus[m.status]; sel=[int(round(v.value())) for v in x]
    return round(lam.value(),4), sel, st
def binding_release_trains(inst, phi, sel):
    """Trains whose release arc lies on SOME longest 0-n path of the selected graph:
    (rho_k - phi_k) + longest((k,1) -> n) == longest(0 -> n)."""
    A=inst.alt_pairs(); due=inst.due_dates()
    F=[('0',inst.node(k,0),inst.release[k]-phi[k]) for k in range(inst.K)]+[a for a in inst.fixed_arcs() if a[0]!='0']
    S=[A[i][0] if sel[i]==1 else A[i][1] for i in range(len(A))]
    D=[(inst.node(k,inst.R-1),'n',inst.run[k][inst.R-1]-due[k]) for k in range(inst.K)]
    arcs=F+S+D; L=rs.longest_path(arcs)['n']
    out=[]
    for k in range(inst.K):
        d=rs.longest_path(arcs, source=inst.node(k,0))
        if d is not None and abs((inst.release[k]-phi[k])+d['n']-L)<1e-6: out.append(k)
    return out
if __name__=='__main__':
    specs=[(k,s,seed) for seed in (1,2,3,4) for k,s in ((3,2),(4,2),(5,2),(5,3),(6,2))]
    print(f"{'inst':<8}{'L0':>6}{'bind':>8} | budget  uniform targeted  verdict")
    tot=0; hyp=0; better=0; equal=0; worse=0; worse_hyp=0; rows=[]
    for K,s,seed in specs:
        inst=rs.Instance(K,s,seed=seed); zero=[0]*K
        L0,sel0,st0=solve(inst,zero); b=binding_release_trains(inst,zero,sel0)
        single=(len(b)==1)
        for Phi in (4,8):
            tot+=1
            uni=[Phi/K]*K; Lu,_,_=solve(inst,uni)
            tgt=[0]*K
            if b: tgt[b[0]]=Phi          # target the (first) binding train
            Lt,selt,_=solve(inst,tgt)
            if Lt<Lu-1e-6: v='targeted better'; better+=1
            elif abs(Lt-Lu)<1e-6: v='equal'; equal+=1
            else: v='targeted WORSE'; worse+=1; worse_hyp+= single
            if single: hyp+=1
            rows.append((f"K{K}s{s}#{seed}",L0,b,Phi,Lu,Lt,v,single))
            print(f"K{K}s{s}#{seed:<2}{L0:>6}{str(b):>8} | {Phi:>5}  {Lu:>7}  {Lt:>8}  {v}{'' if single else '  [hypothesis fails: %d binding]'%len(b)}")
    print(f"\nTotal cases {tot}: single-binding hypothesis holds in {hyp}; targeted better {better}, equal {equal}, worse {worse} (worse while hypothesis holds: {worse_hyp})")
    import csv; csv.writer(open('slack_bench.csv','w')).writerows([('inst','L0','binding','budget','uniform','targeted','verdict','single_binding')]+rows)

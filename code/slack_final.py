import railsched as rs, csv
from slack_bench import solve, binding_release_trains
specs=[(k,s,seed) for seed in (1,2,3,4) for k,s in ((3,2),(4,2),(5,2),(5,3),(6,2))]
def seq_rule(inst,Phi,step=1.0):
    """Sequential targeting: give slack in unit steps to the (first) currently binding train."""
    K=inst.K; phi=[0.0]*K; used=0.0
    while used<Phi-1e-9:
        L,sel,_=solve(inst,phi); bs=binding_release_trains(inst,phi,sel)
        if not bs:   # tie among several binding arcs: split one step among all trains on longest paths
            # find all trains whose arc is on SOME longest path: remove pairs is costly; fall back to uniform step
            for k in range(K): phi[k]+=step/K
        else: phi[bs[0]]+=step
        used+=step
    return solve(inst,phi)[0]
rows=[]; strict_hold=0; better=equal=worse=0; sbetter=sequal=sworse=0; worse_with_hyp=0
for K,s,seed in specs:
    inst=rs.Instance(K,s,seed=seed); L0,sel0,_=solve(inst,[0]*K); b=binding_release_trains(inst,[0]*K,sel0)[0]
    for Phi in (4,8):
        Lu=solve(inst,[Phi/K]*K)[0]; tgt=[0]*K; tgt[b]=Phi; Lt=solve(inst,tgt)[0]; Ls=seq_rule(inst,Phi)
        hyp=all(binding_release_trains(inst,[(1-th)*Phi/K+(th*Phi if k==b else 0) for k in range(K)],solve(inst,[(1-th)*Phi/K+(th*Phi if k==b else 0) for k in range(K)])[1])==[b] for th in (0,0.25,0.5,0.75,1.0))
        strict_hold+=hyp
        v='better' if Lt<Lu-1e-6 else ('equal' if abs(Lt-Lu)<1e-6 else 'worse')
        if v=='better': better+=1
        elif v=='equal': equal+=1
        else: worse+=1; worse_with_hyp+=hyp
        vs='better' if Ls<Lu-1e-6 else ('equal' if abs(Ls-Lu)<1e-6 else 'worse')
        sbetter+=vs=='better'; sequal+=vs=='equal'; sworse+=vs=='worse'
        rows.append((f"K{K}s{s}#{seed}",Phi,L0,b,round(Lu,3),round(Lt,3),round(Ls,3),hyp,v,vs))
print(f"single-binding hypothesis holds STRICTLY along segment: {strict_hold}/40")
print(f"single-target vs uniform: better {better}, equal {equal}, worse {worse}  (worse while hypothesis holds: {worse_with_hyp})")
print(f"sequential  vs uniform:   better {sbetter}, equal {sequal}, worse {sworse}")
csv.writer(open('slack_results.csv','w')).writerows([('inst','budget','L0','b','uniform','single_target','sequential','hyp_strict','single_vs_uniform','seq_vs_uniform')]+rows)
for r in rows: print(r)

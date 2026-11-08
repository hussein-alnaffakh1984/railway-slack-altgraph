import railsched as rs, pulp, re, time, sys
def solve_log(inst, tl, tag):
    # replicate railsched.solve_milp but capture CBC log for proof status and bound
    A=inst.alt_pairs(); F=inst.fixed_arcs()
    nodes=sorted({x for u,v,w in F for x in (u,v)}|{u for p in A for a in p for u in a[:2]}|{'n'})
    M=sum(sum(r) for r in inst.run)+max(inst.release)+10
    m=pulp.LpProblem("C",pulp.LpMinimize); t={nd:pulp.LpVariable(f"t_{nd}",lowBound=0) for nd in nodes}
    x=[pulp.LpVariable(f"x{i}",cat="Binary") for i in range(len(A))]
    m+=t['n']; m+=t['0']==0
    for u,v,w in F: m+=t[v]-t[u]>=w
    for i,(e1,e2) in enumerate(A):
        m+=t[e1[1]]-t[e1[0]]>=e1[2]-M*(1-x[i]); m+=t[e2[1]]-t[e2[0]]>=e2[2]-M*x[i]
    log=f"cbc_{tag}.log"; t0=time.time(); m.solve(pulp.PULP_CBC_CMD(msg=0,timeLimit=tl,logPath=log)); el=time.time()-t0
    L=open(log).read()
    proven="Optimal solution found" in L and "Stopped on time" not in L
    mo=re.search(r"Objective value:\s*([\d.]+)",L); mb=re.search(r"Lower bound:\s*([\d.]+)",L); gap=re.search(r"Gap:\s*([\d.]+)",L)
    return round(pulp.value(m.objective)), proven, mb.group(1) if mb else None, el
for K,s in [(7,2),(8,2),(9,2),(10,2)]:
    inst=rs.Instance(K,s,seed=1)
    val,proven,lb,el=solve_log(inst,300,f"K{K}s{s}")
    print(f"K{K}s2 seed1: best={val} proven={proven} lower_bound={lb} time={el:.0f}s",flush=True)

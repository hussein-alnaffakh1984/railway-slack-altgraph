import railsched as rs, time
# Seconds-calibrated corridor: 6 trains, 2 segments; running 120-300 s per section, dwell 30-90 s, releases over a 600 s window.
inst=rs.Instance(6,2,seed=11,span=600,run=(120,300),dwell=(30,90))
A=inst.alt_pairs()
t0=time.time(); opt,sel,st=rs.solve_milp(inst,time_limit=90); tm=time.time()-t0
a,_=rs.solve_amcc(inst); f,_=rs.solve_fcfs(inst)
print(f"realistic: K=6 |A|={len(A)} Cmax={opt} s status={st} milp_time={tm:.1f}s  AMCC={a} ({100*(a-opt)/opt:.1f}%)  FCFS={f} ({100*(f-opt)/opt:.1f}%)")
# --- sensitivity of the optimal (= FCFS) selection: flip one pair at a time ---
A=inst.alt_pairs(); F=inst.fixed_arcs(); val,sel=rs.solve_fcfs(inst)
d=rs.longest_path(F+[A[i][sel[i]] for i in range(len(A))])
waits=[d[inst.node(k,inst.R-1)]+inst.run[k][-1]-(inst.release[k]+sum(inst.run[k])) for k in range(inst.K)]
inf=0; worse=[]
for i in range(len(A)):
    s2=list(sel); s2[i]=1-s2[i]; g=rs.longest_path(F+[A[j][s2[j]] for j in range(len(A))])
    if g is None: inf+=1
    else: worse.append(g['n'])
print(f"delay vs unconstrained completion per train: {waits} (max {max(waits)}); flipping one pair: {inf} infeasible, others -> {sorted(worse)}")

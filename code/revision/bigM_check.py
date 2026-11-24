"""Big-M validity (paper, Section 3.4).  Bound: in the earliest schedule of any feasible selection every
event time lies in [t_lo, t_hi] with t_hi = max source-arc weight + sum of all positive non-source fixed
weights (a longest path is a simple path) and t_lo = min(0, min source-arc weight).  Hence
M >= t_hi - t_lo makes every deselected inequality vacuous without removing any feasible schedule.
We verify (i) that the M used in the original runs satisfies the bound and (ii) that the optima are
unchanged when M is multiplied by 2 and by 10."""
import sys, pulp; sys.path.insert(0, '..')
import railsched as rs
def milp(inst, M):
    F = inst.fixed_arcs(); A = inst.alt_pairs()
    nodes = sorted({x for u, v, w in F for x in (u, v)} | {'0', 'n'})
    m = pulp.LpProblem("c", pulp.LpMinimize); t = {nd: pulp.LpVariable(f"t_{nd}") for nd in nodes}
    x = [pulp.LpVariable(f"x{i}", cat="Binary") for i in range(len(A))]
    m += t['n']; m += t['0'] == 0
    for u, v, w in F: m += t[v] - t[u] >= w
    for i, (e1, e2) in enumerate(A):
        m += t[e1[1]] - t[e1[0]] >= e1[2] - M * (1 - x[i]); m += t[e2[1]] - t[e2[0]] >= e2[2] - M * x[i]
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60, threads=1)); return round(pulp.value(m.objective))
ok = True
for seed in (1, 2, 3, 4):
    for K, s in ((3, 2), (4, 2), (5, 2), (5, 3), (6, 2)):
        inst = rs.Instance(K, s, seed=seed)
        bound = max(inst.release) + sum(sum(r) for r in inst.run)            # t_hi - t_lo with t_lo = 0
        M_used = inst.release[-1] + sum(sum(r) for r in inst.run) + 10
        bb = rs.BnB(inst, propagate=True).solve()[0]
        v = [milp(inst, f * M_used) for f in (1, 2, 10)]
        good = M_used >= bound and len(set(v)) == 1 and v[0] == bb; ok &= good
        print(f"K{K}s{s}#{seed}: bound {bound}, M used {M_used}, optimum with M,2M,10M = {v}, branch-and-bound {bb}  {'ok' if good else 'MISMATCH'}")
print("all 20 instances: M valid and optimum independent of M and equal to branch-and-bound:", ok)

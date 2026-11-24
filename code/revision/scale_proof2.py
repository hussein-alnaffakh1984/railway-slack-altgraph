"""Larger corridors (supplement S6): proof status is read from the CBC log, never from the status code."""
import sys, re, time, csv, pulp; sys.path.insert(0, '..')
import railsched as rs
def solve_log(inst, tl, tag):
    A = inst.alt_pairs(); F = inst.fixed_arcs()
    nodes = sorted({x for u, v, w in F for x in (u, v)} | {'0', 'n'})
    M = sum(sum(r) for r in inst.run) + max(inst.release) + 10
    m = pulp.LpProblem("C", pulp.LpMinimize); t = {nd: pulp.LpVariable(f"t_{nd}", lowBound=0) for nd in nodes}
    x = [pulp.LpVariable(f"x{i}", cat="Binary") for i in range(len(A))]
    m += t['n']; m += t['0'] == 0
    for u, v, w in F: m += t[v] - t[u] >= w
    for i, (e1, e2) in enumerate(A):
        m += t[e1[1]] - t[e1[0]] >= e1[2] - M * (1 - x[i]); m += t[e2[1]] - t[e2[0]] >= e2[2] - M * x[i]
    log = f"logs/cbc_{tag}.log"; t0 = time.time(); m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=tl, threads=1, logPath=log)); el = time.time() - t0
    L = open(log).read()
    proven = "Optimal solution found" in L and "Stopped on time" not in L
    mb = re.search(r"Lower bound:\s*([\d.]+)", L)
    return round(pulp.value(m.objective)), proven, (mb.group(1) if mb else ''), round(el, 1), len(A)
import os; os.makedirs('logs', exist_ok=True); rows = []
for K, s, seed in [(7, 2, 1), (8, 2, 1), (9, 2, 1), (10, 2, 1)]:
    inst = rs.Instance(K, s, seed=seed); val, proven, lb, el, nA = solve_log(inst, 300, f"K{K}s{s}_seed{seed}")
    rows.append((f"K{K}s{s}#{seed}", K, nA, val, lb if not proven else '', 'proven optimal' if proven else 'time limit, not proven', el)); print(rows[-1], flush=True)
csv.writer(open('larger_corridors.csv', 'w', newline='')).writerows([('inst', 'trains', 'pairs', 'best_value', 'lower_bound', 'status', 'seconds')] + rows)

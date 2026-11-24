"""Plain versus propagation branch-and-bound (supplement, Table S5): nodes and wall-clock time in ms.
Both start from the AMCC incumbent; the plain search is capped at 400,000 nodes (a capped run is NOT a proof)."""
import sys, time, csv; sys.path.insert(0, '..')
import railsched as rs
rows = []
for K, s, seed in [(4, 2, 1), (5, 2, 1), (5, 2, 2), (6, 2, 1), (5, 3, 1), (6, 2, 2), (6, 3, 7), (7, 2, 7)]:
    inst = rs.Instance(K, s, seed=seed); ub, sel = rs.solve_amcc(inst)
    res = []
    for prop in (False, True):
        b = rs.BnB(inst, propagate=prop); t0 = time.perf_counter()
        val, _, nodes = b.solve(init_ub=ub, init_sel=sel, max_nodes=400000); ms = 1000 * (time.perf_counter() - t0)
        res.append((val, nodes, ms, b.aborted))
    (v0, n0, t0_, a0), (v1, n1, t1_, a1) = res
    rows.append((f"K{K}s{s}#{seed}", len(inst.alt_pairs()), ub, v1, n0, round(t0_, 1), 'capped, not proven' if a0 else 'proven', v0, n1, round(t1_, 1), 'proven' if not a1 else 'capped', round(n0 / n1, 1)))
    print(rows[-1], flush=True)
csv.writer(open('bnb_table.csv', 'w', newline='')).writerows([('inst', 'pairs', 'amcc_start', 'optimum', 'plain_nodes', 'plain_ms', 'plain_status', 'plain_best', 'prop_nodes', 'prop_ms', 'prop_status', 'node_ratio')] + rows)

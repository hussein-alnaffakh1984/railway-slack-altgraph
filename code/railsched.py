"""
railsched.py  --  Alternative-graph train scheduling engine.

Models a UNIDIRECTIONAL corridor of resources in series. Odd-indexed resources
are single-track SEGMENTS (capacity 1, blocking) and even-indexed resources are
STATIONS / passing loops (uncapacitated -> overtaking allowed). All trains share
the route; conflicts arise on segments. Blocking semantics: a train releases a
segment only when it enters the next resource.

Provides: generator, longest-path + positive-cycle detection, exact MILP (CBC),
baseline branch-and-bound, propagation branch-and-bound (novel), AMCC heuristic,
FCFS heuristic, and the SRMO robust-optimal criterion (novel).
"""
import itertools, random, time
import networkx as nx


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------
class Instance:
    def __init__(self, n_trains, n_seg, seed=0, span=40, run=(8, 22), dwell=(2, 6)):
        rng = random.Random(seed)
        self.K = n_trains
        # resource layout: loop, seg, loop, seg, ..., seg, loop
        self.layout = []
        for s in range(n_seg):
            self.layout.append('loop'); self.layout.append('seg')
        self.layout.append('loop')
        self.R = len(self.layout)
        self.release = sorted(rng.randint(0, span) for _ in range(n_trains))
        self.run = [[rng.randint(*run) if self.layout[r] == 'seg'
                     else rng.randint(*dwell) for r in range(self.R)]
                    for _ in range(n_trains)]
        self.seed = seed

    def node(self, k, r): return f"{k}_{r}"

    def succ(self, k, r):
        return self.node(k, r + 1) if r < self.R - 1 else 'n'

    def fixed_arcs(self):
        F = []
        for k in range(self.K):
            F.append(('0', self.node(k, 0), self.release[k]))
            for r in range(self.R):
                F.append((self.node(k, r), self.succ(k, r), self.run[k][r]))
        return F

    def alt_pairs(self, headway=0):
        """Blocking alternative pairs on every segment, for every train couple."""
        A = []
        for r in range(self.R):
            if self.layout[r] != 'seg':
                continue
            for u, v in itertools.combinations(range(self.K), 2):
                su, sv = self.succ(u, r), self.succ(v, r)
                e1 = (su, self.node(v, r), headway)   # u before v
                e2 = (sv, self.node(u, r), headway)   # v before u
                A.append((e1, e2))
        return A

    def due_dates(self, allowance=1.5):
        """A simple due date per train = release + ideal travel * allowance."""
        d = []
        for k in range(self.K):
            ideal = self.release[k] + sum(self.run[k])
            d.append(int(round(ideal * 1.0 + (ideal - self.release[k]) * (allowance - 1.0))))
        return d


# ----------------------------------------------------------------------
# Longest path with positive-cycle detection (Bellman-Ford)
# ----------------------------------------------------------------------
def longest_path(arcs, source='0'):
    nodes = {x for u, v, w in arcs for x in (u, v)} | {source}
    NEG = float('-inf')
    d = {x: NEG for x in nodes}; d[source] = 0
    n = len(nodes)
    for _ in range(n - 1):
        changed = False
        for u, v, w in arcs:
            if d[u] != NEG and d[u] + w > d[v]:
                d[v] = d[u] + w; changed = True
        if not changed:
            break
    for u, v, w in arcs:                       # positive-cycle check
        if d[u] != NEG and d[u] + w > d[v]:
            return None
    return d


def makespan_of(inst, selection, headway=0):
    """selection: list of 0/1 choosing arc index per alternative pair."""
    A = inst.alt_pairs(headway)
    arcs = inst.fixed_arcs() + [A[i][selection[i]] for i in range(len(A))]
    d = longest_path(arcs)
    return None if d is None else d['n']


# ----------------------------------------------------------------------
# Exact MILP (CBC via PuLP)
# ----------------------------------------------------------------------
def solve_milp(inst, headway=0, time_limit=30):
    import pulp
    F = inst.fixed_arcs(); A = inst.alt_pairs(headway)
    nodes = sorted({x for u, v, w in F for x in (u, v)} |
                   {x for e1, e2 in A for arc in (e1, e2) for x in (arc[0], arc[1])} | {'0', 'n'})
    M = inst.release[-1] + sum(sum(inst.run[k]) for k in range(inst.K)) + 10
    prob = pulp.LpProblem("altgraph", pulp.LpMinimize)
    t = {nd: pulp.LpVariable(f"t_{nd}", lowBound=0) for nd in nodes}
    x = {p: pulp.LpVariable(f"x_{p}", cat="Binary") for p in range(len(A))}
    prob += t['n']
    prob += t['0'] == 0
    for u, v, w in F:
        prob += t[v] - t[u] >= w
    for p, (e1, e2) in enumerate(A):
        (i, j, a1), (h, k, a2) = e1, e2
        prob += t[j] - t[i] >= a1 - M * (1 - x[p])
        prob += t[k] - t[h] >= a2 - M * x[p]
    t0 = time.perf_counter()
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit))
    rt = time.perf_counter() - t0
    return round(pulp.value(prob.objective)), rt, pulp.LpStatus[prob.status]


# ----------------------------------------------------------------------
# Branch-and-Bound  (baseline and propagation variants)
# ----------------------------------------------------------------------
class BnB:
    """Exact branch-and-bound for the alternative graph.
    propagate=False : longest-path lower bound + positive-cycle pruning only.
    propagate=True  : adds SOUND incumbent-based forced-arc propagation
                      (if one arc of a pair cannot improve on the incumbent or
                      creates a cycle, the other arc is logically forced)."""
    def __init__(self, inst, headway=0, propagate=False):
        self.inst = inst
        self.A = inst.alt_pairs(headway)
        self.F = inst.fixed_arcs()
        self.propagate = propagate
        self.nodes_explored = 0

    def _dist(self, chosen):
        arcs = self.F + [self.A[i][chosen[i]] for i in chosen]
        return longest_path(arcs)

    def _propagate(self, chosen):
        """Sound: force the surviving arc whenever the other is dominated/cyclic."""
        changed = True
        while changed:
            changed = False
            for p in range(len(self.A)):
                if p in chosen:
                    continue
                d0 = self._dist({**chosen, p: 0})
                d1 = self._dist({**chosen, p: 1})
                dead0 = (d0 is None) or (d0['n'] >= self.best)
                dead1 = (d1 is None) or (d1['n'] >= self.best)
                if dead0 and dead1:
                    return None                      # node cannot improve
                if dead0 and not dead1:
                    chosen[p] = 1; changed = True
                elif dead1 and not dead0:
                    chosen[p] = 0; changed = True
        return chosen

    def solve(self, init_ub=None, init_sel=None, max_nodes=None):
        self.best = init_ub if init_ub is not None else float('inf')
        self.best_sel = ({i: init_sel[i] for i in range(len(self.A))}
                         if init_sel is not None else None)
        self.max_nodes = max_nodes
        self.aborted = False
        self._rec({})
        sel = [self.best_sel[i] for i in range(len(self.A))]
        return self.best, sel, self.nodes_explored

    def _rec(self, chosen):
        if self.max_nodes is not None and self.nodes_explored >= self.max_nodes:
            self.aborted = True
            return
        self.nodes_explored += 1
        if self.propagate:
            chosen = self._propagate(dict(chosen))
            if chosen is None:
                return
        d = self._dist(chosen)
        if d is None or d['n'] >= self.best:
            return
        unset = [p for p in range(len(self.A)) if p not in chosen]
        if not unset:
            self.best = d['n']; self.best_sel = dict(chosen)
            return
        p = unset[0]                                 # same branching for both variants
        c0 = self._dist({**chosen, p: 0}); c1 = self._dist({**chosen, p: 1})
        v0 = c0['n'] if c0 else float('inf'); v1 = c1['n'] if c1 else float('inf')
        for idx in ([0, 1] if v0 <= v1 else [1, 0]):
            self._rec({**chosen, p: idx})


# ----------------------------------------------------------------------
# Heuristics
# ----------------------------------------------------------------------
def solve_fcfs(inst, headway=0):
    """Fix every segment order by train release time (first-come-first-served)."""
    A = inst.alt_pairs(headway)
    # arc0 = 'u before v' with u<v ; choose 0 if release[u]<=release[v]
    sel = []
    idx = 0
    for r in range(inst.R):
        if inst.layout[r] != 'seg':
            continue
        for u, v in itertools.combinations(range(inst.K), 2):
            sel.append(0 if inst.release[u] <= inst.release[v] else 1)
            idx += 1
    return makespan_of(inst, sel, headway), sel


def solve_amcc(inst, headway=0):
    """AMCC: greedily fix the arc that avoids the largest current makespan."""
    A = inst.alt_pairs(headway)
    chosen = {}
    F = inst.fixed_arcs()
    def dist(ch):
        arcs = F + [A[i][ch[i]] for i in ch]
        return longest_path(arcs)
    while len(chosen) < len(A):
        best_pick = None; best_key = -1
        for p in range(len(A)):
            if p in chosen:
                continue
            c0 = dist({**chosen, p: 0}); c1 = dist({**chosen, p: 1})
            v0 = c0['n'] if c0 else float('inf')
            v1 = c1['n'] if c1 else float('inf')
            mx = max(v0, v1)                       # the value we want to avoid
            if mx > best_key:
                best_key = mx
                best_pick = (p, 0 if v0 <= v1 else 1)
        p, idx = best_pick
        chosen[p] = idx
    sel = [chosen[i] for i in range(len(A))]
    return makespan_of(inst, sel, headway), sel


# ----------------------------------------------------------------------
# Robustness:  stability radius and the novel SRMO criterion
# ----------------------------------------------------------------------
def stability_radius(inst, selection, due, headway=0):
    A = inst.alt_pairs(headway)
    arcs = inst.fixed_arcs() + [A[i][selection[i]] for i in range(len(A))]
    d = longest_path(arcs)
    if d is None:
        return None, None
    Lk = [d[inst.node(k, inst.R - 1)] + inst.run[k][inst.R - 1] for k in range(inst.K)]
    slack = [due[k] - Lk[k] for k in range(inst.K)]
    return min(slack), slack


def srmo(inst, due, headway=0, eps=0):
    """Stability-Radius-Maximising Optimum: among makespan-optimal selections,
    return the one with the largest stability radius. Exact via enumeration of
    optimal selections found by a bounded search (small instances)."""
    A = inst.alt_pairs(headway)
    opt, _, _ = BnB(inst, headway, propagate=True).solve()
    best_sigma = -float('inf'); best_sel = None; n_opt = 0
    for combo in itertools.product([0, 1], repeat=len(A)):
        mk = makespan_of(inst, combo, headway)
        if mk is not None and mk <= opt + eps:
            n_opt += 1
            sigma, _ = stability_radius(inst, combo, due, headway)
            if sigma is not None and sigma > best_sigma:
                best_sigma = sigma; best_sel = combo
    return opt, best_sigma, best_sel, n_opt

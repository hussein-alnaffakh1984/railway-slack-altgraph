"""
ag.py -- generic alternative-graph engine used for the revision experiments.

An instance is described by
  fixed : list of (u, v, w)            arcs present in every schedule (routing, release, dwell)
  flex  : list of (name, node, d)      flexible departure arcs (0 -> node) of weight d - phi
  pairs : list of ((u,v,w),(u,v,w))    alternative pairs (exactly one arc is selected)
  due   : list of (v, w)               arcs (v -> n) of weight w  (objective = longest 0-n path)
Source is '0', sink is 'n'. All data are integers; allocations phi are Fractions.
Every MILP is solved on integer-scaled data so that optimal values are integers and can be
rounded safely; every value returned by CBC is re-evaluated exactly by longest paths.
"""
from fractions import Fraction as Fr
import itertools, math, os, tempfile
import pulp

NEG = float('-inf')


def longest(arcs, source='0'):
    """Bellman-Ford longest paths; returns None when a positive cycle is reachable."""
    nodes = {x for u, v, w in arcs for x in (u, v)} | {source}
    d = {x: NEG for x in nodes}
    d[source] = 0
    for _ in range(len(nodes)):
        ch = False
        for u, v, w in arcs:
            if d[u] != NEG and d[u] + w > d[v]:
                d[v] = d[u] + w
                ch = True
        if not ch:
            return d
    return None


class AG:
    max_solve_seconds = 0.0      # longest single CBC call in this process (time limit is 120 s)
    n_solves = 0
    def __init__(self, fixed, flex, pairs, due, name=''):
        self.fixed, self.flex, self.pairs, self.due, self.name = list(fixed), list(flex), list(pairs), list(due), name
        self.m = len(flex)
        self.nodes = sorted({x for u, v, w in fixed for x in (u, v)} | {f[1] for f in flex}
                            | {x for p in pairs for a in p for x in a[:2]} | {v for v, w in due} | {'0', 'n'})

    # ---------- exact evaluation of one selection --------------------------------
    def arcs(self, phi, sel):
        A = list(self.fixed) + [('0', nd, d - phi[i]) for i, (nm, nd, d) in enumerate(self.flex)]
        A += [self.pairs[i][s] for i, s in enumerate(sel)]
        A += [(v, 'n', w) for v, w in self.due]
        return A

    def value(self, phi, sel):
        d = longest(self.arcs(phi, sel))
        return None if d is None else d['n']

    def beta(self, phi, sel):
        """beta_k = weight of flex arc k + longest path from its head to n (in G(sel)); and L."""
        arcs = self.arcs(phi, sel)
        L = longest(arcs)['n']
        out = []
        for i, (nm, nd, d) in enumerate(self.flex):
            dd = longest(arcs, source=nd)
            out.append((d - phi[i]) + dd['n'] if dd['n'] != NEG else NEG)
        return L, out

    # ---------- big-M (see paper, Section 3.4) -----------------------------------
    def bigM(self, phimax=0):
        src = [w for u, v, w in self.fixed if u == '0'] + [d for nm, nd, d in self.flex]
        pos = sum(w for u, v, w in self.fixed if u != '0' and w > 0)
        upper = max(src) + pos                      # every event time is <= upper
        lower = min(min(src) - phimax, 0)           # every event time is >= lower
        return upper - lower + 1

    # ---------- MILP -------------------------------------------------------------
    def _model(self, w_flex, scale, sense=pulp.LpMinimize, Mfac=1):
        """w_flex: list of flex-arc weights (Fractions) or None when phi are variables."""
        sc = lambda z: self._int(z * scale)
        M = sc(self.bigM(phimax=max([0] + [f[2] - w for f, w in zip(self.flex, w_flex)]) if w_flex else 0)) * Mfac
        m = pulp.LpProblem("ag", sense)
        t = {nd: pulp.LpVariable(f"t_{i}") for i, nd in enumerate(self.nodes)}
        x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(self.pairs))]
        m += t['0'] == 0
        for u, v, w in self.fixed:
            m += t[v] - t[u] >= sc(w)
        if w_flex is not None:
            for (nm, nd, d), w in zip(self.flex, w_flex):
                m += t[nd] - t['0'] >= sc(w)
        for i, (e1, e2) in enumerate(self.pairs):
            m += t[e1[1]] - t[e1[0]] >= sc(e1[2]) - M * x[i]          # x=0 selects arc 0
            m += t[e2[1]] - t[e2[0]] >= sc(e2[2]) - M * (1 - x[i])    # x=1 selects arc 1
        for v, w in self.due:
            m += t['n'] - t[v] >= sc(w)
        return m, t, x, M

    @staticmethod
    def _int(z):
        z = Fr(z)
        assert z.denominator == 1, f"scaling does not make data integral: {z}"
        return int(z)

    @staticmethod
    def _solve(m, tl=120):
        import time
        t0 = time.perf_counter()
        m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=tl, threads=1))
        AG.max_solve_seconds = max(AG.max_solve_seconds, time.perf_counter() - t0)
        AG.n_solves += 1
        return pulp.LpStatus[m.status]

    def solve(self, phi, scale=1, Mfac=1):
        """Exact optimum L*(phi) (a Fraction) and one optimal selection."""
        w = [Fr(d) - Fr(p) for (nm, nd, d), p in zip(self.flex, phi)]
        m, t, x, M = self._model(w, scale, Mfac=Mfac)
        m += t['n']
        st = self._solve(m)
        assert st == 'Optimal', st
        sel = [int(round(v.value())) for v in x]
        val = self.value([Fr(p) for p in phi], sel)        # exact re-evaluation
        assert val is not None and abs(float(val) * scale - pulp.value(m.objective)) < 0.5, (val, pulp.value(m.objective))
        return Fr(val), sel

    def binding_in_some_optimum(self, phi, L, ks, scale=1):
        """True iff some optimal selection at phi has a longest 0-n path through a flex arc k in ks.
        MILP: choose a selection whose earliest schedule has value <= L and a unit 0-n flow that
        leaves the source on an arc of ks; maximize the flow's weight (<= L, with equality iff binding)."""
        w = [Fr(d) - Fr(p) for (nm, nd, d), p in zip(self.flex, phi)]
        m, t, x, M = self._model(w, scale, sense=pulp.LpMaximize)
        sc = lambda z: self._int(Fr(z) * scale)
        m += t['n'] <= sc(L)
        arcs = [(u, v, sc(wt), None) for u, v, wt in self.fixed if u != '0']
        arcs += [('0', self.flex[k][1], sc(w[k]), None) for k in ks]
        for i, (e1, e2) in enumerate(self.pairs):
            arcs.append((e1[0], e1[1], sc(e1[2]), (i, 0)))
            arcs.append((e2[0], e2[1], sc(e2[2]), (i, 1)))
        arcs += [(v, 'n', sc(wt), None) for v, wt in self.due]
        y = [pulp.LpVariable(f"y_{j}", lowBound=0, upBound=1) for j in range(len(arcs))]
        for j, (u, v, wt, tag) in enumerate(arcs):
            if tag is not None:
                i, s = tag
                m += y[j] <= (1 - x[i] if s == 0 else x[i])
        for nd in self.nodes:
            out = pulp.lpSum(y[j] for j, a in enumerate(arcs) if a[0] == nd)
            inn = pulp.lpSum(y[j] for j, a in enumerate(arcs) if a[1] == nd)
            if nd == '0':
                m += out == 1
            elif nd == 'n':
                m += inn == 1
            else:
                m += out - inn == 0
        m += pulp.lpSum(a[2] * y[j] for j, a in enumerate(arcs))
        st = self._solve(m)
        if st == 'Infeasible':
            return False
        assert st == 'Optimal', st
        z = pulp.value(m.objective)
        assert z <= sc(L) + 0.5, (z, sc(L))
        return z > sc(L) - 0.5

    def optimal_allocation(self, Phi, ub=None):
        """min over phi >= 0, sum phi = Phi of L*(phi). Returns (value, phi) as floats (LP optimum)."""
        m, t, x, M = self._model(None, 1)
        M2 = self.bigM(phimax=Phi)
        # rebuild with a big-M valid for the largest possible advance
        m = pulp.LpProblem("alloc", pulp.LpMinimize)
        t = {nd: pulp.LpVariable(f"t_{i}") for i, nd in enumerate(self.nodes)}
        x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(self.pairs))]
        ph = [pulp.LpVariable(f"phi_{i}", lowBound=0, upBound=(ub[i] if ub else None)) for i in range(self.m)]
        m += t['n']
        m += t['0'] == 0
        m += pulp.lpSum(ph) == Phi
        for u, v, w in self.fixed:
            m += t[v] - t[u] >= w
        for (nm, nd, d), p in zip(self.flex, ph):
            m += t[nd] - t['0'] >= d - p
        for i, (e1, e2) in enumerate(self.pairs):
            m += t[e1[1]] - t[e1[0]] >= e1[2] - M2 * x[i]
            m += t[e2[1]] - t[e2[0]] >= e2[2] - M2 * (1 - x[i])
        for v, w in self.due:
            m += t['n'] - t[v] >= w
        st = self._solve(m)
        assert st == 'Optimal', st
        return pulp.value(m.objective), [p.value() for p in ph]

    # ---------- brute force (small instances only) -------------------------------
    def enumerate(self, phi):
        """All feasible selections with their exact values: list of (value, sel)."""
        out = []
        for sel in itertools.product((0, 1), repeat=len(self.pairs)):
            v = self.value(phi, sel)
            if v is not None:
                out.append((v, sel))
        return out


# ---------- transfer segment and the finite certificate ---------------------------
def segment(m, Phi, b, theta):
    """psi(theta) for the uniform start phi_k = Phi/m and target b."""
    th = Fr(theta)
    return [Fr(Phi, m) * (1 - th) + (Fr(Phi) * th if k == b else 0) for k in range(m)]


def certificate(ag, Phi, b, binding_test, value_fn):
    """Exact check of the hypothesis of Theorem 1 on the whole segment (Proposition 2 of the paper):
    it suffices to test the grid theta = j/(m*Phi), j = 0..m*Phi.
    Returns (holds, first_failing_theta, g_values)."""
    m = ag.m
    others = [k for k in range(m) if k != b]
    g = {}
    for j in range(m * Phi + 1):
        th = Fr(j, m * Phi)
        phi = segment(m, Phi, b, th)
        L = value_fn(phi)
        g[th] = L
        if binding_test(phi, L, others):
            return False, th, g
    return True, None, g

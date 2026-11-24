"""Instance families for the revision experiments (all data integer, times in seconds/time units)."""
import random, itertools, sys
sys.path.insert(0, '..')
from ag import AG


def route_instance(trains, name=''):
    """trains: list of dict(name, release, steps=[(resource, time), ...], flex=(step_index, d) or None,
    due={step_index_or_'exit': due_time}).  Consecutive steps on the same resource are one occupation
    (e.g. run-in and dwell on a platform track). Unit capacity, blocking: a train holds a resource until
    it enters the next one (or exits)."""
    fixed, flex, due, occ = [], [], [], {}
    for T in trains:
        nm, st = T['name'], T['steps']
        node = lambda i, nm=nm, st=st: f"{nm}{i}" if i < len(st) else f"{nm}*"
        fixed.append(('0', node(0), T['release']))
        for i, (r, p) in enumerate(st):
            fixed.append((node(i), node(i + 1), p))
        # occupations: (resource, entry node, release node)
        i = 0
        while i < len(st):
            j = i
            while j + 1 < len(st) and st[j + 1][0] == st[i][0]:
                j += 1
            occ.setdefault(st[i][0], []).append((nm, node(i), node(j + 1)))
            i = j + 1
        if T.get('flex'):
            si, d = T['flex']
            flex.append((nm, node(si), d))
        for key, tau in T.get('due', {}).items():
            due.append((node(len(st)) if key == 'exit' else node(key), tau))
    pairs = []
    for r, lst in sorted(occ.items(), key=lambda z: str(z[0])):
        for (h, hin, hout), (k, kin, kout) in itertools.combinations(lst, 2):
            pairs.append(((hout, kin, 0), (kout, hin, 0)))      # arc 0: h before k ; arc 1: k before h
    return trains, fixed, flex, pairs, due


def finish(trains, fixed, flex, pairs, due, name=''):
    """Turn planned due times into modified due dates max{tau, a} with a the conflict-free time at phi=0."""
    from ag import longest
    free = longest(list(fixed) + [('0', nd, d) for nm, nd, d in flex])
    duearcs = [(v, -max(tau, free[v])) for v, tau in due]
    return AG(fixed, flex, pairs, duearcs, name)


def dariano(delA=47, delB=0, delC=17, runs=None, name='published'):
    """Station instance of D'Ariano, Pacciarelli, Pranzo (2005), Table-1 weights (see paper, Section 4)."""
    r = runs or dict(A3=12, A4=10, A8=15, B3=10, B4=10, B8=15, C6=25, C7=25, C8=15)
    trains = [
        dict(name='A', release=60 + delA, steps=[(3, r['A3']), (4, r['A4']), (4, 20), (8, r['A8'])],
             flex=(3, 115), due={2: 95, 'exit': 130}),
        dict(name='B', release=95 + delB, steps=[(3, r['B3']), (4, r['B4']), (4, 20), (8, r['B8'])],
             flex=(3, 160), due={2: 115, 'exit': 175}),
        dict(name='C', release=95 + delC, steps=[(6, r['C6']), (7, r['C7']), (8, r['C8'])],
             due={'exit': 160}),
    ]
    return finish(*route_instance(trains), name=name)


def perturbed_station(seed):
    """Random perturbation of the published station: entry delays and running times vary."""
    g = random.Random(seed)
    base = dict(A3=12, A4=10, A8=15, B3=10, B4=10, B8=15, C6=25, C7=25, C8=15)
    runs = {k: max(1, round(v * g.uniform(0.8, 1.2))) for k, v in base.items()}
    return dariano(delA=g.randint(0, 70), delB=g.randint(0, 20), delC=g.randint(0, 40), runs=runs,
                   name=f"station#{seed}")


def junction(seed):
    """Two platform tracks merging at a junction X into one exit block, plus a crossing freight train.
    U1,U2: a1 -> P1 (stop) -> X -> o1 ;  V1,V2: b1 -> P2 (stop) -> X -> o1 ;  W: c1 -> X -> o2.
    Following conflicts (a1,P1 / b1,P2), merging conflicts (X,o1) and a crossing conflict (X): 20 pairs."""
    g = random.Random(10_000 + seed)
    j = lambda v: max(1, round(v * g.uniform(0.8, 1.2)))
    dly = lambda: g.randint(10, 90) if g.random() < 0.7 else 0
    trains = []
    for nm, rel, a, plat in (('U1', 0, 'a1', 'P1'), ('U2', 100, 'a1', 'P1'), ('V1', 45, 'b1', 'P2'), ('V2', 145, 'b1', 'P2')):
        rel += g.randint(-15, 15) if rel else 0
        run_in, arr, dw, jx, out = j(30), j(20), 30, j(12), j(25)
        d = rel + run_in + arr + dw + 20                      # planned departure: 20 s hold after the minimum dwell
        trains.append(dict(name=nm, release=rel + dly(), steps=[(a, run_in), (plat, arr), (plat, dw), ('X', jx), ('o1', out)],
                           flex=(3, d), due={'exit': d + jx + out}))
    relw = 70 + g.randint(-20, 20); c1, x, o2 = j(40), j(20), j(30)
    trains.append(dict(name='W', release=relw + dly(), steps=[('c1', c1), ('X', x), ('o2', o2)], due={'exit': relw + c1 + x + o2 + 30}))
    return finish(*route_instance(trains), name=f"junction#{seed}")


def corridor(K, s, seed):
    """The synthetic corridor of railsched.Instance with the maximum-lateness objective;
    flexible arcs are the release arcs (departure from the origin station)."""
    import railsched as rs
    inst = rs.Instance(K, s, seed=seed)
    fixed = [(u, v, w) for u, v, w in inst.fixed_arcs() if u != '0' and v != 'n']
    flex = [(f"T{k}", inst.node(k, 0), inst.release[k]) for k in range(K)]
    duev = inst.due_dates()
    due = [(inst.node(k, inst.R - 1), inst.run[k][inst.R - 1] - duev[k]) for k in range(K)]
    return AG(fixed, flex, inst.alt_pairs(), due, name=f"K{K}s{s}#{seed}")

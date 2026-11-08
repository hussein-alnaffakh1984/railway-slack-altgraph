import itertools, random
from equiv import cmax_perm
# rank-one heterogeneous: p[j][i] = a_j * p_i
def cmax_opt_gen(p,rel,m): return min(cmax_perm(o,p,rel,m) for o in itertools.permutations(range(len(p))))
def carlier(p,rel,m):
    K=len(p); h=lambda j,i: rel[j]+sum(p[j][:i]); q=lambda j,i: sum(p[j][i+1:]); best=0
    for i in range(m):
        for S in range(1,K+1):
            for sub in itertools.combinations(range(K),S):
                best=max(best,min(h(j,i) for j in sub)+sum(p[j][i] for j in sub)+min(q(j,i) for j in sub))
    return best
def mk(a,pr): return [[a[j]*pr[i] for i in range(len(pr))] for j in range(len(a))]

random.seed(2)
def test(name, gen, trials=1500, K=4, m=3):
    f=0; ex=None
    for _ in range(trials):
        a,pr,rel=gen(K,m); p=mk(a,pr)
        c=cmax_opt_gen(p,rel,m); b=carlier(p,rel,m)
        if c!=b: f+=1; ex=ex or (a,pr,rel,c,b)
    print(f"{name:<50} fails {f}/{trials}")
    if ex: print("   e.g. a=%s p=%s rel=%s  Cmax=%d carlier=%d"%ex)
# generators
def g_general(K,m): return [random.randint(1,3) for _ in range(K)],[random.randint(1,5) for _ in range(m)],[random.randint(0,15) for _ in range(K)]
def g_rel0(K,m):    return [random.randint(1,3) for _ in range(K)],[random.randint(1,5) for _ in range(m)],[0]*K
def g_agreeable(K,m): # releases sorted ascending, speeds a_j sorted DEScending (fast/late agreeable)
    a=sorted((random.randint(1,3) for _ in range(K)),reverse=True); pr=[random.randint(1,5) for _ in range(m)]
    rel=sorted(random.randint(0,15) for _ in range(K)); return a,pr,rel
def g_agreeable2(K,m): # releases sorted asc, speeds sorted asc
    a=sorted(random.randint(1,3) for _ in range(K)); pr=[random.randint(1,5) for _ in range(m)]
    rel=sorted(random.randint(0,15) for _ in range(K)); return a,pr,rel
print("Is the Carlier bound exact for rank-one  p[j][i]=a_j*p_i ?\n")
test("(A) general rank-one (any a_j, any releases)", g_general)
test("(B) rank-one, releases = 0", g_rel0)
test("(C) rank-one, releases asc & speeds desc (agreeable)", g_agreeable)
test("(D) rank-one, releases asc & speeds asc", g_agreeable2)
import itertools
from equiv import cmax_perm

# ---- minimal counterexample search (self-contained) ----
best=None
for m in (2,3):
    for K in (2,3):
        for pr in itertools.product(range(1,4),repeat=m):
            for a in itertools.product(range(1,4),repeat=K):
                if len(set(a))==1: continue
                p=mk(a,list(pr)); rel=[0]*K
                c=cmax_opt_gen(p,rel,m); b=carlier(p,rel,m)
                if c>b and (best is None or (K,m,sum(pr)+sum(a))<best[0]): best=((K,m,sum(pr)+sum(a)),a,list(pr),c,b)
        if best: break
    if best: break
print("Minimal rank-one counterexample (rel=0): speeds a=%s profile p=%s  C_max=%d > bound=%d"%(best[1],best[2],best[3],best[4]))

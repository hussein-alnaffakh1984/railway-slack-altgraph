import itertools, random
# Series corridor = permutation BLOCKING flow shop (no overtaking, unit-capacity).
# Jobs (trains) in a fixed order traverse machines (resources) 1..m with proc p[j][i].
# Blocking recursion for a given job order:
def cmax_perm(order, p, rel, m):
    # t[pos][i] = start time of the job at sequence position 'pos' on machine i
    K=len(order)
    t=[[0]*m for _ in range(K)]
    for pos,j in enumerate(order):
        for i in range(m):
            lb = rel[j] if i==0 else t[pos][i-1]+p[j][i-1]   # finished previous machine
            if pos>0:
                prev=order[pos-1]
                if i<m-1:
                    lb=max(lb, t[pos-1][i+1])                 # machine i free: prev entered i+1
                else:
                    lb=max(lb, t[pos-1][i]+p[prev][i])        # last machine: prev completed
            t[pos][i]=lb
    last=order[-1]
    return max(t[pos][m-1]+p[order[pos]][m-1] for pos in range(K))
def cmax_opt(p, rel, m):
    K=len(p)
    return min(cmax_perm(o,p,rel,m) for o in itertools.permutations(range(K)))
def bound(p, rel, m):
    K=len(p)
    Lpath=max(rel[j]+sum(p[j]) for j in range(K))
    Lcut=0
    for i in range(m):
        h=min(rel[j]+sum(p[j][:i]) for j in range(K))
        q=min(sum(p[j][i+1:]) for j in range(K))
        Lcut=max(Lcut, h+sum(p[j][i] for j in range(K))+q)
    return max(Lpath,Lcut), Lpath, Lcut

def test_class(name, gen, trials=400, K=4, m=3):
    random.seed(0); fails=0; ex=None
    for _ in range(trials):
        p,rel=gen(K,m)
        c=cmax_opt(p,rel,m); b,lp,lc=bound(p,rel,m)
        if c!=b:
            fails+=1
            if ex is None: ex=(p,rel,c,b,lp,lc)
    print(f"{name:<46} fails {fails}/{trials}")
    if ex: 
        p,rel,c,b,lp,lc=ex
        print(f"    e.g. Cmax={c} > bound={b} (Lpath={lp},Lcut={lc})  p={p} rel={rel}")
    return fails

# ---- candidate classes ----
def gen_hetero(K,m):
    return [[random.randint(1,9) for _ in range(m)] for _ in range(K)], [random.randint(0,15) for _ in range(K)]
def gen_homog(K,m):                      # proportionate: p depends on machine only
    pr=[random.randint(1,9) for _ in range(m)]
    return [pr[:] for _ in range(K)], [random.randint(0,15) for _ in range(K)]
def gen_homog_domB(K,m):                 # homogeneous + one bottleneck >= sum of others
    pr=[random.randint(1,5) for _ in range(m)]; b=random.randrange(m)
    pr[b]=sum(pr)-pr[b]+random.randint(1,5)
    return [pr[:] for _ in range(K)], [random.randint(0,20) for _ in range(K)]
def gen_homog_superB(K,m):               # homogeneous + bottleneck >= sum others, others equal small
    b=random.randrange(m); pr=[1]*m; pr[b]=random.randint(m,m+8)
    return [pr[:] for _ in range(K)], [random.randint(0,20) for _ in range(K)]







pass
def gen_homog_rel0(K,m):
    pr=[random.randint(1,9) for _ in range(m)]; return [pr[:] for _ in range(K)], [0]*K
def gen_homog_rel0_lastB(K,m):
    pr=[random.randint(1,3) for _ in range(m)]; pr[m-1]=random.randint(m,m+8); return [pr[:] for _ in range(K)],[0]*K
def gen_homog_rel0_lastB_dom(K,m):  # bottleneck last AND >= sum of all upstream
    up=[random.randint(1,3) for _ in range(m-1)]; b=sum(up)+random.randint(0,5)
    pr=up+[b]; return [pr[:] for _ in range(K)],[0]*K
def gen_homog_nondec_rel(K,m):      # homogeneous, releases sorted (no overtaking-friendly), small spread
    pr=[random.randint(1,9) for _ in range(m)]; r=sorted(random.randint(0,5) for _ in range(K))
    return [pr[:] for _ in range(K)], r





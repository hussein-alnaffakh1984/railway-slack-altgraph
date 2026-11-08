import random
from equiv import cmax_opt, cmax_perm
# Clean closed form derived from the lattice longest-path proof:
#   C_max = P + max_{a=1..K} [ rho_(a) + (K-a) * p_b ],   P=sum p_i, p_b=max p_i,
#   rho_(1)<=...<=rho_(K).  (Each monotone lattice step has weight p of its resource;
#   up-steps+finish contribute P; the K-a right-steps are best placed on the bottleneck.)
def closed_form(pr, rel):
    P=sum(pr); pb=max(pr); r=sorted(rel); K=len(r)
    return P + max(r[a] + (K-1-a)*pb for a in range(K))   # a is 0-indexed: (K-a) -> (K-1-a)
def cmax_prop(pr, rel, m):
    order=sorted(range(len(rel)), key=lambda j: rel[j])
    return cmax_perm(order,[pr[:] for _ in range(len(rel))],rel,m)
random.seed(11)
f=0
for _ in range(5000):
    m=random.randint(2,6); K=random.randint(1,6)
    pr=[random.randint(1,9) for _ in range(m)]; rel=[random.randint(0,40) for _ in range(K)]
    if cmax_prop(pr,rel,m)!=closed_form(pr,rel): f+=1
print(f"closed form  C_max = P + max_a[rho_(a)+(K-a)p_b]  matches: {5000-f}/5000")

# Boundary probe: does the subset(Carlier) bound stay tight for HETEROGENEOUS trains?
import itertools
def cmax_opt_gen(p,rel,m): return min(cmax_perm(o,p,rel,m) for o in itertools.permutations(range(len(p))))
def carlier(p,rel,m):
    K=len(p); h=lambda j,i: rel[j]+sum(p[j][:i]); q=lambda j,i: sum(p[j][i+1:])
    best=0
    for i in range(m):
        for S in range(1,K+1):
            for sub in itertools.combinations(range(K),S):
                best=max(best, min(h(j,i) for j in sub)+sum(p[j][i] for j in sub)+min(q(j,i) for j in sub))
    return best
random.seed(5); fh=0; exh=None
for _ in range(800):
    m=random.randint(2,3); K=random.randint(2,4)
    p=[[random.randint(1,9) for _ in range(m)] for _ in range(K)]; rel=[random.randint(0,10) for _ in range(K)]
    c=cmax_opt_gen(p,rel,m); b=carlier(p,rel,m)
    if c!=b: fh+=1; exh=exh or (p,rel,c,b)
print(f"Carlier subset bound tight for HETEROGENEOUS trains: fails {fh}/800")
if exh: print("   e.g.",exh)

import sys; sys.path.insert(0,'..')
from fractions import Fraction as Fr
from ag import *
from families import *
ag=dariano()
print("pairs",len(ag.pairs),"flex",ag.flex,"M",ag.bigM(25))
for d in (0,10,25):
    en=ag.enumerate([d,d]); L=min(v for v,s in en); Lm,sel=ag.solve([d,d])
    print(d,"enum",L,"feasible",len(en),"milp",Lm)
for Phi in (10,20,25):
    print(Phi,"uniform",min(v for v,s in ag.enumerate([Fr(Phi,2)]*2)),ag.solve([Fr(Phi,2)]*2,scale=2)[0],"targeted",ag.solve([0,Phi])[0], "opt alloc",ag.optimal_allocation(Phi))
# binding tests vs enumeration
def bind_enum(phi,L,ks):
    for v,s in ag.enumerate(phi):
        if v==L:
            LL,be=ag.beta(phi,s)
            if any(be[k]==LL for k in ks): return True
    return False
for Phi in (10,20,25):
    for j in range(2*Phi+1):
        th=Fr(j,2*Phi); phi=segment(2,Phi,1,th)
        L=min(v for v,s in ag.enumerate(phi)); Lm,_=ag.solve(phi,scale=4)
        assert L==Lm,(L,Lm)
        for ks in ([0],[1]):
            a=bind_enum(phi,L,ks); b=ag.binding_in_some_optimum(phi,L,ks,scale=4)
            assert a==b,(Phi,th,ks,a,b)
print("MILP == enumeration (values and binding tests) on all grid points of the published instance")

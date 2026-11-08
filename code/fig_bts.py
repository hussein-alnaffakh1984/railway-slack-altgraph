import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
src=open("btf_on_dariano.py").read().split('print("BTF on')[0]; ns={}; exec(src,ns); maxsec=ns['maxsec']
ds=list(range(0,26))
uni=[maxsec(d,d) for d in ds]; bonly=[maxsec(0,d) for d in ds]; aonly=[maxsec(d,0) for d in ds]
plt.figure(figsize=(7,4))
plt.plot([2*d for d in ds],uni,'s--',color='#1E4682',lw=1.8,ms=4,label=r'uniform: $\varphi_A=\varphi_B=\delta$ (budget $2\delta$)')
plt.plot(ds,bonly,'o-',color='#C44E52',lw=2.2,ms=4,label=r'targeted: $\varphi_B=\delta$, $\varphi_A=0$ (budget $\delta$)',zorder=5)
plt.plot(ds,aonly,'^:',color='#55A868',lw=1.8,ms=4,label=r'$\varphi_A=\delta$, $\varphi_B=0$ (budget $\delta$)')
plt.xlabel('total slack budget $\\Phi$ (s)'); plt.ylabel('maximum secondary delay (s)')
plt.legend(fontsize=8); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig('fig_bts.png',dpi=300,bbox_inches='tight'); print('ok')

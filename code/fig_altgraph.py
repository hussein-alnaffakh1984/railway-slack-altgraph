import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch
fig,ax=plt.subplots(figsize=(10,4.2)); ax.axis('off')
# node positions: rows A (top), C (mid), B (bottom) as in D'Ariano Fig.3
rowA,rowC,rowB=2.0,1.0,0.0
nodes={'0':(0,1.0),'n':(9.6,1.0),
 'A3':(1.6,rowA),'A4':(3.0,rowA),'ASt':(4.4,rowA),'A8':(6.2,rowA),'A*':(7.8,rowA),
 'C6':(1.6,rowC),'C7':(3.0,rowC),'C8':(6.2,rowC),'C*':(7.8,rowC),
 'B3':(1.6,rowB),'B4':(3.0,rowB),'BSt':(4.4,rowB),'B8':(6.2,rowB),'B*':(7.8,rowB)}
def arrow(u,v,w,color='#444',ls='-',rad=0.0,lw=1.2,lab=True,fs=7):
    x0,y0=nodes[u]; x1,y1=nodes[v]
    a=FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=10,color=color,lw=lw,ls=ls,connectionstyle=f"arc3,rad={rad}",shrinkA=9,shrinkB=9); ax.add_patch(a)
    if lab:
        mx,my=(x0+x1)/2,(y0+y1)/2; ax.text(mx+0.0,my+0.09+rad*0.6,str(w),fontsize=fs,color=color,ha='center')
# fixed routing arcs (weights = occupation times from D'Ariano 2005)
for u,v,w in [('A3','A4',12),('A4','ASt',10),('ASt','A8',20),('A8','A*',15),('C6','C7',25),('C7','C8',25),('C8','C*',15),('B3','B4',10),('B4','BSt',10),('BSt','B8',20),('B8','B*',15)]: arrow(u,v,w)
# release arcs
arrow('0','A3','107',rad=-0.15); arrow('0','C6','112'); arrow('0','B3','95',rad=0.15)
# min-departure arcs
arrow('0','A8','',color='#8a2be2',ls='--',rad=-0.42,lab=False); arrow('0','B8','',color='#8a2be2',ls='--',rad=0.42,lab=False)
ax.text(3.1,2.62,r'$115-\delta_A$',fontsize=8,color='#8a2be2',ha='center'); ax.text(3.1,-0.62,r'$160-\delta_B$',fontsize=8,color='#8a2be2',ha='center')
# due-date arcs to n
for u,w,r in [('ASt','',-0.35),('A*','',-0.1),('C*','',0.0),('BSt','',0.35),('B*','',0.1)]: arrow(u,'n',w,color='#2a7',ls=':',rad=r,lab=False)
for x,y,t in [(8.9,2.35,'-164'),(6.3,2.75,'-129 (ASt)'),(8.9,1.12,'-177'),(8.9,-0.35,'-175'),(6.3,-0.75,'-115 (BSt)')]: ax.text(x,y,t,fontsize=7.5,color='#2a7',ha='center')
# alternative pairs (blocking): A/B on 3,4,Stop,8 ; A/C and B/C on 8
pairs=[('B4','A3','A4','B3'),('B8','A4','A8','B4'),('B*','A8','A*','B8')]   # A/B on sections 3, 4 (incl. stop), 8 -- as in D'Ariano Fig. 3
for (u1,v1,u2,v2) in pairs:
    arrow(u1,v1,'',color='#C44E52',ls='-',rad=0.0,lab=False,lw=1.0); arrow(u2,v2,'',color='#C44E52',ls='-',rad=0.0,lab=False,lw=1.0)
arrow('C*','A8','',color='#e69500',lab=False,lw=1.0); arrow('A*','C8','',color='#e69500',lab=False,lw=1.0)
arrow('C*','B8','',color='#e69500',lab=False,lw=1.0); arrow('B*','C8','',color='#e69500',lab=False,lw=1.0)
for k,(x,y) in nodes.items():
    ax.add_patch(mp.Circle((x,y),0.17,fc='white',ec='#333',zorder=5)); ax.text(x,y,k,fontsize=7,ha='center',va='center',zorder=6)
ax.set_xlim(-0.4,10.1); ax.set_ylim(-0.95,2.95); plt.tight_layout(); plt.savefig('fig_altgraph.png',dpi=300,bbox_inches='tight'); print('ok')

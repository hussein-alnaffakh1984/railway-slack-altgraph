import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patches as mp, csv
ACC='#1E4682'; RED='#C44E52'; GRN='#55A868'
# ---- Fig 1: station layout (after D'Ariano et al. 2005, Fig.3 top) ----
fig,ax=plt.subplots(figsize=(8,2.6)); ax.axis('off')
def seg(x0,x1,y,lab,c='#444'):
    ax.plot([x0,x1],[y,y],color=c,lw=3); ax.text((x0+x1)/2,y+0.13,lab,ha='center',fontsize=9)
seg(0,1,1.0,'1 (B)'); seg(0,1,0.5,'2 (A)'); ax.plot([1,1.5],[1.0,0.75],color='#444',lw=3); ax.plot([1,1.5],[0.5,0.75],color='#444',lw=3)
seg(1.5,2.5,0.75,'3'); ax.plot([2.5,4.5],[0.75,0.75],color='#444',lw=3); ax.text(3.0,0.88,'4',ha='center',fontsize=9); ax.add_patch(mp.Rectangle((3.6,0.62),0.8,0.26,fc='#f5d6d6',ec=RED)); ax.text(4.0,0.95,'Stop (within section 4)',ha='center',fontsize=9,color=RED)
seg(0,1.5,0.0,'5 (C)'); seg(1.5,2.5,0.0,'6'); seg(2.5,4.5,0.0,'7')
ax.plot([4.5,5.2],[0.75,0.4],color='#444',lw=3); ax.plot([4.5,5.2],[0.0,0.4],color='#444',lw=3)
ax.add_patch(mp.Rectangle((5.2,0.27),1.2,0.26,fc='#fde9c9',ec='#c80')); ax.text(5.8,0.6,'8 (merge)',ha='center',fontsize=9,color='#a60')
ax.annotate('',xy=(6.95,0.4),xytext=(6.4,0.4),arrowprops=dict(arrowstyle='->',lw=1.5)); ax.text(7.0,0.4,'exit',va='center',fontsize=9)
for x,y,t in [(-0.15,1.0,'B'),(-0.15,0.5,'A'),(-0.15,0.0,'C')]: ax.text(x,y,t,ha='right',va='center',fontsize=11,fontweight='bold',color=ACC)
ax.set_xlim(-0.4,7.3); ax.set_ylim(-0.3,1.4); plt.tight_layout(); plt.savefig('fig_station.png',dpi=300,bbox_inches='tight')

# ---- Fig 2: benchmark gaps (20 instances) ----
rows=list(csv.DictReader(open('benchmark_20_instances.csv')))
rows.sort(key=lambda r:(int(r['nA']),r['inst']))
x=range(len(rows)); am=[float(r['amcc_gap']) for r in rows]; fc=[float(r['fcfs_gap']) for r in rows]
fig,ax=plt.subplots(figsize=(8,3.4))
ax.bar([i-0.2 for i in x],fc,0.4,color=RED,label='FCFS gap (%)'); ax.bar([i+0.2 for i in x],am,0.4,color=ACC,label='AMCC gap (%)')
ax.set_xticks(list(x)); ax.set_xticklabels([r['inst'] for r in rows],rotation=70,fontsize=7); ax.set_ylabel('optimality gap (%)')
ax.set_title('Heuristic optimality gaps vs. proven optimum (20 instances, sorted by |A|)',fontsize=10); ax.legend(fontsize=8); ax.grid(axis='y',alpha=.3)
plt.tight_layout(); plt.savefig('fig_gaps.png',dpi=300,bbox_inches='tight')

# ---- Fig 3: node reduction with runtimes ----
rows=list(csv.DictReader(open('propagation_bnb_node_reduction.csv')))
fig,ax=plt.subplots(figsize=(7,3.3)); x=range(len(rows))
b=[int(r['base_nodes']) for r in rows]; p=[int(r['pbnb_nodes']) for r in rows]
ax.bar([i-0.2 for i in x],b,0.4,color='#999',label='baseline B&B nodes'); ax.bar([i+0.2 for i in x],p,0.4,color=ACC,label='P-B&B nodes')
ax.set_yscale('log'); ax.set_xticks(list(x)); ax.set_xticklabels([r['inst'] for r in rows],rotation=45,fontsize=8); ax.set_ylabel('nodes (log)')
ax.set_title('Search-tree nodes: baseline vs. propagation B&B (K7s2#7 baseline hit the 400,000-node cap)',fontsize=9); ax.legend(fontsize=8); ax.grid(axis='y',alpha=.3)
plt.tight_layout(); plt.savefig('fig_nodes.png',dpi=300,bbox_inches='tight')
print("figs ok")

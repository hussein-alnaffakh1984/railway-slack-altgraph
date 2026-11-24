"""Figures 1-3 of the revised paper (colour-blind-safe Okabe-Ito palette; every series also has its own
line style / marker so that the figures read in black and white)."""
import sys; sys.path.insert(0, '..')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
from fractions import Fraction as Fr
import families as fam
BLUE, ORANGE, VERM, GREEN, PURPLE, SKY, BLACK = '#0072B2', '#E69F00', '#D55E00', '#009E73', '#CC79A7', '#56B4E9', '#222222'
plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 11})

# ---------------- Figure 1: station layout ----------------
fig, ax = plt.subplots(figsize=(9, 3.1)); ax.axis('off')
def seg(x0, x1, y, lab, dy=0.12):
    ax.plot([x0, x1], [y, y], color='#555', lw=3.2, solid_capstyle='butt'); ax.text((x0 + x1) / 2, y + dy, lab, ha='center', fontsize=12)
    for x in (x0, x1): ax.plot([x, x], [y - 0.05, y + 0.05], color='#555', lw=1.2)
seg(0, 1, 1.0, '1'); seg(0, 1, 0.5, '2'); ax.plot([1, 1.5], [1.0, 0.75], color='#555', lw=3.2); ax.plot([1, 1.5], [0.5, 0.75], color='#555', lw=3.2)
seg(1.5, 2.5, 0.75, '3'); seg(2.5, 4.5, 0.75, ''); ax.text(2.95, 0.87, '4', ha='center', fontsize=12)
ax.add_patch(mp.Rectangle((3.45, 0.80), 0.95, 0.20, fc='white', ec=BLACK, hatch='///', lw=1.2)); ax.text(3.92, 1.06, 'platform stop (inside section 4)', ha='center', fontsize=10.5)
seg(0, 1.5, 0.0, '5'); seg(1.5, 2.5, 0.0, '6'); seg(2.5, 4.5, 0.0, '7')
ax.plot([4.5, 5.2], [0.75, 0.4], color='#555', lw=3.2); ax.plot([4.5, 5.2], [0.0, 0.4], color='#555', lw=3.2)
seg(5.2, 6.4, 0.4, '8 (merge)')
ax.annotate('', xy=(7.0, 0.4), xytext=(6.45, 0.4), arrowprops=dict(arrowstyle='-|>', lw=1.6, color=BLACK)); ax.text(7.05, 0.4, 'exit', va='center', fontsize=11)
# routes, offset from the track, one style per train
def route(pts, color, ls, lw=2.0):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, ls=ls, lw=lw)
    ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='-|>', lw=lw, color=color, ls='-'))
route([(0.1, 0.42), (1.0, 0.42), (1.5, 0.67), (4.5, 0.67), (5.2, 0.34), (6.3, 0.34)], VERM, '-')
route([(0.1, 0.92), (1.0, 0.92), (1.45, 0.705), (4.48, 0.705), (5.18, 0.30), (6.3, 0.30)], BLUE, '--')
route([(0.1, -0.08), (4.5, -0.08), (5.2, 0.26), (6.3, 0.26)], GREEN, ':', 2.6)
for y, t, c in ((1.0, 'B', BLUE), (0.5, 'A', VERM), (0.0, 'C', GREEN)): ax.text(-0.12, y, t, ha='right', va='center', fontsize=14, fontweight='bold', color=c)
ax.legend(handles=[Line2D([], [], color=VERM, ls='-', lw=2, label='train A (passenger, stops): 2-3-4-8'),
                   Line2D([], [], color=BLUE, ls='--', lw=2, label='train B (passenger, stops): 1-3-4-8'),
                   Line2D([], [], color=GREEN, ls=':', lw=2.6, label='train C (freight): 5-6-7-8')],
          loc='lower right', bbox_to_anchor=(1.0, 0.62), fontsize=9.5, frameon=False)
ax.set_xlim(-0.35, 7.5); ax.set_ylim(-0.25, 1.45); plt.tight_layout(); plt.savefig('fig/fig1_station.png', dpi=300, bbox_inches='tight'); plt.close()

# ---------------- Figure 2: alternative graph ----------------
fig, ax = plt.subplots(figsize=(11.5, 6.2)); ax.axis('off')
rA, rC, rB = 3.2, 1.6, 0.0
N = {'0': (0, rC), 'n': (11.4, rC),
     'A3': (1.9, rA), 'A4': (3.7, rA), 'ASt': (5.5, rA), 'A8': (7.6, rA), 'A*': (9.5, rA),
     'C6': (1.9, rC), 'C7': (3.7, rC), 'C8': (7.6, rC), 'C*': (9.5, rC),
     'B3': (1.9, rB), 'B4': (3.7, rB), 'BSt': (5.5, rB), 'B8': (7.6, rB), 'B*': (9.5, rB)}
def arrow(u, v, w='', color=BLACK, ls='-', rad=0.0, lw=1.5, fs=11, off=(0, 0.14), pos=0.5):
    (x0, y0), (x1, y1) = N[u], N[v]
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=14, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=13, shrinkB=13, zorder=2))
    if w != '':
        ax.text(x0 + (x1 - x0) * pos + off[0], y0 + (y1 - y0) * pos + off[1], str(w), fontsize=fs, color=color, ha='center', va='center',
                bbox=dict(fc='white', ec='none', pad=0.6), zorder=4)
for u, v, w in [('A3', 'A4', 12), ('A4', 'ASt', 10), ('ASt', 'A8', 20), ('A8', 'A*', 15), ('C6', 'C7', 25), ('C7', 'C8', 25), ('C8', 'C*', 15),
                ('B3', 'B4', 10), ('B4', 'BSt', 10), ('BSt', 'B8', 20), ('B8', 'B*', 15)]:
    arrow(u, v, w, lw=1.8, pos={('C6', 'C7'): 0.36, ('C7', 'C8'): 0.14, ('C8', 'C*'): 0.36}.get((u, v), 0.5))
arrow('0', 'A3', 107, off=(0.28, -0.12)); arrow('0', 'C6', 112); arrow('0', 'B3', 95, off=(0.28, 0.12))
# flexible minimum-departure arcs
arrow('0', 'A8', color=PURPLE, ls=(0, (6, 3)), rad=-0.40, lw=2.2); arrow('0', 'B8', color=PURPLE, ls=(0, (6, 3)), rad=0.40, lw=2.2)
ax.text(3.6, rA + 1.22, r'$115-\varphi_A$', fontsize=12, color=PURPLE, ha='center'); ax.text(3.6, rB - 1.22, r'$160-\varphi_B$', fontsize=12, color=PURPLE, ha='center')
# due-date arcs
for u, r in (('ASt', -0.38), ('A*', -0.12), ('C*', 0.0), ('BSt', 0.38), ('B*', 0.12)):
    arrow(u, 'n', color=GREEN, ls=(0, (1, 2)), rad=r, lw=2.0)
for x, y, t in ((10.75, rA - 0.55, r'$-164$'), (8.6, rA + 0.98, r'$-129$'), (10.45, rC + 0.17, r'$-177$'), (10.75, rB + 0.55, r'$-175$'), (8.6, rB - 0.98, r'$-115$')):
    ax.text(x, y, t, fontsize=11, color=GREEN, ha='center', bbox=dict(fc='white', ec='none', pad=0.5), zorder=4)
# alternative pairs
AB = [('B4', 'A3', 'A4', 'B3', 'p1', (2.8, 2.55)), ('B8', 'A4', 'A8', 'B4', 'p2', (5.65, 2.3)), ('B*', 'A8', 'A*', 'B8', 'p3', (8.55, 2.45))]
for u1, v1, u2, v2, lab, (lx, ly) in AB:
    arrow(u1, v1, color=VERM, lw=1.6); arrow(u2, v2, color=VERM, lw=1.6)
    ax.text(lx, ly, lab, fontsize=11, color=VERM, fontweight='bold', ha='center', bbox=dict(fc='white', ec=VERM, boxstyle='round,pad=0.15', lw=0.8), zorder=5)
for u1, v1, u2, v2, lab, (lx, ly) in [('C*', 'A8', 'A*', 'C8', 'p4', (8.55, 1.98)), ('C*', 'B8', 'B*', 'C8', 'p5', (8.55, 1.22))]:
    arrow(u1, v1, color=BLUE, ls=(0, (5, 2, 1, 2)), lw=1.6); arrow(u2, v2, color=BLUE, ls=(0, (5, 2, 1, 2)), lw=1.6)
    ax.text(lx, ly, lab, fontsize=11, color=BLUE, fontweight='bold', ha='center', bbox=dict(fc='white', ec=BLUE, boxstyle='round,pad=0.15', lw=0.8), zorder=5)
names = {'ASt': 'A,Stop', 'BSt': 'B,Stop'}
for k, (x, y) in N.items():
    ax.add_patch(mp.Circle((x, y), 0.30, fc='white', ec=BLACK, lw=1.3, zorder=6))
    lab = names.get(k, k if k in '0n' else f"{k[0]},{k[1:]}")
    ax.text(x, y, lab, fontsize=9.5 if len(lab) > 3 else 11, ha='center', va='center', zorder=7)
for y, t in ((rA, 'train A'), (rC, 'train C'), (rB, 'train B')): ax.text(-0.55, y + (0.55 if y == rC else 0), t, fontsize=12, fontweight='bold', ha='left', va='center')
ax.legend(handles=[Line2D([], [], color=BLACK, lw=1.8, label='routing / release arc (weight in s)'),
                   Line2D([], [], color=PURPLE, lw=2.2, ls=(0, (6, 3)), label=r'minimum-departure arc $(0,\mathrm{dep}_k)$, weight $d_k-\varphi_k$'),
                   Line2D([], [], color=GREEN, lw=2.0, ls=(0, (1, 2)), label='due-date arc into $n$ (weight = $-$modified due date)'),
                   Line2D([], [], color=VERM, lw=1.6, label='alternative pairs p1-p3: A/B on sections 3, 4, 8'),
                   Line2D([], [], color=BLUE, lw=1.6, ls=(0, (5, 2, 1, 2)), label='alternative pairs p4, p5: A/C and B/C on section 8')],
          loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=10.5, frameon=False)
ax.set_xlim(-0.7, 11.9); ax.set_ylim(-1.55, 4.75); plt.tight_layout(); plt.savefig('fig/fig2_altgraph.png', dpi=300, bbox_inches='tight'); plt.close()

# ---------------- Figure 3: equal-budget comparison on the published instance ----------------
ag = fam.dariano(); val = lambda a, b: float(min(v for v, s in ag.enumerate([Fr(a), Fr(b)])))
xs = [Fr(i, 2) for i in range(0, 101)]
uni = [val(x / 2, x / 2) for x in xs]; tgt = [val(0, x) for x in xs]; opp = [val(x, 0) for x in xs]
fig, ax = plt.subplots(figsize=(7.6, 4.3))
ax.plot(xs, uni, color=BLUE, ls='--', lw=2.2, label=r'uniform: $(\varphi_A,\varphi_B)=(\Phi/2,\Phi/2)$')
ax.plot(xs, tgt, color=VERM, ls='-', lw=2.6, label=r'targeted: $(0,\Phi)$ (equals the optimal allocation)')
ax.plot(xs, opp, color=GREEN, ls=':', lw=2.6, label=r'opposite: $(\Phi,0)$')
ax.plot([0, 20, 50], [41, 31, 18], ls='none', marker='s', ms=11, mfc='none', mec=BLACK, mew=1.8, label=r'values published in [2] (uniform, $\delta=0,10,25$)')
ax.plot([10, 20, 25], [val(0, 10), val(0, 20), val(0, 25)], ls='none', marker='o', ms=7, color=VERM)
ax.plot([10, 20, 25], [val(5, 5), val(10, 10), val(12.5, 12.5)], ls='none', marker='D', ms=6, color=BLUE)
ax.set_xlabel(r'total flexibility budget $\Phi=\varphi_A+\varphi_B$ (s)', fontsize=12); ax.set_ylabel('maximum secondary delay (s)', fontsize=12)
ax.set_xlim(-1, 51); ax.set_ylim(14, 44); ax.grid(alpha=.35); ax.legend(fontsize=9.5, loc='upper right', bbox_to_anchor=(1.0, 0.90)); ax.tick_params(labelsize=11)
plt.tight_layout(); plt.savefig('fig/fig3_equal_budget.png', dpi=300, bbox_inches='tight'); plt.close()
print('uniform at 50:', uni[-1], 'targeted at 25, 50:', tgt[50], tgt[-1], 'opposite:', set(opp))

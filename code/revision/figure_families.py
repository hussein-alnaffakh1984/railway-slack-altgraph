"""Figure 4: share of the achievable delay reduction captured by each policy, by family, split by certificate."""
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S = json.load(open('summary.json'))
BLUE, VERM, GREEN = '#0072B2', '#D55E00', '#009E73'
plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 11})
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
fams = [('station', 'perturbed\nstation'), ('junction', 'junction'), ('corridor', 'corridor')]
for ax, key, nkey, title in ((axs[0], 'sharecert', 'helped_cert', 'condition (H) certified'), (axs[1], 'sharenc', 'helped_nc', 'condition (H) fails')):
    for j, (pol, col, hat, lab) in enumerate((('uniform', BLUE, '///', 'uniform'), ('targeted', VERM, '', 'targeted'), ('sequential', GREEN, '...', 'sequential'))):
        vals = [S[f][key][pol] for f, _ in fams]
        bars = ax.bar([i + (j - 1) * 0.27 for i in range(3)], vals, 0.25, color=col, hatch=hat, edgecolor='black', lw=0.8, label=lab)
        for b, v in zip(bars, vals): ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}", ha='center', fontsize=9.5)
    ax.set_xticks(range(3)); ax.set_xticklabels([f"{lab}\n(n = {S[f][nkey]})" for f, lab in fams], fontsize=10.5)
    ax.set_title(title, fontsize=11.5); ax.set_ylim(0, 128); ax.set_yticks(range(0, 101, 20)); ax.grid(axis='y', alpha=.35); ax.set_axisbelow(True)
axs[0].set_ylabel('share of achievable reduction (%)', fontsize=11); axs[1].legend(fontsize=10, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
plt.tight_layout(); plt.savefig('fig/fig4_families.png', dpi=300, bbox_inches='tight')

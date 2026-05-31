"""
Hallmark perturbation bar chart (8x6 in, 12pt+ text).

Horizontal bar chart showing aging hallmark perturbation magnitude,
colored by HALLMARK_COLORS with short name labels.  Handles both
aging (hub_gene = hallmark name) and disease-specific data
(aggregated by hallmark field).
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from steeramed_core.viz.theme import (
    PALETTE, HALLMARK_COLORS, HALLMARK_SHORT_NAMES, setup,
)


def _aggregate_hallmarks(data):
    modules = data.get('perturbed_modules', [])
    disease = data.get('disease', 'unknown')
    is_aging = disease == 'aging'

    bucket = {}
    for mod in modules:
        if is_aging:
            hm = mod.get('hub_gene', '')
        else:
            hm = mod.get('hallmark', '')
        if not hm:
            continue
        if hm not in bucket:
            bucket[hm] = {'deltas': [], 'p_values': [], 'n_genes': []}
        bucket[hm]['deltas'].append(mod.get('delta', 0))
        bucket[hm]['p_values'].append(mod.get('p_value', 1))
        bucket[hm]['n_genes'].append(mod.get('n_genes', 0))

    rows = []
    for hm, d in bucket.items():
        rows.append({
            'hallmark': hm,
            'short': HALLMARK_SHORT_NAMES.get(hm, hm),
            'delta': float(np.mean(d['deltas'])),
            'p_value': min(d['p_values']),
            'n_genes': sum(d['n_genes']),
            'n_modules': len(d['deltas']),
        })
    rows.sort(key=lambda r: abs(r['delta']), reverse=True)
    return rows


def plot_hallmark_bar(data: dict, output_path: str = None) -> plt.Figure:
    """Generate hallmark perturbation bar chart (8x6 in, 12pt+ text)."""
    setup()
    C = PALETTE
    plt.rcParams.update({
        'font.size': 13,
        'axes.labelsize': 13,
        'xtick.labelsize': 12,
        'ytick.labelsize': 14,
    })

    rows = _aggregate_hallmarks(data)
    if not rows:
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
        ax.text(0.5, 0.5, 'No perturbed modules data',
                fontsize=16, ha='center', va='center',
                transform=ax.transAxes, color=C['grey'])
        ax.axis('off')
        if output_path is not None:
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
        return fig

    n = len(rows)
    fig_h = max(6.0, 2.5 + n * 0.4)
    fig, ax = plt.subplots(figsize=(8, fig_h), facecolor='white')

    labels = [r['short'] for r in rows]
    deltas = [r['delta'] for r in rows]
    p_values = [r['p_value'] for r in rows]
    n_genes = [r['n_genes'] for r in rows]
    n_modules = [r['n_modules'] for r in rows]
    colors = [HALLMARK_COLORS.get(r['hallmark'], C['blue']) for r in rows]

    y_pos = np.arange(n)
    ax.barh(y_pos, [abs(d) for d in deltas], color=colors,
            edgecolor='white', linewidth=0.5, height=0.6,
            alpha=0.8, zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=14, fontweight='bold')
    for i, lbl in enumerate(ax.get_yticklabels()):
        lbl.set_color(colors[i])

    ax.invert_yaxis()
    ax.set_xlabel('Perturbation magnitude (|\u0394|)', fontsize=13, labelpad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.grid(True, linewidth=0.3, color='#DDDDDD', zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', length=0)

    max_delta = max(abs(d) for d in deltas) if deltas else 1
    for i in range(n):
        p_s = (f'p={p_values[i]:.1e}' if p_values[i] < 0.001
               else f'p={p_values[i]:.3f}')
        mod_info = f'{n_genes[i]} genes'
        if n_modules[i] > 1:
            mod_info += f' ({n_modules[i]} modules)'
        sign = '+' if deltas[i] >= 0 else '-'
        txt = f'\u0394={sign}{abs(deltas[i]):.4f}  {p_s}  {mod_info}'
        ax.text(max_delta * 1.02, y_pos[i], txt,
                fontsize=12, va='center', color='#555555')

    ax.set_xlim(right=max_delta * 2.0)

    disease = data.get('disease', '').upper()
    ax.set_title(f'Hallmark Perturbation \u2014 {disease}',
                 fontsize=20, fontweight='bold', color=C['navy'],
                 pad=15, loc='left')

    plt.subplots_adjust(left=0.22, right=0.95, top=0.88, bottom=0.08)

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    return fig

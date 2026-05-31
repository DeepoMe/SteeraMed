"""
Top-10 compound ranking bar chart (8x6 in, 12pt+ text).

Horizontal bar chart showing compound importance scores with
rank indicators, known/candidate coloring, and target annotations.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from steeramed_core.viz.theme import PALETTE, setup


def plot_drug_ranking(data: dict, output_path: str = None) -> plt.Figure:
    """Generate Top-10 compound ranking bar chart (8x6 in, 12pt+ text)."""
    setup()
    C = PALETTE
    plt.rcParams.update({
        'font.size': 13,
        'axes.labelsize': 13,
        'xtick.labelsize': 12,
        'ytick.labelsize': 14,
    })

    compounds = data.get('top_compounds', [])[:10]
    if not compounds:
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
        ax.text(0.5, 0.5, 'No compound data available',
                fontsize=16, ha='center', va='center',
                transform=ax.transAxes, color=C['grey'])
        ax.axis('off')
        if output_path is not None:
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
        return fig

    n = len(compounds)
    fig_h = max(6.0, 2.5 + n * 0.4)
    fig, ax = plt.subplots(figsize=(8, fig_h), facecolor='white')

    names = [c.get('compound_name', '?') for c in compounds]
    importances = [c.get('importance', 0) for c in compounds]
    is_known = [c.get('is_known_drug', False) for c in compounds]
    n_targets = [c.get('n_targets', 0) for c in compounds]
    sa_scores = [c.get('mean_abs_sa', 0.0) for c in compounds]
    ranks = [c.get('rank', i + 1) for i, c in enumerate(compounds)]

    y_pos = np.arange(n)
    bar_colors = [C['green'] if k else C['purple'] for k in is_known]

    ax.barh(y_pos, importances, color=bar_colors, edgecolor='white',
            linewidth=0.5, height=0.6, alpha=0.8, zorder=3)

    ytick_labels = []
    for i in range(n):
        star = ' *' if is_known[i] else ''
        ytick_labels.append(f'#{ranks[i]}  {names[i]}{star}')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ytick_labels, fontsize=14, fontweight='bold')
    for i, lbl in enumerate(ax.get_yticklabels()):
        lbl.set_color(C['green'] if is_known[i] else C['purple'])

    ax.invert_yaxis()
    ax.set_xlabel('Importance score', fontsize=13, labelpad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.grid(True, linewidth=0.3, color='#DDDDDD', zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', length=0)

    max_imp = max(importances) if importances else 1
    for i in range(n):
        ax.text(max_imp * 1.02, y_pos[i],
                f'{n_targets[i]} targets | SA {sa_scores[i]:.3f}',
                fontsize=12, va='center', color='#555555')

    ax.set_xlim(right=max_imp * 1.65)

    disease = data.get('disease', '').upper()
    ax.set_title(f'Top-{n} Compound Ranking \u2014 {disease}',
                 fontsize=20, fontweight='bold', color=C['navy'],
                 pad=15, loc='left')

    legend_handles = [
        Patch(facecolor=C['green'], edgecolor='none',
              label='Known drug *'),
        Patch(facecolor=C['purple'], edgecolor='none',
              label='Novel candidate'),
    ]
    ax.legend(handles=legend_handles, loc='lower right', fontsize=12,
              frameon=True, edgecolor='#CCCCCC')

    plt.subplots_adjust(left=0.28, right=0.95, top=0.88, bottom=0.08)

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    return fig

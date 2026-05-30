"""
Scientist-facing four-panel evidence chain visualization.

Panel A: PPI module perturbation (bar chart)
Panel B: Compound SA ranking
Panel C: Mechanism network (compound → PPI hub → hallmark alignment)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.lines import Line2D
from steeramed_core.viz.theme import PALETTE, HALLMARK_COLORS, HALLMARK_SHORT_NAMES, setup, panel_label
from steeramed_core.core.evidence_chain import EvidenceChain


def plot_evidence_chain(chain: EvidenceChain, output_path: str = None, dpi: int = 300) -> plt.Figure:
    """Generate a scientist-facing evidence chain figure.

    Panel A shows top perturbed PPI modules as a horizontal bar chart.
    Panel B ranks the top-10 compounds by importance score.
    Panel C maps the top-5 compounds to their targeted aging hallmarks.

    Args:
        chain: Populated ``EvidenceChain`` object.
        output_path: If provided, save the figure to this path.
        dpi: Resolution for the saved figure.

    Returns:
        The matplotlib Figure object.
    """
    setup()

    fig = plt.figure(figsize=(7.2, 9.0), facecolor='white')
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.2, 1.6],
                          hspace=0.30,
                          left=0.14, right=0.96, top=0.95, bottom=0.04)

    ax_a = fig.add_subplot(gs[0])
    modules = chain.perturbed_modules[:10]
    hub_names = [m.hub_gene for m in modules]
    deltas = [m.delta for m in modules]
    n_genes_list = [m.n_genes for m in modules]
    bar_colors_a = [HALLMARK_COLORS.get(m.hallmark, PALETTE['blue']) for m in modules]

    y_pos_a = np.arange(len(modules))
    ax_a.barh(y_pos_a, deltas, color=bar_colors_a, edgecolor='white',
              linewidth=0.3, height=0.65, zorder=3)
    ax_a.set_yticks(y_pos_a)
    ax_a.set_yticklabels(hub_names, fontsize=6.5)
    xlabel_a = 'N modules perturbed' if chain.disease == 'aging' else r'Delta ($\beta$)'
    ax_a.set_xlabel(xlabel_a, fontsize=7)
    ax_a.invert_yaxis()
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)

    max_delta = max(abs(v) for v in deltas) if deltas else 1
    for i, ng in enumerate(n_genes_list):
        ax_a.text(max_delta + max_delta * 0.02, i, f'n={ng}',
                  fontsize=5, va='center', color='#555555')
    ax_a.set_xlim(right=max_delta * 1.55)

    ax_a.set_title(
        f'a  Perturbed PPI modules (N={len(chain.perturbed_modules)})',
        fontsize=7.5, fontweight='bold', pad=4, color=PALETTE['navy'], loc='left')

    ax_b = fig.add_subplot(gs[1])
    top10 = chain.top_compounds[:10]

    names_b = [c.compound_name for c in top10]
    importances = [c.importance for c in top10]
    mean_abs_sas = [c.mean_abs_sa for c in top10]
    is_known = [c.is_known_drug for c in top10]
    bar_colors_b = [PALETTE['green'] if k else '#CFD8DC' for k in is_known]

    y_pos_b = np.arange(len(names_b))
    ax_b.barh(y_pos_b, importances, color=bar_colors_b, edgecolor='white',
              linewidth=0.3, height=0.65, zorder=3)
    ax_b.set_yticks(y_pos_b)
    ax_b.set_yticklabels(names_b, fontsize=6)
    ax_b.invert_yaxis()
    xlabel_b = '% of patients' if chain.disease == 'aging' else 'Importance score'
    ax_b.set_xlabel(xlabel_b, fontsize=7)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.xaxis.grid(True, linewidth=0.3, color='#DDDDDD', zorder=0)
    ax_b.set_axisbelow(True)

    max_imp = max(importances) if importances else 1
    for i, sa in enumerate(mean_abs_sas):
        ax_b.text(max_imp + max_imp * 0.02, i, f'{sa:.3f}',
                  fontsize=5, va='center',
                  color=PALETTE['green'] if is_known[i] else '#555555')
    ax_b.set_xlim(right=max_imp * 1.65)

    ax_b.set_title('b  Top-10 compound ranking',
                   fontsize=7.5, fontweight='bold', pad=4,
                   color=PALETTE['navy'], loc='left')

    legend_b = [
        plt.Rectangle((0, 0), 1, 1, facecolor=PALETTE['green'],
                       edgecolor='none', label='Known drug'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#CFD8DC',
                       edgecolor='none', label='Other compound'),
    ]
    ax_b.legend(handles=legend_b, loc='lower right', fontsize=5.5,
                frameon=True, edgecolor='#CCCCCC')

    ax_c = fig.add_subplot(gs[2])
    ax_c.set_xlim(-0.5, 14)
    ax_c.set_ylim(-0.5, 8.5)
    ax_c.set_aspect('equal')
    ax_c.axis('off')
    ax_c.set_title('c  Top-5 compound\u2013hallmark alignment',
                   fontsize=7.5, fontweight='bold', pad=4,
                   color=PALETTE['navy'], loc='left')

    ax_c.text(1.0, 8.1, 'Drug', ha='center', fontsize=5.5,
              fontweight='bold', color=PALETTE['grey'])
    ax_c.text(9.5, 8.1, 'Hallmark', ha='center', fontsize=5.5,
              fontweight='bold', color=PALETTE['grey'])

    top5 = chain.top_compounds[:5]
    drug_y_positions = [7.0, 5.8, 4.6, 3.4, 2.2]

    drug_hallmark_links = []
    for idx, comp in enumerate(top5):
        y = drug_y_positions[idx]

        fc = '#E8F5E9' if comp.is_known_drug else '#F3E5F5'
        ec = PALETTE['green'] if comp.is_known_drug else PALETTE['purple']
        ax_c.add_patch(Circle((1.0, y), 0.38, facecolor=fc, edgecolor=ec,
                               linewidth=1.2, zorder=3))
        ax_c.text(1.0, y, f'#{comp.rank}', ha='center', va='center',
                  fontsize=6, fontweight='bold', color=ec, zorder=4)
        ax_c.text(-0.3, y + 0.08, comp.compound_name, ha='right', va='center',
                  fontsize=5.5, fontweight='bold', color=ec)
        ax_c.text(-0.3, y - 0.18, f'({comp.n_targets}tgt)', ha='right', va='center',
                  fontsize=5, color='#999999', style='italic')

        compound_hallmarks = {}
        if chain.mechanism_map and comp.compound_id in chain.mechanism_map:
            mech = chain.mechanism_map[comp.compound_id]
            for hm_name in mech.get("hallmarks", []):
                compound_hallmarks[hm_name] = compound_hallmarks.get(hm_name, 0) + 1
        else:
            for mm in comp.matched_modules:
                hm_name = mm.get("hallmark")
                if hm_name:
                    compound_hallmarks[hm_name] = compound_hallmarks.get(hm_name, 0) + 1

        for hm_name, nhits in compound_hallmarks.items():
            drug_hallmark_links.append((idx, y, hm_name, nhits))

    hallmark_nodes = {}
    for _, _, hm_name, nhits in drug_hallmark_links:
        if hm_name not in hallmark_nodes:
            hallmark_nodes[hm_name] = {'hits': 0, 'color': HALLMARK_COLORS.get(hm_name, PALETTE['grey'])}
        hallmark_nodes[hm_name]['hits'] += nhits

    sorted_hallmarks = sorted(hallmark_nodes.items(), key=lambda x: -x[1]['hits'])
    hm_y_map = {}
    for i, (hname, hdata) in enumerate(sorted_hallmarks[:5]):
        y = 7.0 - i * 1.2
        hm_y_map[hname] = y
        pc = hdata['color']
        short = HALLMARK_SHORT_NAMES.get(hname, hname[:15])
        rect = FancyBboxPatch((8.2, y - 0.28), 2.6, 0.56,
                              boxstyle="round,pad=0.04",
                              facecolor=pc, alpha=0.08, edgecolor=pc,
                              linewidth=0.8)
        ax_c.add_patch(rect)
        ax_c.text(9.5, y, short, ha='center', va='center',
                  fontsize=5, fontweight='bold', color=pc, linespacing=1.0,
                  zorder=4)

    for _, dy, hm_name, nhits in drug_hallmark_links:
        if hm_name in hm_y_map:
            hy = hm_y_map[hm_name]
            pc = hallmark_nodes[hm_name]['color']
            lw = 0.3 + nhits * 0.008
            alp = 0.15 + min(nhits * 0.005, 0.4)
            ax_c.plot([1.38, 8.2], [dy, hy], color=pc, linewidth=lw, alpha=alp, zorder=1)

    legend_e = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E8F5E9',
               markersize=5, markeredgecolor=PALETTE['green'], markeredgewidth=1,
               label='Known drug'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#F3E5F5',
               markersize=5, markeredgecolor=PALETTE['purple'], markeredgewidth=1,
               label='Novel candidate'),
        Line2D([0], [0], color=PALETTE['red'], linewidth=1, alpha=0.5,
               label='Hallmark targeting link'),
    ]
    ax_c.legend(handles=legend_e, loc='lower left', frameon=True,
                fancybox=False, edgecolor='#CCCCCC', fontsize=5,
                bbox_to_anchor=(0.0, -0.06), ncol=3)

    if output_path is not None:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
    return fig

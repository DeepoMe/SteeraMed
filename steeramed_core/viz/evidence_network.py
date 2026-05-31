"""
Drug-PPI-Hallmark alignment network (10x7 in, 12pt+ text).

Bipartite network showing the top-5 recommended compounds on the left
connected to their targeted aging hallmarks on the right.  Edges
represent mechanistic alignment extracted from mechanism_map or
matched_modules.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.lines import Line2D
from steeramed_core.viz.theme import (
    PALETTE, HALLMARK_COLORS, HALLMARK_SHORT_NAMES, setup,
)


def _extract_connections(data):
    top5 = data.get('top_compounds', [])[:5]
    connections = []
    for comp in top5:
        cid = comp.get('compound_id', '')
        cname = comp.get('compound_name', '')
        is_known = comp.get('is_known_drug', False)
        n_targets = comp.get('n_targets', 0)

        hallmarks = set()
        mm_map = data.get('mechanism_map')
        if mm_map and cid in mm_map:
            hallmarks.update(mm_map[cid].get('hallmarks', []))

        if not hallmarks:
            for mm in comp.get('matched_modules', []):
                hm = mm.get('hallmark', '')
                if hm:
                    hallmarks.add(hm)

        connections.append({
            'name': cname,
            'is_known': is_known,
            'hallmarks': hallmarks,
            'n_targets': n_targets,
        })
    return connections


def plot_evidence_network(data: dict, output_path: str = None) -> plt.Figure:
    """Generate Drug-PPI-Hallmark alignment network (10x7 in, 12pt+ text)."""
    setup()
    C = PALETTE

    connections = _extract_connections(data)
    if not connections:
        fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')
        ax.text(0.5, 0.5, 'No compound data available',
                fontsize=16, ha='center', va='center',
                transform=ax.transAxes, color=C['grey'])
        ax.axis('off')
        if output_path is not None:
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
        return fig

    fig = plt.figure(figsize=(10, 7), facecolor='white')
    ax = fig.add_axes([0.20, 0.04, 0.78, 0.88])
    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-0.5, 8.5)
    ax.set_aspect('equal')
    ax.axis('off')

    disease = data.get('disease', '').upper()
    ax.set_title(f'Drug \u2192 Hallmark Alignment \u2014 {disease}',
                 fontsize=22, fontweight='bold', color=C['navy'],
                 pad=12, loc='left')

    ax.text(1.5, 8.1, 'Drug', ha='center', fontsize=14,
            fontweight='bold', color=C['grey'])
    ax.text(10.5, 8.1, 'Hallmark', ha='center', fontsize=14,
            fontweight='bold', color=C['grey'])

    n_drugs = len(connections)
    drug_spacing = min(1.4, 7.0 / max(n_drugs - 1, 1))
    drug_ys = [7.0 - i * drug_spacing for i in range(n_drugs)]

    all_hallmarks = {}
    for conn in connections:
        for hm in conn['hallmarks']:
            if hm not in all_hallmarks:
                all_hallmarks[hm] = 0
            all_hallmarks[hm] += 1

    sorted_hms = sorted(all_hallmarks.items(), key=lambda x: -x[1])
    n_hms = min(len(sorted_hms), 7)
    hm_spacing = min(1.2, 7.0 / max(n_hms - 1, 1))
    hm_ys = [7.0 - i * hm_spacing for i in range(n_hms)]
    hm_y_map = {sorted_hms[i][0]: hm_ys[i] for i in range(n_hms)}

    for idx, conn in enumerate(connections):
        y = drug_ys[idx]
        is_known = conn['is_known']

        if is_known:
            fc, ec = C['light_green'], C['green']
        else:
            fc, ec = C['light_purple'], C['purple']

        circle = Circle((1.5, y), 0.42, facecolor=fc, edgecolor=ec,
                         linewidth=1.8, zorder=3)
        ax.add_patch(circle)
        ax.text(1.5, y, f'#{idx + 1}', ha='center', va='center',
                fontsize=13, fontweight='bold', color=ec, zorder=4)

        ax.text(-0.2, y + 0.1, conn['name'], ha='right', va='center',
                fontsize=14, fontweight='bold', color=ec)
        ax.text(-0.2, y - 0.2,
                f"({conn['n_targets']} targets)",
                ha='right', va='center', fontsize=12,
                color='#999999', style='italic')

        for hm in conn['hallmarks']:
            if hm not in hm_y_map:
                continue
            hy = hm_y_map[hm]
            pc = HALLMARK_COLORS.get(hm, C['grey'])
            lw = 1.0 + all_hallmarks[hm] * 0.3
            alp = 0.2 + min(all_hallmarks[hm] * 0.1, 0.5)
            ax.plot([1.92, 8.8], [y, hy], color=pc,
                    linewidth=lw, alpha=alp, zorder=1)

    for i in range(n_hms):
        hm_name = sorted_hms[i][0]
        y = hm_ys[i]
        pc = HALLMARK_COLORS.get(hm_name, C['grey'])
        short = HALLMARK_SHORT_NAMES.get(hm_name, hm_name[:18])

        rect = FancyBboxPatch(
            (8.8, y - 0.35), 3.4, 0.7,
            boxstyle="round,pad=0.06", facecolor=pc,
            alpha=0.10, edgecolor=pc, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(10.5, y, short, ha='center', va='center',
                fontsize=13, fontweight='bold', color=pc, zorder=4)

        count = sorted_hms[i][1]
        ax.text(10.5, y - 0.22, f'{count} link{"s" if count > 1 else ""}',
                ha='center', va='center', fontsize=12,
                color=pc, alpha=0.7, zorder=4)

    legend_handles = [
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor=C['light_green'], markersize=12,
               markeredgecolor=C['green'], markeredgewidth=1.5,
               label='Known drug'),
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor=C['light_purple'], markersize=12,
               markeredgecolor=C['purple'], markeredgewidth=1.5,
               label='Novel candidate'),
        Line2D([0], [0], color=C['red'], linewidth=2, alpha=0.5,
               label='Hallmark targeting link'),
    ]
    ax.legend(handles=legend_handles, loc='lower left', frameon=True,
              fancybox=False, edgecolor='#CCCCCC', fontsize=12,
              bbox_to_anchor=(0.0, -0.04), ncol=3)

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    return fig

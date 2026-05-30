"""
Patient-friendly three-panel card view visualization.

Generates the Hallmark status card, compound recommendation card,
and disclaimer panel for clinical communication.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from steeramed_core.viz.theme import PALETTE, setup, panel_label
from steeramed_core.core.evidence_chain import EvidenceChain


def plot_patient_view(chain: EvidenceChain, output_path: str = None, dpi: int = 300) -> plt.Figure:
    """Generate a patient-facing three-panel card view.

    Panel A shows the top perturbed PPI modules as horizontal bar cards
    with severity indicators.  Panel B displays the top-ranked compounds
    with known/novel badges.  Panel C presents confidence metrics and
    a hypothesis-generating disclaimer.

    Args:
        chain: Populated ``EvidenceChain`` object.
        output_path: If provided, save the figure to this path.
        dpi: Resolution for the saved figure.

    Returns:
        The matplotlib Figure object.
    """
    setup()
    C = PALETTE

    fig = plt.figure(figsize=(7.5, 10.5), facecolor='white')
    gs = fig.add_gridspec(3, 1, height_ratios=[1.2, 1.4, 0.7],
                          hspace=0.25, left=0.06, right=0.94, top=0.93, bottom=0.04)

    title_parts = [f"Patient {chain.patient_id}"]
    if chain.age is not None:
        sex_str = f" {chain.sex}" if chain.sex else ""
        title_parts.append(f"{chain.age}y{sex_str}")
    title_parts.append(chain.disease.upper())
    fig.text(0.5, 0.97, " · ".join(title_parts), fontsize=14,
             fontweight='bold', ha='center', va='top', color=C['navy'])

    ax_a = fig.add_subplot(gs[0])
    ax_a.set_xlim(0, 10)
    ax_a.set_ylim(0, 8.0)
    ax_a.axis('off')

    ax_a.text(5, 7.7, '1. What is happening in your body?',
              fontsize=13, fontweight='bold', ha='center', color=C['navy'])
    ax_a.text(5, 7.35, 'Top perturbed PPI modules from methylation profile',
              fontsize=7.5, ha='center', color=C['grey'])

    top_mods = chain.perturbed_modules[:5]
    max_delta = max((abs(m.delta) for m in top_mods), default=1)

    for i, mod in enumerate(top_mods):
        y = 6.2 - i * 1.15
        pct = abs(mod.delta) / max_delta * 100 if max_delta else 0

        if pct > 80:
            level, color, bg = "HIGH", C['red'], C['light_red']
        elif pct > 50:
            level, color, bg = "MODERATE", C['orange'], C['light_amber']
        else:
            level, color, bg = "MILD", C['amber'], C['light_amber']

        rect = FancyBboxPatch((0.3, y - 0.45), 9.4, 0.9,
                               boxstyle="round,pad=0.06",
                               facecolor=bg, edgecolor=color,
                               linewidth=1.2, alpha=0.7)
        ax_a.add_patch(rect)

        ax_a.text(0.6, y + 0.08, mod.hub_gene, fontsize=9,
                  fontweight='bold', color=color, va='center')
        p_str = f"p={mod.p_value:.2e}" if mod.p_value < 0.001 else f"p={mod.p_value:.3f}"
        ax_a.text(0.6, y - 0.22, f"\u0394={mod.delta:+.4f}  {p_str}  ({mod.n_genes} genes)",
                  fontsize=6.5, color='#666666', va='center')

        bar_x, bar_w, bar_h = 6.0, 2.5, 0.22
        bar_y = y - 0.10
        bg_rect = FancyBboxPatch((bar_x, bar_y), bar_w, bar_h,
                                  boxstyle="round,pad=0.02",
                                  facecolor='#EEEEEE', edgecolor='#DDDDDD', linewidth=0.3)
        ax_a.add_patch(bg_rect)
        fill_w = bar_w * pct / 100
        fill_rect = FancyBboxPatch((bar_x, bar_y), fill_w, bar_h,
                                    boxstyle="round,pad=0.02",
                                    facecolor=color, edgecolor='none', alpha=0.7)
        ax_a.add_patch(fill_rect)
        ax_a.text(bar_x + bar_w + 0.15, y, level, fontsize=6.5,
                  color=color, va='center', fontweight='bold')

    panel_label(ax_a, 'a')

    ax_b = fig.add_subplot(gs[1])
    ax_b.set_xlim(0, 10)
    ax_b.set_ylim(0, 8.5)
    ax_b.axis('off')

    ax_b.text(5, 8.2, '2. Which compounds may help?',
              fontsize=13, fontweight='bold', ha='center', color=C['navy'])
    ax_b.text(5, 7.8, 'Compound screening ranked by module importance',
              fontsize=7.5, ha='center', color=C['grey'])

    top_comps = chain.top_compounds[:5]
    for i, comp in enumerate(top_comps):
        y = 6.8 - i * 1.15
        is_novel = not comp.is_known_drug
        bg_color = C['light_purple'] if is_novel else C['light_green']
        border_color = C['purple'] if is_novel else C['green']
        border_w = 1.5 if comp.rank <= 2 else 0.6

        rect = FancyBboxPatch((0.3, y - 0.45), 9.4, 0.9,
                               boxstyle="round,pad=0.06",
                               facecolor=bg_color, edgecolor=border_color,
                               linewidth=border_w, alpha=0.6)
        ax_b.add_patch(rect)

        rank_bg = C['purple'] if is_novel and comp.rank <= 2 else (
            C['blue'] if comp.rank <= 5 else C['grey'])
        rank_rect = FancyBboxPatch((0.5, y - 0.2), 0.5, 0.4,
                                    boxstyle="round,pad=0.03",
                                    facecolor=rank_bg, edgecolor='none', alpha=0.85)
        ax_b.add_patch(rank_rect)
        ax_b.text(0.75, y, f'#{comp.rank}', fontsize=8, fontweight='bold',
                  color='white', ha='center', va='center')

        ax_b.text(1.3, y + 0.12, comp.compound_name, fontsize=9, fontweight='bold',
                  color=C['navy'] if comp.rank <= 2 else '#333333', va='center')
        ax_b.text(1.3, y - 0.18, f"importance={comp.importance}  targets={comp.n_targets}",
                  fontsize=6.5, color='#888888', va='center')

        hub_names = []
        for mm in comp.matched_modules[:3]:
            hub_names.append(mm.get("hub_gene", mm.get("hub", "?")))
        hub_str = ", ".join(hub_names) if hub_names else "—"
        ax_b.text(4.5, y - 0.18, hub_str, fontsize=5.5, color=C['teal'],
                  va='center', style='italic')

        ev_label = "NOVEL" if is_novel else "KNOWN"
        ev_color = C['purple'] if is_novel else C['green']
        ev_bg = C['light_purple'] if is_novel else C['light_green']
        ev_rect = FancyBboxPatch((8.3, y - 0.2), 1.3, 0.4,
                                  boxstyle="round,pad=0.03",
                                  facecolor=ev_bg, edgecolor=ev_color,
                                  linewidth=0.8, alpha=0.7)
        ax_b.add_patch(ev_rect)
        ax_b.text(8.95, y, ev_label, fontsize=6.5, fontweight='bold',
                  color=ev_color, ha='center', va='center')

    panel_label(ax_b, 'b')

    ax_c = fig.add_subplot(gs[2])
    ax_c.set_xlim(0, 10)
    ax_c.set_ylim(0, 5)
    ax_c.axis('off')

    ax_c.text(5, 4.7, '3. How confident?',
              fontsize=13, fontweight='bold', ha='center', color=C['navy'])

    n_known = chain.meta.get("n_known_drugs_in_top10", "?")
    n_total = chain.meta.get("n_total_compounds", "?")
    n_mods = len(chain.perturbed_modules)

    metrics = [
        {'label': 'Known drugs\nin Top-10', 'value': str(n_known),
         'detail': 'Validated drugs\namong top recommendations',
         'color': C['teal'], 'bg': C['light_blue'], 'x': 1.7},
        {'label': 'Total compounds\nscreened', 'value': str(n_total),
         'detail': 'Compound pool size\nfor this patient',
         'color': C['green'], 'bg': C['light_green'], 'x': 5.0},
        {'label': 'Perturbed\nmodules', 'value': str(n_mods),
         'detail': 'PPI modules with\nsignificant alteration',
         'color': C['purple'], 'bg': C['light_purple'], 'x': 8.3},
    ]

    for m in metrics:
        rect = FancyBboxPatch((m['x'] - 1.4, 0.5), 2.8, 3.5,
                               boxstyle="round,pad=0.1",
                               facecolor=m['bg'], edgecolor=m['color'],
                               linewidth=1.2, alpha=0.6)
        ax_c.add_patch(rect)

        ax_c.text(m['x'], 3.5, m['label'], fontsize=8, fontweight='bold',
                  ha='center', color=m['color'], linespacing=1.2)
        ax_c.text(m['x'], 2.6, m['value'], fontsize=22, fontweight='bold',
                  ha='center', color=m['color'])
        ax_c.text(m['x'], 1.4, m['detail'], fontsize=7, ha='center',
                  color='#666666', linespacing=1.4)

    verdict_rect = FancyBboxPatch((1.5, -0.1), 7.0, 0.55,
                                   boxstyle="round,pad=0.05",
                                   facecolor=C['light_amber'],
                                   edgecolor=C['orange'], linewidth=1.0, alpha=0.5)
    ax_c.add_patch(verdict_rect)
    ax_c.text(5, 0.17, 'Hypothesis-generating only \u2014 not treatment recommendations',
              fontsize=7, ha='center', va='center', fontweight='bold', color=C['orange'])

    panel_label(ax_c, 'c')

    if output_path is not None:
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
    return fig

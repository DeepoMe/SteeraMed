"""
Single-page patient summary card (8x10 in, 12pt+ text).

Generates a card-style summary showing disease context, top perturbed
modules with severity indicators, and recommended compounds with a
confidence assessment bar.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from steeramed_core.viz.theme import PALETTE, HALLMARK_COLORS, HALLMARK_SHORT_NAMES, setup

_DISEASE_LABELS = {
    'aging': 'Aging Case',
    'ra': 'RA',
    'depression': 'MDD',
    'parkinsons': 'PD',
    'alzheimers': 'AD',
    'covid19': 'COVID-19',
}


def _confidence(data):
    top = data.get('top_compounds', [])[:10]
    n_known = sum(1 for c in top if c.get('is_known_drug'))
    if n_known >= 5:
        return 'STRONG', PALETTE['green'], f'{n_known}/10 known drugs recovered'
    if n_known >= 2:
        return 'MODERATE', PALETTE['amber'], f'{n_known}/10 known drugs recovered'
    return 'EXPLORATORY', PALETTE['purple'], 'Hypothesis-generating screening'


def plot_patient_card(data: dict, output_path: str = None) -> plt.Figure:
    """Generate a single-page patient summary card (8x10 in, 12pt+ text)."""
    setup()
    C = PALETTE
    disease = data.get('disease', 'unknown')
    is_aging = disease == 'aging'

    fig = plt.figure(figsize=(8, 10), facecolor='white')
    ax = fig.add_axes([0.04, 0.02, 0.92, 0.96])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    label = _DISEASE_LABELS.get(disease, disease.upper())
    if is_aging:
        line1 = f"{label} \u00b7 Population-level Screening"
        parts = []
        geo = data.get('geo_id', '')
        if geo:
            parts.append(geo)
        n_samples = data.get('n_samples', '')
        if n_samples:
            parts.append(str(n_samples))
        n_mod = len(data.get('perturbed_modules', []))
        if n_mod:
            parts.append(f'{n_mod} perturbed modules')
        line2 = ' \u00b7 '.join(parts)
    else:
        pid = data.get('patient_id', '?')
        suffix = ''
        if data.get('age') is not None:
            suffix = f" \u00b7 {int(data['age'])}{data.get('sex', '')}"
        line1 = f"{label} \u00b7 Patient #{pid}{suffix}"
        _, _, line2 = _confidence(data)

    ax.text(5, 11.5, line1, fontsize=24, fontweight='bold',
            ha='center', va='center', color=C['navy'])
    if line2:
        ax.text(5, 11.0, line2, fontsize=14, ha='center',
                va='center', color=C['grey'])

    ax.plot([0.3, 9.7], [10.55, 10.55], color=C['lgrey'], linewidth=1.5)

    ax.text(0.3, 10.2, "What\u2019s happening?", fontsize=18,
            fontweight='bold', color=C['navy'])

    modules = data.get('perturbed_modules', [])[:5]
    max_delta = max((abs(m.get('delta', 0)) for m in modules), default=1)

    for i, mod in enumerate(modules):
        y = 9.55 - i * 0.85
        delta = mod.get('delta', 0)
        p_val = mod.get('p_value', 1)
        n_genes = mod.get('n_genes', 0)
        hallmark = mod.get('hallmark', '')

        if is_aging:
            name = HALLMARK_SHORT_NAMES.get(
                mod.get('hub_gene', ''), mod.get('hub_gene', ''))
            sev_color = HALLMARK_COLORS.get(
                mod.get('hub_gene', ''), C['blue'])
        else:
            name = mod.get('hub_gene', '')
            sev_color = HALLMARK_COLORS.get(hallmark, C['blue'])

        pct = abs(delta) / max_delta * 100 if max_delta else 0
        if pct > 70:
            sev, bg = 'HIGH', C['light_red']
        elif pct > 40:
            sev, bg = 'MOD', C['light_amber']
        else:
            sev, bg = 'LOW', C['light_teal']

        card = FancyBboxPatch(
            (0.3, y - 0.32), 9.4, 0.64,
            boxstyle="round,pad=0.05", facecolor=bg,
            edgecolor=sev_color, linewidth=1.0, alpha=0.6)
        ax.add_patch(card)

        ax.text(0.6, y + 0.07, name, fontsize=14, fontweight='bold',
                color=sev_color, va='center')

        p_s = (f"p={p_val:.1e}" if p_val < 0.001
               else f"p={p_val:.3f}")
        ax.text(0.6, y - 0.17,
                f"\u0394={delta:+.4f}  {p_s}  ({n_genes} genes)",
                fontsize=12, color='#555555', va='center')

        badge = FancyBboxPatch(
            (8.6, y - 0.14), 1.0, 0.28,
            boxstyle="round,pad=0.03", facecolor=sev_color,
            edgecolor='none', alpha=0.85)
        ax.add_patch(badge)
        ax.text(9.1, y, sev, fontsize=12, fontweight='bold',
                color='white', ha='center', va='center')

        if not is_aging and hallmark:
            tag = HALLMARK_SHORT_NAMES.get(hallmark, hallmark)
            ax.text(5.5, y + 0.07, tag, fontsize=12, color=sev_color,
                    va='center', style='italic')

    sep_y = 9.55 - len(modules) * 0.85 + 0.15
    ax.plot([0.3, 9.7], [sep_y, sep_y], color=C['lgrey'], linewidth=1.5)

    drug_title_y = sep_y - 0.35
    ax.text(0.3, drug_title_y, "Recommended compounds", fontsize=18,
            fontweight='bold', color=C['navy'])

    compounds = data.get('top_compounds', [])[:5]
    for i, comp in enumerate(compounds):
        y = drug_title_y - 0.65 - i * 0.75
        is_known = comp.get('is_known_drug', False)

        if is_known:
            bg, border, badge_txt = C['light_green'], C['green'], 'KNOWN'
        else:
            bg, border, badge_txt = C['light_purple'], C['purple'], 'CANDIDATE'

        card = FancyBboxPatch(
            (0.3, y - 0.3), 9.4, 0.6,
            boxstyle="round,pad=0.05", facecolor=bg,
            edgecolor=border,
            linewidth=1.2 if i < 2 else 0.8, alpha=0.6)
        ax.add_patch(card)

        rank = comp.get('rank', i + 1)
        rc = C['green'] if rank == 1 else (
            C['blue'] if rank <= 3 else C['grey'])
        circle = plt.Circle(
            (0.75, y), 0.2, facecolor=rc, edgecolor='none', alpha=0.9)
        ax.add_patch(circle)
        ax.text(0.75, y, f'#{rank}', fontsize=12, fontweight='bold',
                color='white', ha='center', va='center')

        cname = comp.get('compound_name', 'Unknown')
        ax.text(1.2, y + 0.06, cname, fontsize=16, fontweight='bold',
                color=C['navy'] if rank <= 2 else '#333333', va='center')

        nt = comp.get('n_targets', 0)
        imp = comp.get('importance', 0)
        ax.text(1.2, y - 0.16, f"targets: {nt}  importance: {imp}",
                fontsize=12, color='#777777', va='center')

        brect = FancyBboxPatch(
            (8.0, y - 0.13), 1.6, 0.26,
            boxstyle="round,pad=0.03", facecolor=border,
            edgecolor='none', alpha=0.85)
        ax.add_patch(brect)
        ax.text(8.8, y, badge_txt, fontsize=12, fontweight='bold',
                color='white', ha='center', va='center')

    level, lcolor, detail = _confidence(data)
    conf_y = drug_title_y - 0.65 - len(compounds) * 0.75 - 0.3
    crect = FancyBboxPatch(
        (0.3, conf_y - 0.2), 9.4, 0.4,
        boxstyle="round,pad=0.04", facecolor=lcolor,
        edgecolor='none', alpha=0.12)
    ax.add_patch(crect)
    ax.text(5, conf_y, f"Overall: {level} \u2014 {detail}",
            fontsize=14, fontweight='bold', ha='center',
            va='center', color=lcolor)

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    return fig

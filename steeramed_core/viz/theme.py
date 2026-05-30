"""
Visualization theme and utilities for Nature-grade figure output.

Provides a unified color palette (PALETTE, HALLMARK_COLORS), rcParams
configuration, and helper functions for consistent figure styling.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

FIG_DIR = Path.cwd() / "results" / "figures"

PALETTE = {
    'navy': '#1A237E',
    'blue': '#2166AC',
    'red': '#C62828',
    'green': '#2E7D32',
    'teal': '#00897B',
    'orange': '#E65100',
    'purple': '#7B1FA2',
    'grey': '#757575',
    'amber': '#F9A825',
    'lgrey': '#E0E0E0',
    'light_green': '#E8F5E9',
    'light_red': '#FFEBEE',
    'light_blue': '#E3F2FD',
    'light_amber': '#FFF8E1',
    'light_purple': '#F3E5F5',
    'light_teal': '#E0F2F1',
}

HALLMARK_COLORS = {
    "Chronic Inflammation": '#C62828',
    "Epigenetic Alterations": '#7B1FA2',
    "Disabled Autophagy": '#E65100',
    "Stem Cell Exhaustion": '#00897B',
    "Loss of Proteostasis": '#F9A825',
    "Genomic Instability": '#757575',
    "Mitochondrial Dysfunction": '#2166AC',
}

HALLMARK_SHORT_NAMES = {
    "Chronic Inflammation": "Inflammaging",
    "Epigenetic Alterations": "Epigenetic Drift",
    "Disabled Autophagy": "Autophagy Decline",
    "Stem Cell Exhaustion": "Stem Cell Loss",
    "Loss of Proteostasis": "Proteostasis Loss",
    "Genomic Instability": "Genomic Damage",
    "Mitochondrial Dysfunction": "Mito. Dysfunc.",
}


def setup():
    """Configure matplotlib rcParams for Nature-grade figure output.

    Sets font family, sizes, spine visibility, DPI, and savefig
    defaults suitable for print-quality figures.
    """
    mpl.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'svg.fonttype': 'none',
        'pdf.fonttype': 42,
        'font.size': 8,
        'axes.linewidth': 0.5,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.labelsize': 8,
        'axes.titlesize': 9,
        'axes.titleweight': 'bold',
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
        'legend.fontsize': 6,
        'legend.frameon': False,
        'legend.handlelength': 1.5,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'savefig.transparent': False,
        'mathtext.default': 'regular',
    })


def panel_label(ax, text, x=-0.15, y=1.08, fontsize=11):
    """Place a bold panel label (e.g. 'a', 'b') on an axes.

    Args:
        ax: Matplotlib axes to annotate.
        text: Label string (typically a single lowercase letter).
        x: Horizontal position in axes coordinates.
        y: Vertical position in axes coordinates.
        fontsize: Font size for the label.
    """
    ax.text(x, y, text, transform=ax.transAxes, fontsize=fontsize,
            fontweight='bold', va='top', ha='right')


def save_figure(fig, name, formats=('pdf', 'png'), dpi=300):
    """Save a figure to the default FIG_DIR in multiple formats.

    Args:
        fig: Matplotlib figure to save.
        name: Base filename (without extension).
        formats: Tuple of file extensions to export.
        dpi: Resolution for raster formats (png, tiff).
    """
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        p = FIG_DIR / f"{name}.{ext}"
        kwargs = {'bbox_inches': 'tight', 'pad_inches': 0.05}
        if ext in ('png', 'tiff'):
            kwargs['dpi'] = dpi
        fig.savefig(str(p), format=ext, **kwargs)
    plt.close(fig)

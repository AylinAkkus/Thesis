#!/usr/bin/env python3
"""
Create a side-by-side progress figure for ScreenSpot Pro and OS-World-G.

Shows progress from baseline 7B models to our SFT-7B (63k) and
SFT-7B Soup (4x uniform, 63k), with per-step improvement annotations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Hard-coded accuracies from the provided comparison table
SSP_VALUES = {
    'SFT-7B (63k)': 50.09,
    'SFT-7B (114k)': 49.6,
    'SFT-7B Soup (4x, 63k)': 51.6,
    'OpenCUA-7B (RL)': 50.0,
    'GTA1-7B (RL)': 50.1,
    'UI-Venus-7B (RL)': 50.8,
}

OSW_VALUES = {
    'SFT-7B (63k)': 60.1,
    'SFT-7B (114k)': 60.1,
    'SFT-7B Soup (4x, 63k)': 60.2,
    'OpenCUA-7B (RL)': 55.3,
    'GTA1-7B (RL)': 67.7,
    'UI-Venus-7B (RL)': 58.8,
    'GTA1-32B': 61.8,
}

# RL-improved target accuracies to overlay as extensions on existing bars
SSP_RL_TARGETS = {
    'SFT-7B (63k)': 50.66,
    'SFT-7B Soup (4x, 63k)': 52.25,
}

OSW_RL_TARGETS = {
    'SFT-7B (63k)': 61.10,
    'SFT-7B Soup (4x, 63k)': 62.05,
}

def _add_delta_box(ax, x0, y0, x1, y1, text_color='darkred'):
    """Annotate improvement between two bars centered between them."""
    improvement = y1 - y0
    mid_x = (x0 + x1) / 2
    mid_y = (y0 + y1) / 2
    ax.annotate(
        f"{improvement:+.2f}pp",
        xy=(mid_x, mid_y),
        ha='center',
        va='center',
        fontsize=8,
        color=text_color,
        fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=text_color, alpha=0.9),
    )


def _add_callout(ax, x_index, y_value, text, dx=-0.7, dy=1.5):
    """Add a callout label with arrow for a specific bar index and value."""
    ax.annotate(
        text,
        xy=(x_index, y_value),
        xytext=(x_index + dx, y_value + dy),
        textcoords='data',
        ha='right',
        va='bottom',
        fontsize=8,
        fontweight='bold',
        color='darkred',
        arrowprops=dict(arrowstyle='->', color='darkred', lw=1.2),
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='darkred', alpha=0.9),
    )


def _add_gain_extension(ax, x_index, y_from, y_to, bar_width, color='forestgreen', label_text=None):
    """Overlay an 'extension' above a bar to indicate improved target.

    Draws a semi-transparent rectangle on top of the bar and an arrow to the
    target value, optionally labeling the new value.
    """
    height = y_to - y_from
    if height <= 0:
        return

    extension_width = bar_width * 0.6
    # Draw the extension as a translucent green overlay, centered on the bar
    ax.bar(
        x_index,
        height,
        bottom=y_from,
        width=extension_width,
        color='#2ecc71',
        alpha=0.35,
        edgecolor=color,
        linewidth=1.5,
        zorder=4,
    )

    # Add a subtle upward arrow to the target
    ax.annotate(
        '',
        xy=(x_index, y_to),
        xytext=(x_index, y_from + height * 0.15),
        arrowprops=dict(arrowstyle='-|>', lw=1.2, color=color),
        zorder=5,
    )

    if label_text is not None:
        ax.text(
            x_index,
            y_to + 0.3,
            label_text,
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold',
            color=color,
            zorder=6,
        )


def create_progress_figure():
    """Create a 1x2 figure showing SS Pro and OS-World-G progress."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    # Left subplot: ScreenSpot Pro
    ax_left = axes[0]
    ssp_ui_venus = ('UI-Venus-7B (RL)', SSP_VALUES['UI-Venus-7B (RL)'])
    ssp_gta1 = ('GTA1-7B (RL)', SSP_VALUES['GTA1-7B (RL)'])
    ssp_ours_63k = ('SFT-7B (63k)', SSP_VALUES['SFT-7B (63k)'])
    ssp_ours_soup = ('SFT-7B Soup (4x, 63k)', SSP_VALUES['SFT-7B Soup (4x, 63k)'])

    ssp_labels = [
        'UI-Venus-7B',
        'GTA1-7B',
        'SFT-7B\n(63k)',
        'SFT-7B\n(63k) + RL',
        'SFT-7B Soup\n(4x, 63k)',
        'SFT-7B Soup\n(4x, 63k) + RL',
    ]
    ssp_values = [
        ssp_ui_venus[1],
        ssp_gta1[1],
        ssp_ours_63k[1],
        SSP_RL_TARGETS['SFT-7B (63k)'],
        ssp_ours_soup[1],
        SSP_RL_TARGETS['SFT-7B Soup (4x, 63k)'],
    ]

    # Colors: baselines in blue hues, ours in red, RL in green
    ssp_colors = ['#2E86AB', '#5DADE2', '#CD5C5C', '#2ecc71', '#8B0000', '#27ae60']
    bars = ax_left.bar(range(len(ssp_values)), ssp_values, color=ssp_colors, alpha=0.9, zorder=3)
    for i, bar in enumerate(bars):
        if i == 0:  # UI-Venus baseline
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
            bar.set_linestyle('-')
        elif i == 1:  # GTA1 baseline
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
            bar.set_linestyle('--')
        elif i == 2:  # 63k baseline
            bar.set_edgecolor('darkred')
            bar.set_linewidth(2)
            bar.set_linestyle('--')
        elif i == 3:  # 63k + RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(2)
            bar.set_linestyle('-')
        elif i == 4:  # Soup baseline
            bar.set_edgecolor('darkred')
            bar.set_linewidth(4)
            bar.set_linestyle('-')
        else:  # Soup + RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(3)
            bar.set_linestyle('-')

    # Value labels
    for i, (bar, val) in enumerate(zip(bars, ssp_values)):
        label_color = 'black'
        if i in (2, 4):
            label_color = 'darkred'
        elif i in (3, 5):
            label_color = 'forestgreen'
        ax_left.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 0.3,
            f"{val:.2f}%",
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold' if i >= 2 else 'normal',
            color=label_color,
            zorder=5,
        )

    # Arrows highlighting improvement from baseline to + RL bars
    ssp_centers = [bar.get_x() + bar.get_width() / 2.0 for bar in bars]
    ax_left.annotate(
        '',
        xy=(ssp_centers[3], ssp_values[3]),
        xytext=(ssp_centers[2], ssp_values[2]),
        arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.5),
        zorder=6,
    )
    ax_left.annotate(
        '',
        xy=(ssp_centers[5], ssp_values[5]),
        xytext=(ssp_centers[4], ssp_values[4]),
        arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.5),
        zorder=6,
    )

    ax_left.set_title('ScreenSpot Pro', fontsize=12, fontweight='bold', pad=10)
    ax_left.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax_left.set_xticks(range(len(ssp_labels)))
    ax_left.set_xticklabels(ssp_labels, rotation=0, ha='center', fontsize=9)
    ax_left.set_ylim(35, 55)
    ax_left.grid(True, alpha=0.3, axis='y', zorder=0)

    # Right subplot: OS-World-G
    ax_right = axes[1]
    osw_ui_venus = ('UI-Venus-7B (RL)', OSW_VALUES['UI-Venus-7B (RL)'])
    osw_gta1 = ('GTA1-7B (RL)', OSW_VALUES['GTA1-7B (RL)'])
    osw_gta1_32b = ('GTA1-32B', OSW_VALUES['GTA1-32B'])
    osw_ours_63k = ('SFT-7B (63k)', OSW_VALUES['SFT-7B (63k)'])
    osw_ours_soup = ('SFT-7B Soup (4x, 63k)', OSW_VALUES['SFT-7B Soup (4x, 63k)'])

    osw_labels = [
        'UI-Venus-7B',
        'GTA1-7B',
        'GTA1-32B',
        'SFT-7B\n(63k)',
        'SFT-7B\n(63k) + RL',
        'SFT-7B Soup\n(4x, 63k)',
        'SFT-7B Soup\n(4x, 63k) + RL',
    ]
    osw_values = [
        osw_ui_venus[1],
        osw_gta1[1],
        osw_gta1_32b[1],
        osw_ours_63k[1],
        OSW_RL_TARGETS['SFT-7B (63k)'],
        osw_ours_soup[1],
        OSW_RL_TARGETS['SFT-7B Soup (4x, 63k)'],
    ]

    osw_colors = ['#2E86AB', '#5DADE2', '#85C1E9', '#CD5C5C', '#2ecc71', '#8B0000', '#27ae60']
    bars_r = ax_right.bar(range(len(osw_values)), osw_values, color=osw_colors, alpha=0.9, zorder=3)
    for i, bar in enumerate(bars_r):
        if i == 0:  # UI-Venus baseline
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
            bar.set_linestyle('-')
        elif i == 1:  # GTA1 baseline
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
            bar.set_linestyle('--')
        elif i == 2:  # GTA1-32B baseline
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
            bar.set_linestyle('-')
        elif i == 3:  # 63k baseline
            bar.set_edgecolor('darkred')
            bar.set_linewidth(2)
            bar.set_linestyle('--')
        elif i == 4:  # 63k + RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(2)
            bar.set_linestyle('-')
        elif i == 5:  # Soup baseline
            bar.set_edgecolor('darkred')
            bar.set_linewidth(4)
            bar.set_linestyle('-')
        else:  # i == 6, Soup + RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(3)
            bar.set_linestyle('-')

    for i, (bar, val) in enumerate(zip(bars_r, osw_values)):
        label_color = 'black'
        # Determine dynamic indices for coloring
        idx_63k = osw_labels.index('SFT-7B\n(63k)')
        idx_63k_rl = osw_labels.index('SFT-7B\n(63k) + RL')
        idx_soup = osw_labels.index('SFT-7B Soup\n(4x, 63k)')
        idx_soup_rl = osw_labels.index('SFT-7B Soup\n(4x, 63k) + RL')
        if i in (idx_63k, idx_soup):
            label_color = 'darkred'
        elif i in (idx_63k_rl, idx_soup_rl):
            label_color = 'forestgreen'
        ax_right.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 0.3,
            f"{val:.1f}%",
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold' if i >= 2 else 'normal',
            color=label_color,
            zorder=5,
        )

    # Arrows highlighting improvement from baseline to + RL bars (dynamic indices)
    osw_centers = [bar.get_x() + bar.get_width() / 2.0 for bar in bars_r]
    i_63k = osw_labels.index('SFT-7B\n(63k)')
    i_63k_rl = osw_labels.index('SFT-7B\n(63k) + RL')
    i_soup = osw_labels.index('SFT-7B Soup\n(4x, 63k)')
    i_soup_rl = osw_labels.index('SFT-7B Soup\n(4x, 63k) + RL')
    ax_right.annotate(
        '',
        xy=(osw_centers[i_63k_rl], osw_values[i_63k_rl]),
        xytext=(osw_centers[i_63k], osw_values[i_63k]),
        arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.5),
        zorder=6,
    )
    ax_right.annotate(
        '',
        xy=(osw_centers[i_soup_rl], osw_values[i_soup_rl]),
        xytext=(osw_centers[i_soup], osw_values[i_soup]),
        arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.5),
        zorder=6,
    )

    ax_right.set_title('OS-World-G', fontsize=12, fontweight='bold', pad=10)
    ax_right.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax_right.set_xticks(range(len(osw_labels)))
    ax_right.set_xticklabels(osw_labels, rotation=0, ha='center', fontsize=9)
    ax_right.set_ylim(50, 70)
    ax_right.grid(True, alpha=0.3, axis='y', zorder=0)

    # Layout and overall title
    fig.suptitle('Progress of SFT-7B on ScreenSpot Pro and OS-World-G', fontsize=14, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0.0, 1, 0.95])

    return fig


def save_plot():
    """Save the combined progress figure to the data directory."""
    fig = create_progress_figure()

    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)

    output_path_png = output_dir / 'progress_sspro_osworld.png'
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')

    print(f"Plot saved to: {output_path_png}")

    plt.show()
    return output_path_png


if __name__ == "__main__":
    save_plot()



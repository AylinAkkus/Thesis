#!/usr/bin/env python3
"""
Create a side-by-side progress figure for ScreenSpot Pro and OS-World-G,
without Soup model variants. RL labels are renamed to "v1 RL pipeline".
"""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Hard-coded accuracies (Soup variants removed)
SSP_VALUES = {
    'SFT-7B (63k)': 50.09,
    'GTA1-7B (RL)': 50.1,
    'UI-Venus-7B (RL)': 50.8,
}

OSW_VALUES = {
    'SFT-7B (63k)': 60.1,
    'UI-Venus-7B (RL)': 58.8,
    'GTA1-7B (RL)': 67.7,
    'GTA1-32B': 61.8,
}

# RL-improved target accuracies to overlay as extensions on existing bars
SSP_RL_TARGETS = {
    'SFT-7B (63k)': 50.66,
}

OSW_RL_TARGETS = {
    'SFT-7B (63k)': 61.10,
}


def create_progress_figure():
    """Create a 1x2 figure showing SS Pro and OS-World-G progress (no Soup)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    # Left subplot: ScreenSpot Pro
    ax_left = axes[0]
    ssp_ui_venus = ('UI-Venus-7B (RL)', SSP_VALUES['UI-Venus-7B (RL)'])
    ssp_gta1 = ('GTA1-7B (RL)', SSP_VALUES['GTA1-7B (RL)'])
    ssp_ours_63k = ('SFT-7B (63k)', SSP_VALUES['SFT-7B (63k)'])

    ssp_labels = [
        'UI-Venus-7B',
        'GTA1-7B',
        'SFT-7B\n(63k)',
        'SFT-7B\n(63k) + v1 RL pipeline',
    ]
    ssp_values = [
        ssp_ui_venus[1],
        ssp_gta1[1],
        ssp_ours_63k[1],
        SSP_RL_TARGETS['SFT-7B (63k)'],
    ]

    # Colors: baselines in blue hues, ours in red, RL in green
    ssp_colors = ['#2E86AB', '#5DADE2', '#CD5C5C', '#2ecc71']
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
        else:  # 63k + v1 RL pipeline
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(2)
            bar.set_linestyle('-')

    # Value labels
    for i, (bar, val) in enumerate(zip(bars, ssp_values)):
        label_color = 'black'
        if i == 2:
            label_color = 'darkred'
        elif i == 3:
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

    # Arrow highlighting improvement from baseline to + v1 RL pipeline
    ssp_centers = [bar.get_x() + bar.get_width() / 2.0 for bar in bars]
    ax_left.annotate(
        '',
        xy=(ssp_centers[3], ssp_values[3]),
        xytext=(ssp_centers[2], ssp_values[2]),
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

    osw_labels = [
        'UI-Venus-7B',
        'GTA1-7B',
        'GTA1-32B',
        'SFT-7B\n(63k)',
        'SFT-7B\n(63k) + v1 RL pipeline',
    ]
    osw_values = [
        osw_ui_venus[1],
        osw_gta1[1],
        osw_gta1_32b[1],
        osw_ours_63k[1],
        OSW_RL_TARGETS['SFT-7B (63k)'],
    ]

    osw_colors = ['#2E86AB', '#5DADE2', '#85C1E9', '#CD5C5C', '#2ecc71']
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
        else:  # 63k + v1 RL pipeline
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(2)
            bar.set_linestyle('-')

    for i, (bar, val) in enumerate(zip(bars_r, osw_values)):
        label_color = 'black'
        idx_63k = osw_labels.index('SFT-7B\n(63k)')
        idx_63k_rl = osw_labels.index('SFT-7B\n(63k) + v1 RL pipeline')
        if i == idx_63k:
            label_color = 'darkred'
        elif i == idx_63k_rl:
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

    # Arrow highlighting improvement from baseline to + v1 RL pipeline
    osw_centers = [bar.get_x() + bar.get_width() / 2.0 for bar in bars_r]
    i_63k = osw_labels.index('SFT-7B\n(63k)')
    i_63k_rl = osw_labels.index('SFT-7B\n(63k) + v1 RL pipeline')
    ax_right.annotate(
        '',
        xy=(osw_centers[i_63k_rl], osw_values[i_63k_rl]),
        xytext=(osw_centers[i_63k], osw_values[i_63k]),
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
    fig.suptitle('Progress of SFT-7B on ScreenSpot Pro and OS-World-G (no Soup)', fontsize=14, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0.0, 1, 0.95])

    return fig


def save_plot():
    """Save the combined progress figure to the data directory."""
    fig = create_progress_figure()

    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)

    output_path_png = output_dir / 'progress_sspro_osworld_nosoup.png'
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')

    print(f"Plot saved to: {output_path_png}")

    plt.show()
    return output_path_png


if __name__ == "__main__":
    save_plot()



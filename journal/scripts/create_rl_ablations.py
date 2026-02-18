#!/usr/bin/env python3
"""
Visualize RL ablations (excluding decoding):
- Temperature ablation: 1.4 vs 1.7 (selected)
- Data pool ablation: 20% vs 30% 0-reward (20% selected)

Numbers are taken from journal/improve_rl_gains_through_better_diversity.md
"""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# Style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


# Data
TEMP_ABLATION = {
    1.4: {
        'SS Pro': 53.00,
        'OS-World-G': 63.1,
    },
    1.7: {  # selected
        'SS Pro': 53.57,
        'OS-World-G': 63.6,
    },
}

DATA_POOL_ABLATION = {
    '20% 0-reward (selected)': {
        'SS Pro': 53.57,
        'OS-World-G': 63.6,
    },
    '30% 0-reward': {
        'SS Pro': 52.81,
        'OS-World-G': 62.5,
    },
}


def _add_value_labels(ax, rects, decimals=2, color='black', fontweight='bold'):
    for rect in rects:
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2.0,
            height + 0.25,
            f"{height:.{decimals}f}%",
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight=fontweight,
            color=color,
            zorder=5,
        )


def create_figure():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    # Colors
    color_selected = '#2ECC71'
    color_alt_blue = '#7FB3D5'
    color_alt_red = '#F5B7B1'

    # --- Left: Temperature ablation ---
    ax = axes[0]
    groups = ['SS Pro', 'OS-World-G']
    x = list(range(len(groups)))
    width = 0.35
    vals_14 = [TEMP_ABLATION[1.4][g] for g in groups]
    vals_17 = [TEMP_ABLATION[1.7][g] for g in groups]

    bars_14 = ax.bar([xi - width/2 for xi in x], vals_14, width, label='T = 1.4', color=color_alt_red, edgecolor='darkred', zorder=3)
    bars_17 = ax.bar([xi + width/2 for xi in x], vals_17, width, label='T = 1.7 (selected)', color=color_selected, edgecolor='forestgreen', linewidth=1.5, zorder=3)

    _add_value_labels(ax, bars_14, decimals=2, color='darkred', fontweight='normal')
    _add_value_labels(ax, bars_17, decimals=2, color='forestgreen')

    ax.set_title('Temperature Ablation', fontsize=12, fontweight='bold', pad=10)
    ax.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=9)
    ax.set_ylim(52, 66)
    ax.grid(True, alpha=0.3, axis='y', zorder=0)
    ax.legend(frameon=True, fontsize=9)

    # --- Right: Data pool ablation ---
    ax = axes[1]
    pools = list(DATA_POOL_ABLATION.keys())
    x = list(range(len(groups)))
    width = 0.35
    vals_sel = [DATA_POOL_ABLATION[pools[0]][g] for g in groups]
    vals_alt = [DATA_POOL_ABLATION[pools[1]][g] for g in groups]

    bars_sel = ax.bar([xi - width/2 for xi in x], vals_sel, width, label=pools[0], color=color_selected, edgecolor='forestgreen', linewidth=1.5, zorder=3)
    bars_alt = ax.bar([xi + width/2 for xi in x], vals_alt, width, label=pools[1], color=color_alt_red, edgecolor='darkred', zorder=3)

    _add_value_labels(ax, bars_sel, decimals=2, color='forestgreen')
    _add_value_labels(ax, bars_alt, decimals=2, color='darkred', fontweight='normal')

    ax.set_title('Data Pool Ablation', fontsize=12, fontweight='bold', pad=10)
    ax.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=9)
    ax.set_ylim(52, 66)
    ax.grid(True, alpha=0.3, axis='y', zorder=0)
    ax.legend(frameon=True, fontsize=9)

    fig.suptitle('RL Ablations: Temperature and Data Pool', fontsize=14, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    return fig


def save_plot():
    fig = create_figure()
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    output_path_png = output_dir / 'rl_ablations.png'
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Plot saved to: {output_path_png}")
    plt.show()
    return output_path_png


if __name__ == '__main__':
    save_plot()



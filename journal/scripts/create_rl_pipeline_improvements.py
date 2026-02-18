#!/usr/bin/env python3
"""
Visualize improved RL pipeline results from journal/improve_rl_gains_through_better_diversity.md

Only overall progress is shown, with baseline models included.
Left: ScreenSpot Pro. Right: OS-World-G.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# Style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


# Data copied from journal/improve_rl_gains_through_better_diversity.md
# and baseline numbers used elsewhere in the repo.

# Baselines
BASELINES_SSP = {
    'UI-Venus-7B': 50.8,
    'GTA1-7B': 50.1,
}

BASELINES_OSW = {
    'UI-Venus-7B': 58.8,
    'GTA1-7B': 67.7,
    'GTA1-32B': 61.8,
}

# Our models (greedy decoding unless stated otherwise)
OURS_PROGRESS = {
    'SFT-7B 63k': {
        'SS Pro': 50.09,
        'OS-World-G': 60.1,
    },
    'initial RL pipeline (220 steps)': {
        'SS Pro': 50.66,
        'OS-World-G': 61.1,
    },
    'improved RL pipeline (194 steps)': {
        'SS Pro': 53.57,
        'OS-World-G': 63.6,
    },
}

def create_figure():
    # Create 1x2 figure: left SS Pro, right OS-World-G
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    # Colors
    color_baseline = ['#2E86AB', '#5DADE2', '#85C1E9']  # baseline blues
    color_ours_sft = '#CD5C5C'  # IndianRed
    color_ours_rl1 = '#1ABC9C'  # green-ish
    color_ours_rl2 = '#27AE60'  # darker green

    # --- Left: ScreenSpot Pro ---
    ax_left = axes[0]
    labels_left = list(BASELINES_SSP.keys()) + [
        'SFT-7B 63k',
        'initial\nRL\n(220 steps)',
        'improved\nRL\n(194 steps)'
    ]
    values_left = [BASELINES_SSP[lbl] for lbl in BASELINES_SSP] + [
        OURS_PROGRESS['SFT-7B 63k']['SS Pro'],
        OURS_PROGRESS['initial RL pipeline (220 steps)']['SS Pro'],
        OURS_PROGRESS['improved RL pipeline (194 steps)']['SS Pro'],
    ]

    colors_left = color_baseline[:len(BASELINES_SSP)] + [
        color_ours_sft,
        color_ours_rl1,
        color_ours_rl2,
    ]

    bars_left = ax_left.bar(range(len(values_left)), values_left, color=colors_left, alpha=0.9, zorder=3)
    # Edge styles
    for i, bar in enumerate(bars_left):
        if i < len(BASELINES_SSP):
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
        elif i == len(BASELINES_SSP):  # SFT
            bar.set_edgecolor('darkred')
            bar.set_linewidth(2)
            bar.set_linestyle('--')
        elif i == len(BASELINES_SSP) + 1:  # initial RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(2)
        else:  # improved RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(3)

    # Labels above bars
    for i, (bar, val) in enumerate(zip(bars_left, values_left)):
        label_color = 'black'
        if i >= len(BASELINES_SSP):
            label_color = 'forestgreen' if i > len(BASELINES_SSP) else 'darkred'
        ax_left.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 0.3,
            f"{val:.2f}%",
            ha='center', va='bottom', fontsize=9,
            fontweight='bold' if i >= len(BASELINES_SSP) else 'normal',
            color=label_color, zorder=5,
        )

    # Improvement arrow SFT -> improved RL
    centers_left = [bar.get_x() + bar.get_width() / 2.0 for bar in bars_left]
    i_sft = len(BASELINES_SSP)
    i_rl2 = len(BASELINES_SSP) + 2
    ax_left.annotate(
        '',
        xy=(centers_left[i_rl2], values_left[i_rl2]),
        xytext=(centers_left[i_sft], values_left[i_sft]),
        arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.5),
        zorder=6,
    )

    ax_left.set_title('ScreenSpot Pro', fontsize=12, fontweight='bold', pad=10)
    ax_left.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax_left.set_xticks(range(len(labels_left)))
    ax_left.set_xticklabels(labels_left, rotation=0, ha='center', fontsize=9)
    ax_left.set_ylim(48, 56)
    ax_left.grid(True, alpha=0.3, axis='y', zorder=0)

    # --- Right: OS-World-G ---
    ax_right = axes[1]
    labels_right = list(BASELINES_OSW.keys()) + [
        'SFT-7B 63k',
        'initial\nRL\n(220 steps)',
        'improved\nRL\n(194 steps)'
    ]
    values_right = [BASELINES_OSW[lbl] for lbl in BASELINES_OSW] + [
        OURS_PROGRESS['SFT-7B 63k']['OS-World-G'],
        OURS_PROGRESS['initial RL pipeline (220 steps)']['OS-World-G'],
        OURS_PROGRESS['improved RL pipeline (194 steps)']['OS-World-G'],
    ]

    colors_right = color_baseline[:len(BASELINES_OSW)] + [
        color_ours_sft,
        color_ours_rl1,
        color_ours_rl2,
    ]

    bars_right = ax_right.bar(range(len(values_right)), values_right, color=colors_right, alpha=0.9, zorder=3)
    for i, bar in enumerate(bars_right):
        if i < len(BASELINES_OSW):
            bar.set_edgecolor('#1B4F72')
            bar.set_linewidth(2)
            bar.set_linestyle('-' if labels_right[i] != 'GTA1-7B' else '--')
        elif i == len(BASELINES_OSW):  # SFT
            bar.set_edgecolor('darkred')
            bar.set_linewidth(2)
            bar.set_linestyle('--')
        elif i == len(BASELINES_OSW) + 1:  # initial RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(2)
        else:  # improved RL
            bar.set_edgecolor('forestgreen')
            bar.set_linewidth(3)

    for i, (bar, val) in enumerate(zip(bars_right, values_right)):
        label_color = 'black'
        if i >= len(BASELINES_OSW):
            label_color = 'forestgreen' if i > len(BASELINES_OSW) else 'darkred'
        ax_right.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 0.3,
            f"{val:.1f}%",
            ha='center', va='bottom', fontsize=9,
            fontweight='bold' if i >= len(BASELINES_OSW) else 'normal',
            color=label_color, zorder=5,
        )

    centers_right = [bar.get_x() + bar.get_width() / 2.0 for bar in bars_right]
    i_sft_r = len(BASELINES_OSW)
    i_rl2_r = len(BASELINES_OSW) + 2
    ax_right.annotate(
        '',
        xy=(centers_right[i_rl2_r], values_right[i_rl2_r]),
        xytext=(centers_right[i_sft_r], values_right[i_sft_r]),
        arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.5),
        zorder=6,
    )

    ax_right.set_title('OS-World-G', fontsize=12, fontweight='bold', pad=10)
    ax_right.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax_right.set_xticks(range(len(labels_right)))
    ax_right.set_xticklabels(labels_right, rotation=0, ha='center', fontsize=9)
    ax_right.set_ylim(56, 70)
    ax_right.grid(True, alpha=0.3, axis='y', zorder=0)

    fig.suptitle('Overall Progress with Baselines', fontsize=14, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    return fig


def save_plot():
    fig = create_figure()
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    output_path_png = output_dir / 'rl_pipeline_improvements.png'
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Plot saved to: {output_path_png}")
    plt.show()
    return output_path_png


if __name__ == '__main__':
    save_plot()



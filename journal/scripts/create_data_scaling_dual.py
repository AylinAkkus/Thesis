#!/usr/bin/env python3
"""
Create a dual-axis line plot showing the impact of data scaling
on both ScreenSpot Pro and ScreenSpot V2 performance.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')

# Data scaling results (unique best configuration per scale)
scales =    [10,    20,    35,    80]
ss_pro =    [45.22, 46.55, 47.18, 49.65]
ss_v2  =    [91.05, 90.27, 90.66, 90.79]

def create_plot():
    fig, ax1 = plt.subplots(figsize=(7, 4.5))

    color_pro = '#2E86AB'
    color_v2  = '#E8553A'

    # ScreenSpot Pro on left axis
    ln1 = ax1.plot(scales, ss_pro, 's-', color=color_pro, linewidth=2,
                   markersize=8, markeredgecolor='white', markeredgewidth=1.2,
                   label='ScreenSpot Pro', zorder=3)
    ax1.set_xlabel('Training Samples (k)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11,
                   fontweight='bold', color=color_pro)
    ax1.tick_params(axis='y', labelcolor=color_pro)
    ax1.set_ylim(43, 52)

    # ScreenSpot V2 on right axis
    ax2 = ax1.twinx()
    ln2 = ax2.plot(scales, ss_v2, 'o--', color=color_v2, linewidth=2,
                   markersize=8, markeredgecolor='white', markeredgewidth=1.2,
                   label='ScreenSpot V2', zorder=3)
    ax2.set_ylabel('ScreenSpot V2 Accuracy (%)', fontsize=11,
                   fontweight='bold', color=color_v2)
    ax2.tick_params(axis='y', labelcolor=color_v2)
    ax2.set_ylim(88, 93)

    # Shared x-axis
    ax1.set_xticks(scales)
    ax1.set_xticklabels([f'{s}k' for s in scales], fontsize=10)

    # Value annotations for SS Pro (below the markers)
    for x, y in zip(scales, ss_pro):
        ax1.annotate(f'{y:.1f}', (x, y), textcoords='offset points',
                     xytext=(0, -15), ha='center', fontsize=8, color=color_pro,
                     fontweight='bold')

    # Value annotations for SS V2 (above the markers)
    for x, y in zip(scales, ss_v2):
        ax2.annotate(f'{y:.1f}', (x, y), textcoords='offset points',
                     xytext=(0, 12), ha='center', fontsize=8, color=color_v2,
                     fontweight='bold')

    # Combined legend
    lines = ln1 + ln2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=9, frameon=True,
               fancybox=True, shadow=False)

    ax1.grid(True, alpha=0.3, axis='y')
    ax2.grid(False)

    plt.title('Impact of Data Scale on Grounding Accuracy',
              fontsize=12, fontweight='bold', pad=12)
    fig.tight_layout()
    return fig


def save_plot():
    fig = create_plot()
    output_path = Path(__file__).resolve().parent.parent.parent / 'figures' / 'DataScaling.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Plot saved to: {output_path}")
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    save_plot()


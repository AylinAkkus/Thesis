#!/usr/bin/env python3
"""
Recreate the dual bar plot showing model performance on ScreenSpot Pro
stratified by image resolution and aspect ratio.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')

# --- Data from Table 1: Performance by Image Resolution ---
resolution_labels = ['2-3MP', '3-4MP', '4-5MP', '5-6MP', '6-8MP', '>8MP']
resolution_accuracy = [15.79, 54.49, 44.92, 67.78, 43.75, 32.19]
resolution_counts = [19, 613, 236, 90, 272, 351]

# --- Data from Table 2: Performance by Aspect Ratio ---
aspect_labels = ['1.5', '1.6', '1.8', '3.6']
aspect_accuracy = [56.17, 57.14, 43.33, 39.67]
aspect_counts = [308, 147, 884, 242]

# Overall accuracy
overall_accuracy = 46.55


def create_plot():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # ── Left subplot: Image Resolution ──
    x1 = np.arange(len(resolution_labels))
    bars1 = ax1.bar(x1, resolution_accuracy, color='#4C8CBF', edgecolor='white', width=0.6)
    ax1.axhline(y=overall_accuracy, color='red', linestyle='--', linewidth=1.5,
                label=f'Overall Accuracy: {overall_accuracy:.1f}%')

    # Bar labels with accuracy and sample count
    for i, (bar, acc, n) in enumerate(zip(bars1, resolution_accuracy, resolution_counts)):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
                 f'{acc:.1f}%\n(n={n})', ha='center', va='bottom', fontsize=9)

    ax1.set_xlabel('Image Size (Megapixels)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x1)
    ax1.set_xticklabels(resolution_labels, fontsize=10)
    ax1.set_ylim(0, 82)
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(axis='y', alpha=0.3)

    # ── Right subplot: Aspect Ratio ──
    x2 = np.arange(len(aspect_labels))
    bars2 = ax2.bar(x2, aspect_accuracy, color='#4E9F50', edgecolor='white', width=0.6)
    ax2.axhline(y=overall_accuracy, color='red', linestyle='--', linewidth=1.5,
                label=f'Overall Accuracy: {overall_accuracy:.1f}%')

    # Bar labels with accuracy and sample count
    for i, (bar, acc, n) in enumerate(zip(bars2, aspect_accuracy, aspect_counts)):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
                 f'{acc:.1f}%\n(n={n})', ha='center', va='bottom', fontsize=9)

    ax2.set_xlabel('Aspect Ratio', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(aspect_labels, fontsize=10)
    ax2.set_ylim(0, 82)
    ax2.legend(fontsize=10, loc='upper right')
    ax2.grid(axis='y', alpha=0.3)

    # ── Shared title ──
    fig.suptitle('Model Performance on ScreenSpotPro Benchmark\nacross Image Size and Aspect Ratio',
                 fontsize=14, fontweight='bold', y=1.01)

    plt.tight_layout()
    return fig


def save_plot():
    fig = create_plot()
    out_dir = Path(__file__).resolve().parent.parent.parent / 'figures'
    out_path = out_dir / 'accuracy_by_resolution_and_aspect.png'
    fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved plot to {out_path}')


if __name__ == '__main__':
    save_plot()


#!/usr/bin/env python3
"""
Create a single summary figure capturing SS Pro progress:

- Waterfall-style cumulative improvements from a pre hi-res baseline to the current best.
- Annotates the high-resolution training delta from 28.65 to the early hi-res baseline (36.12).

Saves to journal/scripts/data/sspro_progress_summary.png
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import colors as mcolors
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
from pathlib import Path

# Style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# -----------------------------
# Data (from journal markdowns)
# -----------------------------

# We treat 36.12% (default prompt + image resolution) as an early hi-res baseline from
# how_does_prompt_impact_qwen_2_5_vl_training_?.md. Add pre hi-res 28.65% before it.
pre_hires_baseline = 28.65
baseline_early = 36.12

# Prompt improvement (default prompt without resolution performed better on SS Pro)
prompt_best = 39.03  # from how_does_prompt_impact_qwen_2_5_vl_training_?.md

# Model difficulty filtering (10k) using Qwen 2.5 VL 7B for easy and GTA1-7B for hard
filtering_easy_hard = 45.22  # from impact_of_model_difficulty_filtering_?.md

# Data scaling progression (without replacement unless noted)
scale_20k = 46.55  # from how_does_scaling_data_impact_sft_?.md
scale_35k = 47.18  # from how_does_scaling_data_impact_sft_?.md
scale_80k_plus = 49.65  # 80k + improved prompt + pro apps data (best so far)
scale_114k = 50.41  # 114k + improved prompt + pro apps data

# Reference: a recent competitive open-source model (GTA1-7B) for dotted line
reference_sota = 50.10
# Future projection (purely illustrative; no numeric value shown on the plot). Push visually to top.
future_projection = 54.5


def create_summary_figure():
    fig = plt.figure(figsize=(9, 6))

    # Single plot: Waterfall-style cumulative improvements
    ax1 = fig.add_subplot(1, 1, 1)

    stages = [
        ("1MP\nBaseline", pre_hires_baseline),
        ("4MP", baseline_early),
        ("+ Better training\nprompt", prompt_best),
        ("+ Model\nfiltering", filtering_easy_hard),
        ("+ Scale to\n20k", scale_20k),
        ("+ Scale to\n35k", scale_35k),
        ("+ Scale to\n80K + YouTube", scale_80k_plus),
        ("+ Scale to\n114K", scale_114k),
        ("Future:\nPro App Knowledge + RL", future_projection),
    ]

    # Monochrome bars (gradually darker) to emphasize milestone arrows
    n_stages = len(stages)
    if n_stages > 1:
        gray_vals = np.linspace(0.9, 0.35, n_stages)
    else:
        gray_vals = [0.6]
    colors = [mcolors.to_hex((g, g, g)) for g in gray_vals]

    xs = list(range(len(stages)))
    ys = [acc for _, acc in stages]

    bars = ax1.bar(xs, ys, color=colors, edgecolor='#444444', linewidth=1.2, alpha=1.0)
    # Style the future bar specially (hatched, distinct edge color)
    if len(bars) == len(stages) and len(bars) > 0:
        future_bar = bars[-1]
        future_bar.set_hatch('///')
        future_bar.set_alpha(0.9)
        future_bar.set_edgecolor('#444444')
        future_bar.set_linewidth(1.5)

    # Add labels and improvement annotations
    for i, bar in enumerate(bars):
        height = bar.get_height()
        # Do not show a numeric value on the future bar
        if i == len(bars) - 1:
            ax1.text(bar.get_x() + bar.get_width() / 2.0, height + 0.5,
                     "Future\n(Pro App Knowledge + RL)",
                     ha='center', va='bottom', fontsize=8, fontweight='bold', color='#6A5ACD')
        else:
            ax1.text(bar.get_x() + bar.get_width() / 2.0, height + 0.5,
                     f"{ys[i]:.2f}%", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#333333')
        # Remove all per-step +XXpp box annotations in favor of arrow labels

    # Reference SOTA line
    ax1.axhline(reference_sota, linestyle='--', color='#2E86AB', linewidth=1.5, alpha=0.8)
    ax1.text(len(stages) - 0.6, reference_sota + 0.4, 'GTA1-7B 50.1%', color='#2E86AB', fontsize=8)
    # Arrow annotation highlighting SOTA reference
    ax1.annotate('Reference: GTA1-7B 50.1%',
                 xy=(len(stages) - 1.2, reference_sota),
                 xytext=(len(stages) - 2.8, reference_sota + 3.0),
                 arrowprops=dict(arrowstyle='->', color='#2E86AB', lw=1.5),
                 color='#2E86AB', fontsize=8, fontweight='bold', ha='left', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#2E86AB', alpha=0.9))

    labels = [label for label, _ in stages]
    # Remove x-axis label for the future bar
    if labels:
        labels[-1] = ""
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels, rotation=15, ha='right', fontsize=9)
    ax1.set_ylim(25, 55)
    ax1.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11, fontweight='bold')
    ax1.set_title('How to Train a Strong Grounding Model (Data Perspective)', fontsize=12, fontweight='bold', pad=10)
    ax1.grid(True, axis='y', alpha=0.3)

    # Remove previous bracket summary; arrows will carry deltas

    # Gradient arrows for major milestones
    def draw_gradient_arrow(ax, x0, y0, x1, y1, color_start, color_end, label):
        steps = 50
        c0 = np.array(mcolors.to_rgb(color_start))
        c1 = np.array(mcolors.to_rgb(color_end))
        # Draw white outline first for contrast
        for t0, t1 in zip(np.linspace(0, 1, steps, endpoint=False), np.linspace(0, 1, steps, endpoint=False)[1:].tolist() + [1.0]):
            xt0 = x0 + (x1 - x0) * t0
            yt0 = y0 + (y1 - y0) * t0
            xt1 = x0 + (x1 - x0) * t1
            yt1 = y0 + (y1 - y0) * t1
            ax.plot([xt0, xt1], [yt0, yt1], color='white', linewidth=6, alpha=0.9, solid_capstyle='round', zorder=6)
        # Draw gradient on top
        for t0, t1 in zip(np.linspace(0, 1, steps, endpoint=False), np.linspace(0, 1, steps, endpoint=False)[1:].tolist() + [1.0]):
            xt0 = x0 + (x1 - x0) * t0
            yt0 = y0 + (y1 - y0) * t0
            xt1 = x0 + (x1 - x0) * t1
            yt1 = y0 + (y1 - y0) * t1
            ct = c0 * (1 - t0) + c1 * t0
            ax.plot([xt0, xt1], [yt0, yt1], color=ct, linewidth=4, alpha=1.0, solid_capstyle='round', zorder=7)
        # Arrow head (double-draw for outline)
        outline = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='->',
                                  mutation_scale=16, linewidth=5, color='white',
                                  shrinkA=0, shrinkB=0, zorder=8)
        outline.set_clip_on(False)
        ax.add_patch(outline)
        head = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='->',
                               mutation_scale=16, linewidth=2.5, color=color_end,
                               shrinkA=0, shrinkB=0, zorder=9)
        head.set_clip_on(False)
        ax.add_patch(head)
        # Label at midpoint with colored border
        xm = (x0 + x1) / 2.0
        ym = (y0 + y1) / 2.0
        ax.text(xm, ym + 1.2, label, ha='center', va='bottom', fontsize=9, color=color_end,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor=color_end, alpha=0.95), zorder=8)

    ylim_top = ax1.get_ylim()[1]

    # 1) High-resolution training: top of 1MP -> top of 4MP
    x0 = bars[0].get_x() + bars[0].get_width() / 2.0
    x1 = bars[1].get_x() + bars[1].get_width() / 2.0
    y0 = ys[0]
    y1 = ys[1]
    delta_hr = y1 - y0
    draw_gradient_arrow(ax1, x0, y0, x1, y1, '#00B8D9', '#0052CC', f'High-resolution training +{delta_hr:.2f}pp')

    # 2) Model filtering to improve web data quality: top of Better prompt -> top of Model filtering
    x0 = bars[2].get_x() + bars[2].get_width() / 2.0
    x1 = bars[3].get_x() + bars[3].get_width() / 2.0
    y0 = ys[2]
    y1 = ys[3]
    delta_filt = y1 - y0
    draw_gradient_arrow(ax1, x0, y0, x1, y1, '#FFA000', '#FF6F00', f'Model filtering to improve web data quality +{delta_filt:.2f}pp')

    # 3) Scaling: top of Model filtering -> top of 114K
    x0 = bars[3].get_x() + bars[3].get_width() / 2.0
    x1 = bars[7].get_x() + bars[7].get_width() / 2.0
    y0 = ys[3]
    y1 = ys[7]
    delta_scale = y1 - y0
    draw_gradient_arrow(ax1, x0, y0, x1, y1, '#2ECC71', '#1E8449', f'Scale data (to 114K) +{delta_scale:.2f}pp')

    # Add SFT-only note
    ax1.text(0.01, 0.02, 'Note: SFT-only (no RL) improvements shown', transform=ax1.transAxes,
             fontsize=8, color='gray', ha='left', va='bottom',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='lightgray', alpha=0.8))

    # RL note merged into future bar label

    fig.tight_layout()
    return fig


def save_plot():
    fig = create_summary_figure()
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / 'sspro_progress_summary.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Plot saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    save_plot()



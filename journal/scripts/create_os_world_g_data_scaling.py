#!/usr/bin/env python3
"""
Create a bar plot showing the impact of data scaling on OS-World-G (refined) performance.
Shows 7B performance scaling with data size, including benchmark reference lines.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Model naming (our models labeled as SFT)
OUR_MODEL_LABEL = 'SFT-7B'

# Data for the comparison (including all benchmark models)
models_data = {
    # Benchmark models
    'GTA1-7B': 67.7,
    'GTA1-32B': 61.9,
    'UI-Venus-7B': 58.8,
    'OpenCUA-7B': 55.3,
}

# Data scaling results (ours)
os_10k = 51.0  # 10k samples
os_20k = 57.2  # 20k samples
os_35k = 56.2  # 35k samples
os_80k = 57.6  # 80k samples
os_114k = 59.5  # 114k samples (measured)
os_114k_interp = 60.1  # 114k samples (interpolated)


def create_data_scaling_plot():
    """Create a bar plot showing data scaling impact on performance."""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Build explicit ordering:
    # UI-Venus-7B (left) -> SFT group (10k..114k interp) -> OpenCUA-7B -> GTA1-32B -> GTA1-7B (right)
    ui_venus = 'UI-Venus-7B'
    open_cua = 'OpenCUA-7B'
    gta32 = 'GTA1-32B'
    gta7 = 'GTA1-7B'

    sft_models = [
        f'{OUR_MODEL_LABEL}\n10k samples',
        f'{OUR_MODEL_LABEL}\n20k samples',
        f'{OUR_MODEL_LABEL}\n35k samples',
        f'{OUR_MODEL_LABEL}\n80k samples',
        f'{OUR_MODEL_LABEL}\n114k samples',
        f'{OUR_MODEL_LABEL}\n114k samples (interpolated)',
    ]
    name_to_value = {
        ui_venus: models_data[ui_venus],
        open_cua: models_data[open_cua],
        gta32: models_data[gta32],
        gta7: models_data[gta7],
        sft_models[0]: os_10k,
        sft_models[1]: os_20k,
        sft_models[2]: os_35k,
        sft_models[3]: os_80k,
        sft_models[4]: os_114k,
        sft_models[5]: os_114k_interp,
    }

    ordered_names = sft_models + [open_cua, ui_venus]  + [gta32, gta7]
    all_models = ordered_names
    all_accuracies = [name_to_value[name] for name in ordered_names]

    # Colors - benchmark models in blue, our models in red gradient (improving)
    colors = []
    for model in all_models:
        if OUR_MODEL_LABEL in model:
            if '114k samples (interpolated)' in model:
                colors.append('#4B0000')  # Darkest red
            elif '114k' in model:
                colors.append('#8B0000')  # Very dark red
            elif '80k' in model:
                colors.append('#A40000')  # Dark red
            elif '35k' in model:
                colors.append('#CD5C5C')  # Medium red
            elif '20k' in model:
                colors.append('#E57373')  # Lighter red
            elif '10k' in model:
                colors.append('#F24236')  # Lightest red (baseline)
            else:
                colors.append('#F24236')
        else:
            colors.append('#2E86AB')  # Blue for benchmarks

    # Create bar plot
    bars = ax.bar(range(len(all_models)), all_accuracies, color=colors, alpha=0.8)

    # Highlight our model bars with different edge styles
    for i, model in enumerate(all_models):
        if OUR_MODEL_LABEL in model:
            bars[i].set_alpha(1.0)
            if '114k samples (interpolated)' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(4)
                bars[i].set_linestyle('-')
            elif '114k' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(4)
                bars[i].set_linestyle('-')
            elif '80k' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(4)
                bars[i].set_linestyle('-')
            elif '35k' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(3)
                bars[i].set_linestyle('-')
            elif '20k' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(2)
                bars[i].set_linestyle('--')
            else:  # 10k baseline
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(2)
                bars[i].set_linestyle(':')

    # Add value labels on top of bars
    for i, (bar, acc) in enumerate(zip(bars, all_accuracies)):
        height = bar.get_height()
        fontweight = 'bold' if OUR_MODEL_LABEL in all_models[i] else 'normal'
        color = 'darkred' if OUR_MODEL_LABEL in all_models[i] else 'black'
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.5,
            f'{acc:.1f}%',
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight=fontweight,
            color=color,
        )

    # Add improvement annotations between our model stages
    our_indices = [i for i, model in enumerate(all_models) if OUR_MODEL_LABEL in model]

    # Annotations for successive SFT improvements (10k->20k->35k->80k->114k->114k interp)
    sft_values = [os_10k, os_20k, os_35k, os_80k, os_114k, os_114k_interp]
    if len(our_indices) == len(sft_values):
        for a_idx, b_idx, a_val, b_val in zip(
            our_indices[:-1], our_indices[1:], sft_values[:-1], sft_values[1:]
        ):
            improvement = b_val - a_val
            mid_x = (a_idx + b_idx) / 2
            mid_y = (a_val + b_val) / 2
            ax.annotate(
                f'{improvement:+.1f}pp',
                xy=(mid_x, mid_y),
                ha='center',
                va='center',
                fontsize=7,
                color='darkred',
                fontweight='bold',
                bbox=dict(
                    boxstyle='round,pad=0.2', facecolor='white', edgecolor='darkred', alpha=0.8
                ),
            )

    # Customize the plot
    ax.set_ylabel('OS-World-G (refined) Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title(
        'Impact of Data Scaling\nOS-World-G (refined) Performance', fontsize=12, fontweight='bold', pad=15
    )

    # Set x-axis with model names (clean up labels)
    model_labels = []
    for model in all_models:
        if OUR_MODEL_LABEL in model:
            if '114k samples (interpolated)' in model:
                model_labels.append('SFT-7B\n(114k) (interpolated)')
            elif '114k' in model:
                model_labels.append('SFT-7B\n(114k)')
            elif '80k' in model:
                model_labels.append('SFT-7B\n(80k)')
            elif '35k' in model:
                model_labels.append('SFT-7B\n(35k)')
            elif '20k' in model:
                model_labels.append('SFT-7B\n(20k)')
            elif '10k' in model:
                model_labels.append('SFT-7B\n(10k)')
            else:
                model_labels.append('SFT-7B')
        else:
            model_labels.append(model.replace(' 7B', '').replace(' 32B', ''))

    ax.set_xticks(range(len(all_models)))
    ax.set_xticklabels(model_labels, rotation=45, ha='right', fontsize=8)

    # Set y-axis
    ax.set_ylim(50, 70)
    ax.grid(True, alpha=0.3, axis='y')

    # Add legend for our model stages
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor='#F24236', edgecolor='darkred', linestyle=':', linewidth=2, label='SFT-7B (10k)'),
        Patch(facecolor='#E57373', edgecolor='darkred', linestyle='--', linewidth=2, label='SFT-7B (20k)'),
        Patch(facecolor='#CD5C5C', edgecolor='darkred', linestyle='-', linewidth=3, label='SFT-7B (35k)'),
        Patch(facecolor='#A40000', edgecolor='darkred', linestyle='-', linewidth=4, label='SFT-7B (80k)'),
        Patch(facecolor='#8B0000', edgecolor='darkred', linestyle='-', linewidth=4, label='SFT-7B (114k)'),
        Patch(facecolor='#4B0000', edgecolor='darkred', linestyle='-', linewidth=4, label='SFT-7B (114k) (interpolated)'),
        Patch(facecolor='#2E86AB', label='Benchmark Models'),
    ]
    ax.legend(
        handles=legend_elements, loc='upper left', fontsize=8, frameon=True, fancybox=True, shadow=True
    )

    plt.tight_layout()
    return fig


def save_plot():
    """Save the plot to the data directory."""
    fig = create_data_scaling_plot()

    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)

    # Save as PNG only
    output_path_png = output_dir / 'os_world_g_data_scaling.png'

    fig.savefig(
        output_path_png, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none'
    )

    print(f"Plot saved to: {output_path_png}")

    plt.show()
    return output_path_png


if __name__ == "__main__":
    save_plot()



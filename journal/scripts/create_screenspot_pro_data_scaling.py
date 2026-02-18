#!/usr/bin/env python3
"""
Create a scatter plot showing the impact of data scaling on ScreenSpot Pro performance.
Shows SFT-7B performance scaling with data size, including benchmark reference lines.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Data for the comparison (including all benchmark models)
models_data = {
    # Benchmark models
    'GTA1-7B': 50.1,
    'SE-GUI-7B': 47.3,
    # 'UI-Venus-7B': 50.1,
    'Phi-Ground-7B': 43.2,
    'UI-TARS 1.5 7B': 42.0,
    'UI-TARS 7B': 35.7,
    # Our model baseline (10k data)
    'SFT-7B': 45.22
}

# Data scaling results
sft_10k = 45.22  # 10k samples (without replacement)
sft_20k = 46.55  # 20k samples (without replacement)
sft_35k = 47.18  # 35k samples (without replacement)
sft_80k = 49.65  # 80k samples (with replacement) + improved prompt + pro apps in-house data
sft_114k = 50.41  # 114k samples (with replacement) + improved prompt + pro apps in-house data

# Separate our model from benchmarks for different styling
benchmark_models = {k: v for k, v in models_data.items() if k != 'SFT-7B'}
our_model = {k: v for k, v in models_data.items() if k == 'SFT-7B'}

def create_data_scaling_plot():
    """Create a bar plot showing data scaling impact on performance (filtering style)."""
    fig, ax = plt.subplots(figsize=(8, 6))  # Wider to accommodate additional bars including 80k
    
    # Prepare data and sort by accuracy (lowest to highest)
    all_models_dict = {**benchmark_models, **our_model}
    sorted_items = sorted(all_models_dict.items(), key=lambda x: x[1])
    all_models = [item[0] for item in sorted_items]
    all_accuracies = [item[1] for item in sorted_items]
    
    # Find our model position and insert scaling stages
    our_model_idx = all_models.index('SFT-7B')
    
    # Insert the scaling stages after our baseline model
    all_models.insert(our_model_idx + 1, 'SFT-7B\n20k samples')
    all_models.insert(our_model_idx + 2, 'SFT-7B\n35k samples')
    all_models.insert(our_model_idx + 3, 'SFT-7B\n80k samples')
    all_models.insert(our_model_idx + 4, 'SFT-7B\n114k samples (interpolated)')
    all_accuracies.insert(our_model_idx + 1, sft_20k)
    all_accuracies.insert(our_model_idx + 2, sft_35k)
    all_accuracies.insert(our_model_idx + 3, sft_80k)
    all_accuracies.insert(our_model_idx + 4, sft_114k)
    
    # Create colors - benchmark models in blue, our models in red gradient (improving)
    colors = []
    for model in all_models:
        if 'SFT-7B' in model:
            if '114k samples (interpolated)' in model:
                colors.append('#4B0000')  # Darkest red for highest scaling
            elif '80k samples' in model:
                colors.append('#8B0000')  # Dark red for best scaling
            elif '35k samples' in model:
                colors.append('#CD5C5C')  # Medium red for high scaling
            elif '20k samples' in model:
                colors.append('#CD5C5C')  # Medium red for intermediate scaling
            else:
                colors.append('#F24236')  # Light red for baseline
        else:
            colors.append('#2E86AB')  # Blue for benchmarks
    
    # Create bar plot
    bars = ax.bar(range(len(all_models)), all_accuracies, color=colors, alpha=0.8)
    
    # Highlight our model bars with different edge styles
    for i, model in enumerate(all_models):
        if 'SFT-7B' in model:
            bars[i].set_alpha(1.0)
            if '114k samples (interpolated)' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(4)
                bars[i].set_linestyle('-')
            elif '80k samples' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(4)
                bars[i].set_linestyle('-')
            elif '35k samples' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(3)
                bars[i].set_linestyle('-')
            elif '20k samples' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(2)
                bars[i].set_linestyle('--')
            else:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(2)
                bars[i].set_linestyle(':')
    
    # Add value labels on top of bars
    for i, (bar, acc) in enumerate(zip(bars, all_accuracies)):
        height = bar.get_height()
        fontweight = 'bold' if 'SFT-7B' in all_models[i] else 'normal'
        color = 'darkred' if 'SFT-7B' in all_models[i] else 'black'
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{acc:.1f}%', ha='center', va='bottom', 
                fontsize=8, fontweight=fontweight, color=color)
    
    # Add improvement annotations between our model stages
    sft_indices = [i for i, model in enumerate(all_models) if 'SFT-7B' in model]
    
    # Annotation for 10k -> 20k improvement
    if len(sft_indices) >= 2:
        baseline_idx, k20_idx = sft_indices[0], sft_indices[1]
        improvement1 = sft_20k - sft_10k
        mid_x = (baseline_idx + k20_idx) / 2
        mid_y = (sft_10k + sft_20k) / 2
        ax.annotate(f'+{improvement1:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Annotation for 20k -> 35k improvement
    if len(sft_indices) >= 3:
        k20_idx, k35_idx = sft_indices[1], sft_indices[2]
        improvement2 = sft_35k - sft_20k
        mid_x = (k20_idx + k35_idx) / 2
        mid_y = (sft_20k + sft_35k) / 2
        ax.annotate(f'+{improvement2:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Annotation for 35k -> 80k improvement
    if len(sft_indices) >= 4:
        k35_idx, k80_idx = sft_indices[2], sft_indices[3]
        improvement3 = sft_80k - sft_35k
        mid_x = (k35_idx + k80_idx) / 2
        mid_y = (sft_35k + sft_80k) / 2
        ax.annotate(f'+{improvement3:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Customize the plot
    ax.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title('Impact of Data Scaling\nScreenSpot Pro Performance', 
                fontsize=12, fontweight='bold', pad=15)
    
    # Set x-axis with model names (clean up labels)
    model_labels = []
    for model in all_models:
        if 'SFT-7B' in model:
            if '114k samples (interpolated)' in model:
                model_labels.append('SFT-7B\n(114k) (interpolated)')
            elif '80k samples' in model:
                model_labels.append('SFT-7B\n(80k)')
            elif '35k samples' in model:
                model_labels.append('SFT-7B\n(35k)')
            elif '20k samples' in model:
                model_labels.append('SFT-7B\n(20k)')
            else:
                model_labels.append('SFT-7B\n(10k)')
        else:
            model_labels.append(model.replace(' 7B', ''))
    
    ax.set_xticks(range(len(all_models)))
    ax.set_xticklabels(model_labels, rotation=45, ha='right', fontsize=8)
    
    # Set y-axis
    ax.set_ylim(30, 55)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add legend for our model stages
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#F24236', edgecolor='darkred', linestyle=':', linewidth=2, label='SFT-7B (10k)'),
        Patch(facecolor='#CD5C5C', edgecolor='darkred', linestyle='--', linewidth=2, label='SFT-7B (20k)'),
        Patch(facecolor='#8B0000', edgecolor='darkred', linestyle='-', linewidth=3, label='SFT-7B (35k)'),
        Patch(facecolor='#4B0000', edgecolor='darkred', linestyle='-', linewidth=4, label='SFT-7B (80k)'),
        Patch(facecolor='#8B0000', edgecolor='darkred', linestyle='-', linewidth=3, label='SFT-7B (114k) (interpolated)'),
        Patch(facecolor='#2E86AB', label='Benchmark Models')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8, frameon=True, 
              fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_plot():
    """Save the plot to the data directory."""
    fig = create_data_scaling_plot()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save as PNG only
    output_path_png = output_dir / 'screenspot_pro_data_scaling.png'
    
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Plot saved to: {output_path_png}")
    
    plt.show()
    return output_path_png

if __name__ == "__main__":
    save_plot()

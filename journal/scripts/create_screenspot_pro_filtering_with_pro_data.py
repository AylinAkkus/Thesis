#!/usr/bin/env python3
"""
Create a bar plot showing the impact of model difficulty filtering on ScreenSpot Pro performance.
Shows SFT-7B with progressive improvements from baseline -> easy filtering -> easy+hard filtering.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Data for the comparison
models_data = {
    # Benchmark models
    'GTA1-7B': 50.1,
    'SE-GUI-7B': 47.3,
    'UI-Venus-7B': 50.1,
    'Phi-Ground-7B': 43.2,
    'UI-TARS 1.5 7B': 42.0,
    'UI-TARS 7B': 35.7,
    # Our model baseline
    'SFT-7B': 36.12
}

# Model difficulty filtering progression data
sft_baseline = 36.12  # No Filtering
sft_easy_filtering = 39.78  # Easy filtering only
sft_easy_hard_filtering = 45.22  # Easy + Hard filtering
sft_with_pro_app_data = 46.11  # Easy + Hard filtering + In-house pro app data

# Separate our model from benchmarks for different styling
benchmark_models = {k: v for k, v in models_data.items() if k != 'SFT-7B'}
our_model = {k: v for k, v in models_data.items() if k == 'SFT-7B'}

def create_bar_plot_with_filtering():
    """Create a compact square bar plot with model difficulty filtering stages."""
    fig, ax = plt.subplots(figsize=(7, 6))  # Slightly wider to accommodate additional bars
    
    # Prepare data and sort by accuracy (lowest to highest)
    all_models_dict = {**benchmark_models, **our_model}
    sorted_items = sorted(all_models_dict.items(), key=lambda x: x[1])
    all_models = [item[0] for item in sorted_items]
    all_accuracies = [item[1] for item in sorted_items]
    
    # Find our model position and insert filtering stages
    our_model_idx = all_models.index('SFT-7B')
    
    # Insert the filtering stages after our baseline model
    all_models.insert(our_model_idx + 1, 'SFT-7B\n+ Easy Filter')
    all_models.insert(our_model_idx + 2, 'SFT-7B\n+ Easy+Hard Filter')
    all_models.insert(our_model_idx + 3, 'SFT-7B\n+ Pro App Data')
    all_accuracies.insert(our_model_idx + 1, sft_easy_filtering)
    all_accuracies.insert(our_model_idx + 2, sft_easy_hard_filtering)
    all_accuracies.insert(our_model_idx + 3, sft_with_pro_app_data)
    
    # Create colors - benchmark models in blue, our models in red gradient
    colors = []
    for model in all_models:
        if 'SFT-7B' in model:
            if '+ Pro App Data' in model:
                colors.append('#4B0000')  # Darkest red for final stage
            elif '+ Easy+Hard Filter' in model:
                colors.append('#8B0000')  # Dark red for filtering
            elif '+ Easy Filter' in model:
                colors.append('#CD5C5C')  # Medium red for easy filtering
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
            if '+ Pro App Data' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(4)
                bars[i].set_linestyle('-')
            elif '+ Easy+Hard Filter' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(3)
                bars[i].set_linestyle('-')
            elif '+ Easy Filter' in model:
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
    
    # Annotation for easy filtering improvement
    if len(sft_indices) >= 2:
        baseline_idx, easy_idx = sft_indices[0], sft_indices[1]
        improvement1 = sft_easy_filtering - sft_baseline
        mid_x = (baseline_idx + easy_idx) / 2
        mid_y = (sft_baseline + sft_easy_filtering) / 2
        ax.annotate(f'+{improvement1:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Annotation for easy+hard filtering improvement
    if len(sft_indices) >= 3:
        easy_idx, hard_idx = sft_indices[1], sft_indices[2]
        improvement2 = sft_easy_hard_filtering - sft_easy_filtering
        mid_x = (easy_idx + hard_idx) / 2
        mid_y = (sft_easy_filtering + sft_easy_hard_filtering) / 2
        ax.annotate(f'+{improvement2:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Annotation for pro app data improvement
    if len(sft_indices) >= 4:
        hard_idx, pro_idx = sft_indices[2], sft_indices[3]
        improvement3 = sft_with_pro_app_data - sft_easy_hard_filtering
        mid_x = (hard_idx + pro_idx) / 2
        mid_y = (sft_easy_hard_filtering + sft_with_pro_app_data) / 2
        ax.annotate(f'+{improvement3:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Customize the plot
    ax.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title('Impact of Filtering + Pro App Data\nScreenSpot Pro Performance', 
                fontsize=12, fontweight='bold', pad=15)
    
    # Set x-axis with model names (clean up labels)
    model_labels = []
    for model in all_models:
        if 'SFT-7B' in model:
            if '+ Pro App Data' in model:
                model_labels.append('SFT-7B\n(+Pro Data)')
            elif '+ Easy+Hard Filter' in model:
                model_labels.append('SFT-7B\n(Easy+Hard)')
            elif '+ Easy Filter' in model:
                model_labels.append('SFT-7B\n(Easy)')
            else:
                model_labels.append('SFT-7B\n(Baseline)')
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
        Patch(facecolor='#F24236', edgecolor='darkred', linestyle=':', linewidth=2, label='SFT-7B Baseline'),
        Patch(facecolor='#CD5C5C', edgecolor='darkred', linestyle='--', linewidth=2, label='+ Easy Filtering'),
        Patch(facecolor='#8B0000', edgecolor='darkred', linestyle='-', linewidth=3, label='+ Easy+Hard Filtering'),
        Patch(facecolor='#4B0000', edgecolor='darkred', linestyle='-', linewidth=4, label='+ Pro App Data'),
        Patch(facecolor='#2E86AB', label='Benchmark Models')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8, frameon=True, 
              fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_plot():
    """Save the plot to the data directory."""
    fig = create_bar_plot_with_filtering()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save as PNG only
    output_path_png = output_dir / 'screenspot_pro_filtering_with_pro_data.png'
    
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Plot saved to: {output_path_png}")
    
    plt.show()
    return output_path_png

if __name__ == "__main__":
    save_plot()

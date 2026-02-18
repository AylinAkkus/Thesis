#!/usr/bin/env python3
"""
Create a bar plot showing alternative model difficulty filtering approaches on ScreenSpot Pro performance.
Shows SFT-7B with different filtering strategies, including less performant alternatives.
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

# Alternative filtering approaches data
filtering_approaches = {
    'SFT-7B\n(No Filtering)': 36.12,  # No Filtering
    'SFT-7B\n(Qwen + None)': 39.78,  # Easy filtering only with Qwen 2.5 VL 7B
    'SFT-7B\n(SE-GUI-3B + GTA1)': 41.62,  # SE-GUI-3B easy filtering + GTA1 7B hard filtering
    'SFT-7B\n(Qwen + GTA1|SE-GUI)': 42.06,  # Qwen 2.5 VL 7B + GTA1 7B OR SE-GUI-3B
    'SFT-7B\n(Qwen + GTA1|UI-Venus)': 44.46,  # Qwen 2.5 VL 7B + GTA1 7B OR UI-Venus-7B
    'SFT-7B\n(Qwen + GTA1)': 45.22,  # Best approach: Qwen 2.5 VL 7B + GTA1 7B
}

# Separate our model from benchmarks for different styling
benchmark_models = {k: v for k, v in models_data.items() if k != 'SFT-7B'}
our_model = {k: v for k, v in models_data.items() if k == 'SFT-7B'}

def create_bar_plot_filtering_alternatives():
    """Create a compact square bar plot with alternative model difficulty filtering approaches."""
    fig, ax = plt.subplots(figsize=(10, 6))  # Wider to accommodate more bars
    
    # Prepare data and sort by accuracy (lowest to highest)
    benchmark_items = sorted(benchmark_models.items(), key=lambda x: x[1])
    filtering_items = sorted(filtering_approaches.items(), key=lambda x: x[1])
    
    # Combine all data
    all_models = [item[0] for item in benchmark_items] + [item[0] for item in filtering_items]
    all_accuracies = [item[1] for item in benchmark_items] + [item[1] for item in filtering_items]
    
    # Create colors - benchmark models in blue, our models in red gradient
    colors = []
    for model in all_models:
        if 'SFT-7B' in model:
            if 'Qwen + GTA1)' in model and 'GTA1|' not in model:  # Best approach
                colors.append('#8B0000')  # Dark red for best approach
            elif 'GTA1|UI-Venus' in model:
                colors.append('#A52A2A')  # Medium-dark red
            elif 'GTA1|SE-GUI' in model:
                colors.append('#B22222')  # Fire brick
            elif 'SE-GUI-3B + GTA1' in model:
                colors.append('#DC143C')  # Crimson
            elif 'Qwen + None' in model:
                colors.append('#CD5C5C')  # Medium red for easy filtering only
            else:  # No Filtering
                colors.append('#F24236')  # Light red for baseline
        else:
            colors.append('#2E86AB')  # Blue for benchmarks
    
    # Create bar plot
    bars = ax.bar(range(len(all_models)), all_accuracies, color=colors, alpha=0.8)
    
    # Highlight our model bars with different edge styles
    for i, model in enumerate(all_models):
        if 'SFT-7B' in model:
            bars[i].set_alpha(1.0)
            bars[i].set_edgecolor('darkred')
            bars[i].set_linewidth(2)
            if 'Qwen + GTA1)' in model and 'GTA1|' not in model:  # Best approach
                bars[i].set_linestyle('-')
                bars[i].set_linewidth(3)
            elif 'GTA1|UI-Venus' in model:
                bars[i].set_linestyle('--')
            elif 'GTA1|SE-GUI' in model:
                bars[i].set_linestyle('-.')
            elif 'SE-GUI-3B + GTA1' in model:
                bars[i].set_linestyle((0, (3, 1, 1, 1)))  # Dash-dot-dot
            elif 'Qwen + None' in model:
                bars[i].set_linestyle(':')
            else:  # No Filtering
                bars[i].set_linestyle((0, (1, 1)))  # Dotted
    
    # Add value labels on top of bars
    for i, (bar, acc) in enumerate(zip(bars, all_accuracies)):
        height = bar.get_height()
        fontweight = 'bold' if 'SFT-7B' in all_models[i] else 'normal'
        color = 'darkred' if 'SFT-7B' in all_models[i] else 'black'
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{acc:.1f}%', ha='center', va='bottom', 
                fontsize=8, fontweight=fontweight, color=color)
    
    
    # Customize the plot
    ax.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title('Alternative Model Difficulty Filtering Approaches\nScreenSpot Pro Performance Comparison', 
                fontsize=12, fontweight='bold', pad=15)
    
    # Set x-axis with model names (clean up labels)
    model_labels = []
    for model in all_models:
        if 'SFT-7B' in model:
            # Use actual filtering names
            if 'Qwen + GTA1)' in model and 'GTA1|' not in model:
                model_labels.append('SFT-7B\n(Qwen + GTA1)')
            elif 'GTA1|UI-Venus' in model:
                model_labels.append('SFT-7B\n(Qwen + GTA1|UI-Venus)')
            elif 'GTA1|SE-GUI' in model:
                model_labels.append('SFT-7B\n(Qwen + GTA1|SE-GUI)')
            elif 'SE-GUI-3B + GTA1' in model:
                model_labels.append('SFT-7B\n(SE-GUI-3B + GTA1)')
            elif 'Qwen + None' in model:
                model_labels.append('SFT-7B\n(Qwen + None)')
            else:  # No Filtering
                model_labels.append('SFT-7B\n(No Filtering)')
        else:
            model_labels.append(model.replace(' 7B', ''))
    
    ax.set_xticks(range(len(all_models)))
    ax.set_xticklabels(model_labels, rotation=45, ha='right', fontsize=8)
    
    # Set y-axis
    ax.set_ylim(30, 55)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add legend for our model approaches
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#F24236', edgecolor='darkred', linestyle=(0, (1, 1)), linewidth=2, label='No Filtering'),
        Patch(facecolor='#CD5C5C', edgecolor='darkred', linestyle=':', linewidth=2, label='Qwen + None'),
        Patch(facecolor='#DC143C', edgecolor='darkred', linestyle=(0, (3, 1, 1, 1)), linewidth=2, label='SE-GUI-3B + GTA1'),
        Patch(facecolor='#B22222', edgecolor='darkred', linestyle='-.', linewidth=2, label='Qwen + GTA1|SE-GUI'),
        Patch(facecolor='#A52A2A', edgecolor='darkred', linestyle='--', linewidth=2, label='Qwen + GTA1|UI-Venus'),
        Patch(facecolor='#8B0000', edgecolor='darkred', linestyle='-', linewidth=3, label='Qwen + GTA1 (Best)'),
        Patch(facecolor='#2E86AB', label='Benchmark Models')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7, frameon=True, 
              fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_plot():
    """Save the plot to the data directory."""
    fig = create_bar_plot_filtering_alternatives()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save as PNG only
    output_path_png = output_dir / 'screenspot_pro_filtering_alternatives.png'
    
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Plot saved to: {output_path_png}")
    
    plt.show()
    return output_path_png

if __name__ == "__main__":
    save_plot()

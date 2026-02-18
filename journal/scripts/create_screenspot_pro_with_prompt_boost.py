#!/usr/bin/env python3
"""
Create a bar plot comparing ScreenSpot Pro performance with prompt improvement extension.
Shows SFT-7B model with dotted extension indicating better prompt performance.
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
    # Our model
    'SFT-7B': 36.12
}

# Prompt improvement data
sft_base_accuracy = 36.12  # Default Prompt + Image Resolution
sft_improved_accuracy = 39.03  # Default Prompt (better)

# Separate our model from benchmarks for different styling
benchmark_models = {k: v for k, v in models_data.items() if k != 'SFT-7B'}
our_model = {k: v for k, v in models_data.items() if k == 'SFT-7B'}

def create_bar_plot_with_prompt_boost():
    """Create a compact square bar plot with prompt improvement extension."""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Prepare data and sort by accuracy (lowest to highest)
    all_models_dict = {**benchmark_models, **our_model}
    sorted_items = sorted(all_models_dict.items(), key=lambda x: x[1])
    all_models = [item[0] for item in sorted_items]
    all_accuracies = [item[1] for item in sorted_items]
    
    # Create colors - benchmark models in blue, our model in red
    colors = ['#F24236' if model == 'SFT-7B' else '#2E86AB' for model in all_models]
    
    # Create bar plot
    bars = ax.bar(range(len(all_models)), all_accuracies, color=colors, alpha=0.8)
    
    # Highlight our model bar
    our_model_idx = all_models.index('SFT-7B')
    bars[our_model_idx].set_alpha(1.0)
    bars[our_model_idx].set_edgecolor('darkred')
    bars[our_model_idx].set_linewidth(2)
    
    # Add dotted extension for prompt improvement
    bar_width = bars[our_model_idx].get_width()
    bar_x = bars[our_model_idx].get_x()
    improvement_height = sft_improved_accuracy - sft_base_accuracy
    
    # Create dotted extension bar
    extension_bar = ax.bar(our_model_idx, improvement_height, 
                          bottom=sft_base_accuracy, width=bar_width,
                          color='#F24236', alpha=0.6, 
                          linestyle='--', edgecolor='darkred', 
                          linewidth=2, hatch='...')
    
    # Add value labels on top of bars
    for i, (bar, acc) in enumerate(zip(bars, all_accuracies)):
        height = bar.get_height()
        if all_models[i] == 'SFT-7B':
            # For our model, show both values
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{acc:.1f}%', ha='center', va='bottom', 
                    fontsize=8, fontweight='bold', color='darkred')
            # Add improved accuracy label
            ax.text(bar.get_x() + bar.get_width()/2., sft_improved_accuracy + 0.5,
                    f'{sft_improved_accuracy:.1f}%', ha='center', va='bottom', 
                    fontsize=8, fontweight='bold', color='darkred')
            # Add improvement arrow and text
            ax.annotate('', xy=(bar.get_x() + bar.get_width()/2., sft_improved_accuracy - 0.3), 
                       xytext=(bar.get_x() + bar.get_width()/2., height + 0.3),
                       arrowprops=dict(arrowstyle='<->', color='darkred', lw=1.5))
            ax.text(bar.get_x() + bar.get_width() + 0.1, (height + sft_improved_accuracy)/2,
                    f'+{improvement_height:.1f}pp\n(better prompt)', 
                    ha='left', va='center', fontsize=7, color='darkred',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor='darkred', alpha=0.8))
        else:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{acc:.1f}%', ha='center', va='bottom', 
                    fontsize=8)
    
    # Customize the plot
    ax.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title('4MP Training + Better Prompt\nScreenSpot Pro Performance', 
                fontsize=12, fontweight='bold', pad=15)
    
    # Set x-axis with model names (clean up labels)
    model_labels = [model.replace(' 7B', '') for model in all_models]
    ax.set_xticks(range(len(all_models)))
    ax.set_xticklabels(model_labels, rotation=45, ha='right', fontsize=9)
    
    # Set y-axis
    ax.set_ylim(30, 55)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig

def save_plot():
    """Save the plot to the data directory."""
    fig = create_bar_plot_with_prompt_boost()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save as PNG only
    output_path_png = output_dir / 'screenspot_pro_4mp_with_prompt_boost.png'
    
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Plot saved to: {output_path_png}")
    
    plt.show()
    return output_path_png

if __name__ == "__main__":
    save_plot()

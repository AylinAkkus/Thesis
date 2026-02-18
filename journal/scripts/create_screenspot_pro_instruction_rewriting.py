#!/usr/bin/env python3
"""
Create a bar plot showing the negative impact of instruction rewriting on ScreenSpot Pro performance.
Shows how different rewriting strategies degrade performance compared to no rewriting baseline.
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
    'UI-Venus-7B': 50.1,
    'Phi-Ground-7B': 43.2,
    'UI-TARS 1.5 7B': 42.0,
    'UI-TARS 7B': 35.7,
    # Our model baseline (no rewriting)
    'SFT-7B': 45.22
}

# Instruction rewriting results data
sft_baseline = 45.22  # No Rewriting
sft_llm_rewriting = 42.25  # LLM Rewriting (Qwen3 4B)
sft_image_aware = 39.27  # Image-Aware Synthetic (Qwen 2.5 VL 7B)

# Separate our model from benchmarks for different styling
benchmark_models = {k: v for k, v in models_data.items() if k != 'SFT-7B'}
our_model = {k: v for k, v in models_data.items() if k == 'SFT-7B'}

def create_instruction_rewriting_plot():
    """Create a bar plot showing negative impact of instruction rewriting (filtering style)."""
    fig, ax = plt.subplots(figsize=(7, 6))  # Slightly wider to accommodate additional bars
    
    # Prepare data and sort by accuracy (lowest to highest)
    all_models_dict = {**benchmark_models, **our_model}
    sorted_items = sorted(all_models_dict.items(), key=lambda x: x[1])
    all_models = [item[0] for item in sorted_items]
    all_accuracies = [item[1] for item in sorted_items]
    
    # Find our model position and insert rewriting stages
    our_model_idx = all_models.index('SFT-7B')
    
    # Insert the rewriting stages after our baseline model
    all_models.insert(our_model_idx + 1, 'SFT-7B\n+ LLM Rewriting')
    all_models.insert(our_model_idx + 2, 'SFT-7B\n+ Image-Aware')
    all_accuracies.insert(our_model_idx + 1, sft_llm_rewriting)
    all_accuracies.insert(our_model_idx + 2, sft_image_aware)
    
    # Create colors - benchmark models in blue, our models in red gradient (degrading)
    colors = []
    for model in all_models:
        if 'SFT-7B' in model:
            if '+ Image-Aware' in model:
                colors.append('#8B4513')  # Dark brown for worst performance
            elif '+ LLM Rewriting' in model:
                colors.append('#CD853F')  # Medium brown for degraded performance
            else:
                colors.append('#F24236')  # Red for baseline
        else:
            colors.append('#2E86AB')  # Blue for benchmarks
    
    # Create bar plot
    bars = ax.bar(range(len(all_models)), all_accuracies, color=colors, alpha=0.8)
    
    # Highlight our model bars with different edge styles
    for i, model in enumerate(all_models):
        if 'SFT-7B' in model:
            bars[i].set_alpha(1.0)
            if '+ Image-Aware' in model:
                bars[i].set_edgecolor('darkred')
                bars[i].set_linewidth(3)
                bars[i].set_linestyle('-')
            elif '+ LLM Rewriting' in model:
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
    
    # Add degradation annotations between our model stages
    sft_indices = [i for i, model in enumerate(all_models) if 'SFT-7B' in model]
    
    # Annotation for LLM rewriting degradation
    if len(sft_indices) >= 2:
        baseline_idx, llm_idx = sft_indices[0], sft_indices[1]
        degradation1 = sft_llm_rewriting - sft_baseline
        mid_x = (baseline_idx + llm_idx) / 2
        mid_y = (sft_baseline + sft_llm_rewriting) / 2
        ax.annotate(f'{degradation1:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Annotation for image-aware degradation
    if len(sft_indices) >= 3:
        llm_idx, img_idx = sft_indices[1], sft_indices[2]
        degradation2 = sft_image_aware - sft_llm_rewriting
        mid_x = (llm_idx + img_idx) / 2
        mid_y = (sft_llm_rewriting + sft_image_aware) / 2
        ax.annotate(f'{degradation2:.1f}pp', 
                   xy=(mid_x, mid_y), ha='center', va='center',
                   fontsize=7, color='darkred', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='darkred', alpha=0.8))
    
    # Customize the plot
    ax.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=11, fontweight='bold')
    ax.set_title('Impact of Instruction Rewriting\nScreenSpot Pro Performance', 
                fontsize=12, fontweight='bold', pad=15)
    
    # Set x-axis with model names (clean up labels)
    model_labels = []
    for model in all_models:
        if 'SFT-7B' in model:
            if '+ Image-Aware' in model:
                model_labels.append('SFT-7B\n(Img-Aware)')
            elif '+ LLM Rewriting' in model:
                model_labels.append('SFT-7B\n(LLM Rewrite)')
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
        Patch(facecolor='#CD853F', edgecolor='darkred', linestyle='--', linewidth=2, label='+ LLM Rewriting'),
        Patch(facecolor='#8B4513', edgecolor='darkred', linestyle='-', linewidth=3, label='+ Image-Aware'),
        Patch(facecolor='#2E86AB', label='Benchmark Models')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8, frameon=True, 
              fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def save_plot():
    """Save the plot to the data directory."""
    fig = create_instruction_rewriting_plot()
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save as PNG only
    output_path_png = output_dir / 'screenspot_pro_instruction_rewriting_negative.png'
    
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Plot saved to: {output_path_png}")
    
    plt.show()
    return output_path_png

if __name__ == "__main__":
    save_plot()

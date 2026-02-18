#!/usr/bin/env python3
"""
Create a visualization showing the impact of evaluation fix on sft_80k performance.
Shows before and after comparison: 49.0 -> 49.65 on ScreenSpot Pro.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Data for the evaluation fix comparison
sft_80k_before_fix = 49.0  # Before evaluation fix
sft_80k_after_fix = 49.65  # After evaluation fix
improvement = sft_80k_after_fix - sft_80k_before_fix

# Benchmark models from the original data scaling script
benchmark_models = {
    'GTA1-7B': 50.1,
    'SE-GUI-7B': 47.3,
    'Phi-Ground-7B': 43.2,
    'UI-TARS 1.5 7B': 42.0,
    'UI-TARS 7B': 35.7,
    'SFT-7B (10k)': 45.22,
    'SFT-7B (20k)': 46.55,
    'SFT-7B (35k)': 47.18,
}

def create_eval_fix_plot():
    """Create a bar plot showing the evaluation fix impact in context of all models."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Combine all models including the eval fix comparison
    all_models = dict(benchmark_models)
    all_models['SFT-80k (Before Fix)'] = sft_80k_before_fix
    all_models['SFT-80k (After Fix)'] = sft_80k_after_fix
    
    # Sort models by performance (lowest to highest)
    sorted_items = sorted(all_models.items(), key=lambda x: x[1])
    model_names = [item[0] for item in sorted_items]
    model_values = [item[1] for item in sorted_items]
    
    # Create colors
    colors = []
    for name in model_names:
        if 'SFT-80k (Before Fix)' in name:
            colors.append('#FF6B6B')  # Light red for before fix
        elif 'SFT-80k (After Fix)' in name:
            colors.append('#2E8B57')  # Dark green for after fix (improvement)
        elif 'SFT-7B' in name:
            colors.append('#4B0000')  # Dark red for our other models
        else:
            colors.append('#2E86AB')  # Blue for benchmark models
    
    # Create bar plot
    bars = ax.bar(range(len(model_names)), model_values, color=colors, alpha=0.8)
    
    # Enhance bars styling
    for i, (bar, name) in enumerate(zip(bars, model_names)):
        if 'SFT-80k' in name:
            bar.set_edgecolor('black')
            bar.set_linewidth(3)
            bar.set_alpha(1.0)
            if 'After Fix' in name:
                bar.set_edgecolor('darkgreen')
                bar.set_linewidth(4)
        elif 'SFT-7B' in name:
            bar.set_edgecolor('darkred')
            bar.set_linewidth(2)
    
    # Add value labels on top of bars
    for i, (bar, value, name) in enumerate(zip(bars, model_values, model_names)):
        height = bar.get_height()
        fontweight = 'bold' if 'SFT' in name else 'normal'
        color = 'darkgreen' if 'After Fix' in name else ('darkred' if 'SFT' in name else 'black')
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{value:.1f}%', ha='center', va='bottom', 
                fontsize=9, fontweight=fontweight, color=color)
    
    # Add improvement annotation between before/after fix
    before_idx = model_names.index('SFT-80k (Before Fix)')
    after_idx = model_names.index('SFT-80k (After Fix)')
    
    # Draw arrow showing improvement
    arrow_props = dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', 
                      color='darkgreen', lw=3)
    ax.annotate('', xy=(after_idx, sft_80k_after_fix - 0.2), 
                xytext=(before_idx, sft_80k_before_fix + 0.2),
                arrowprops=arrow_props)
    
    # Add improvement text
    mid_x = (before_idx + after_idx) / 2
    mid_y = (sft_80k_before_fix + sft_80k_after_fix) / 2 + 0.8
    ax.text(mid_x, mid_y, f'+{improvement:.2f}pp\nEval Fix', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            color='darkgreen',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', 
                     edgecolor='darkgreen', alpha=0.9))
    
    # Customize the plot
    ax.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('SFT-80k Evaluation Fix Impact\nScreenSpot Pro Performance vs All Models', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Clean up model labels for x-axis
    clean_labels = []
    for name in model_names:
        if 'SFT-80k (Before Fix)' in name:
            clean_labels.append('SFT-80k\n(Before Fix)')
        elif 'SFT-80k (After Fix)' in name:
            clean_labels.append('SFT-80k\n(After Fix)')
        elif '7B' in name:
            clean_labels.append(name.replace(' 7B', '').replace('SFT-7B ', 'SFT-7B\n'))
        else:
            clean_labels.append(name)
    
    # Set x-axis
    ax.set_xticks(range(len(model_names)))
    ax.set_xticklabels(clean_labels, rotation=45, ha='right', fontsize=9)
    
    # Set y-axis
    ax.set_ylim(30, 55)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', label='Benchmark Models'),
        Patch(facecolor='#4B0000', edgecolor='darkred', linewidth=2, label='Our SFT Models'),
        Patch(facecolor='#FF6B6B', edgecolor='black', linewidth=3, label='SFT-80k (Before Fix)'),
        Patch(facecolor='#2E8B57', edgecolor='darkgreen', linewidth=4, label='SFT-80k (After Fix)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, frameon=True, 
              fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig

def create_side_by_side_comparison():
    """Create an alternative visualization with side-by-side metrics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Left plot - Before
    ax1.bar(['SFT-80k'], [sft_80k_before_fix], color='#CD5C5C', alpha=0.8, 
            edgecolor='darkred', linewidth=2)
    ax1.set_title('Before Eval Fix', fontsize=14, fontweight='bold', color='darkred')
    ax1.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_ylim(48.5, 50.2)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.text(0, sft_80k_before_fix + 0.05, f'{sft_80k_before_fix:.2f}%', 
             ha='center', va='bottom', fontsize=16, fontweight='bold', color='darkred')
    
    # Right plot - After
    ax2.bar(['SFT-80k'], [sft_80k_after_fix], color='#4B0000', alpha=1.0, 
            edgecolor='darkred', linewidth=4)
    ax2.set_title('After Eval Fix', fontsize=14, fontweight='bold', color='darkgreen')
    ax2.set_ylabel('ScreenSpot Pro Accuracy (%)', fontsize=12, fontweight='bold')
    ax2.set_ylim(48.5, 50.2)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.text(0, sft_80k_after_fix + 0.05, f'{sft_80k_after_fix:.2f}%', 
             ha='center', va='bottom', fontsize=16, fontweight='bold', color='darkgreen')
    
    # Add improvement badge between plots
    fig.text(0.5, 0.85, f'+{improvement:.2f}pp Improvement', 
             ha='center', va='center', fontsize=16, fontweight='bold',
             color='darkgreen',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', 
                      edgecolor='darkgreen', alpha=0.9))
    
    # Overall title
    fig.suptitle('SFT-80k Evaluation Fix Impact Analysis\nScreenSpot Pro Performance', 
                fontsize=18, fontweight='bold', y=0.95)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.75)
    return fig

def save_plots():
    """Save both visualization styles to the data directory."""
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save the main plot (comprehensive view with all models)
    fig1 = create_eval_fix_plot()
    output_path1 = output_dir / 'sft_80k_eval_fix_comprehensive.png'
    fig1.savefig(output_path1, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Comprehensive plot saved to: {output_path1}")
    
    # Save the side-by-side comparison
    fig2 = create_side_by_side_comparison()
    output_path2 = output_dir / 'sft_80k_eval_fix_comparison.png'
    fig2.savefig(output_path2, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Comparison plot saved to: {output_path2}")
    
    plt.show()
    return output_path1, output_path2

if __name__ == "__main__":
    save_plots()

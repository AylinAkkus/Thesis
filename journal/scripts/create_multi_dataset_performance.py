#!/usr/bin/env python3
"""
Create a multi-dataset performance comparison plot.
Shows performance across ScreenSpot Pro, ScreenSpot V2, and Showdown Clicks.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Multi-dataset performance data
performance_data = {
    'models': [
        'UI-TARS 1.5 7B', 
        'Phi-Ground-7B',
        'SFT-7B (35k)',
        'GTA1-7B'
    ],
    'screenspot_pro': [42.0, 43.2, 47.18, 50.1],
    'screenspot_v2': [],  # Will be computed from breakdown averages
    'showdown_clicks': [67.2, 62.5, 69.12, 68.76]  # Add known values
}

# ScreenSpot V2 subset performance data
screenspot_v2_subsets = {
    'SFT-7B (35k)': {
        'Desktop Text': 97.9,    # 190/194
        'Desktop Icon': 80.7,    # 113/140  
        'Web Text': 94.0,        # 220/234
        'Web Icon': 86.7         # 176/203
    },
    'Phi-Ground-7B': {
        'Desktop Text': 90.2,    # From your data
        'Desktop Icon': 76.4,    # From your data
        'Web Text': 93.6,        # From your data
        'Web Icon': 73.9         # From your data
    },
    'UI-TARS 1.5 7B': {
        'Desktop Text': 92.2,    # From your new data
        'Desktop Icon': 81.5,    # From your new data
        'Web Text': 91.0,        # From your new data
        'Web Icon': 84.2         # From your new data
    },
    'GTA1-7B': {
        'Desktop Text': 94.9,    # From your new data
        'Desktop Icon': 89.3,    # From your new data
        'Web Text': 92.3,        # From your new data
        'Web Icon': 86.7         # From your new data
    }
}

# Compute overall ScreenSpot V2 performance as average of desktop and web averages
def compute_overall_v2_performance():
    overall_v2 = []
    for model in performance_data['models']:
        if model in screenspot_v2_subsets:
            # Get desktop average
            desktop_avg = (screenspot_v2_subsets[model]['Desktop Text'] + 
                          screenspot_v2_subsets[model]['Desktop Icon']) / 2
            # Get web average  
            web_avg = (screenspot_v2_subsets[model]['Web Text'] + 
                      screenspot_v2_subsets[model]['Web Icon']) / 2
            # Overall average
            overall_avg = (desktop_avg + web_avg) / 2
            overall_v2.append(overall_avg)
        else:
            overall_v2.append(None)
    return overall_v2

# Update the screenspot_v2 data
performance_data['screenspot_v2'] = compute_overall_v2_performance()

# Colors for different datasets
dataset_colors = {
    'ScreenSpot Pro': '#2E86AB',
    'ScreenSpot V2': '#F24236', 
    'Showdown Clicks': '#A23B72'
}

def create_performance_plot_with_table():
    """Create a performance plot with ordered bars and performance breakdown table."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [2, 1]})
    
    # Prepare data for plotting - sort by overall average performance
    models = performance_data['models']
    ss_pro_data = performance_data['screenspot_pro']
    ss_v2_data = performance_data['screenspot_v2']
    showdown_data = performance_data['showdown_clicks']
    
    # Calculate overall average for sorting (only include available data)
    overall_averages = []
    for i, model in enumerate(models):
        values = []
        if ss_pro_data[i] is not None:
            values.append(ss_pro_data[i])
        if ss_v2_data[i] is not None:
            values.append(ss_v2_data[i])
        if showdown_data[i] is not None:
            values.append(showdown_data[i])
        overall_averages.append(np.mean(values) if values else 0)
    
    # Sort all data by overall average (least to most)
    sorted_indices = np.argsort(overall_averages)
    sorted_models = [models[i] for i in sorted_indices]
    sorted_ss_pro = [ss_pro_data[i] for i in sorted_indices]
    sorted_ss_v2 = [ss_v2_data[i] for i in sorted_indices]
    sorted_showdown = [showdown_data[i] for i in sorted_indices]
    
    # Create the bar plot
    n_models = len(sorted_models)
    x = np.arange(n_models)
    bar_width = 0.25
    
    # Create grouped bars
    bars1 = ax1.bar(x - bar_width, sorted_ss_pro, bar_width, 
                   label='ScreenSpot Pro', color=dataset_colors['ScreenSpot Pro'], 
                   alpha=0.8, edgecolor='black', linewidth=0.8)
    
    # Only plot V2 and Showdown data where available
    ss_v2_plot = [val if val is not None else 0 for val in sorted_ss_v2]
    showdown_plot = [val if val is not None else 0 for val in sorted_showdown]
    
    bars2 = ax1.bar(x, ss_v2_plot, bar_width,
                   label='ScreenSpot V2', color=dataset_colors['ScreenSpot V2'], 
                   alpha=0.8, edgecolor='black', linewidth=0.8)
    
    bars3 = ax1.bar(x + bar_width, showdown_plot, bar_width,
                   label='Showdown Clicks', color=dataset_colors['Showdown Clicks'], 
                   alpha=0.8, edgecolor='black', linewidth=0.8)
    
    # Hide bars where data is not available
    for i, (v2_val, show_val) in enumerate(zip(sorted_ss_v2, sorted_showdown)):
        if v2_val is None:
            bars2[i].set_visible(False)
        if show_val is None:
            bars3[i].set_visible(False)
    
    # Highlight our model
    our_model_idx = sorted_models.index('SFT-7B (35k)')
    bars1[our_model_idx].set_edgecolor('darkblue')
    bars1[our_model_idx].set_linewidth(3)
    if sorted_ss_v2[our_model_idx] is not None:
        bars2[our_model_idx].set_edgecolor('darkred')
        bars2[our_model_idx].set_linewidth(3)
    if sorted_showdown[our_model_idx] is not None:
        bars3[our_model_idx].set_edgecolor('purple')
        bars3[our_model_idx].set_linewidth(3)
    
    # Add value labels on bars
    def add_value_labels(ax, bars, data, offset_y=1):
        for bar, val in zip(bars, data):
            if val is not None and bar.get_visible():
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + offset_y,
                        f'{val:.1f}%', ha='center', va='bottom', 
                        fontsize=9, fontweight='bold')
    
    add_value_labels(ax1, bars1, sorted_ss_pro)
    add_value_labels(ax1, bars2, sorted_ss_v2)
    add_value_labels(ax1, bars3, sorted_showdown)
    
    # Customize the plot
    ax1.set_xlabel('Models (Ordered by Performance)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Multi-Dataset Performance Comparison', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([model.replace(' 7B', '').replace('(35k)', '') for model in sorted_models], 
                       rotation=45, ha='right', fontsize=10)
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend(fontsize=10)
    
    # Create performance breakdown table
    ax2.axis('off')  # Turn off axis for table
    
    # Prepare table data
    table_data = []
    headers = ['Model', 'SS Pro', 'SS V2', 'Desktop\nText', 'Desktop\nIcon', 'Web\nText', 'Web\nIcon', 'Showdown']
    
    # Get models with breakdown data
    breakdown_models = ['UI-TARS 1.5 7B', 'Phi-Ground-7B', 'SFT-7B (35k)', 'GTA1-7B']
    
    for model in breakdown_models:
        model_idx = models.index(model)
        row = [
            model.replace(' 7B', '').replace('(35k)', ''),
            f"{ss_pro_data[model_idx]:.1f}" if ss_pro_data[model_idx] else "—",
            f"{ss_v2_data[model_idx]:.1f}" if ss_v2_data[model_idx] else "—",
            f"{screenspot_v2_subsets[model]['Desktop Text']:.1f}" if model in screenspot_v2_subsets else "—",
            f"{screenspot_v2_subsets[model]['Desktop Icon']:.1f}" if model in screenspot_v2_subsets else "—",
            f"{screenspot_v2_subsets[model]['Web Text']:.1f}" if model in screenspot_v2_subsets else "—",
            f"{screenspot_v2_subsets[model]['Web Icon']:.1f}" if model in screenspot_v2_subsets else "—",
            f"{showdown_data[model_idx]:.1f}" if showdown_data[model_idx] else "—"
        ]
        table_data.append(row)
    
    # Find best performance in each column (excluding model names)
    best_values = {}
    for col_idx in range(1, len(headers)):
        col_values = []
        for row in table_data:
            if row[col_idx] != "—":
                col_values.append(float(row[col_idx]))
        if col_values:
            best_values[col_idx] = max(col_values)
    
    # Create table with bold formatting for best values
    cell_colors = []
    cell_text = []
    
    for row in table_data:
        row_colors = []
        row_text = []
        for col_idx, cell in enumerate(row):
            if col_idx == 0:  # Model name
                row_colors.append('lightgray')
                row_text.append(cell)
            elif cell != "—" and col_idx in best_values and float(cell) == best_values[col_idx]:
                row_colors.append('lightgreen')
                row_text.append(f"**{cell}**")
            else:
                row_colors.append('white')
                row_text.append(cell)
        cell_colors.append(row_colors)
        cell_text.append(row_text)
    
    # Create the table
    table = ax2.table(cellText=cell_text,
                     colLabels=headers,
                     cellColours=cell_colors,
                     cellLoc='center',
                     loc='center',
                     colColours=['lightblue'] * len(headers))
    
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)
    
    ax2.set_title('Performance Breakdown Table\n(Best values highlighted)', 
                 fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig



def save_plots():
    """Save performance plot with table to the data directory."""
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    # Save performance plot with table
    fig = create_performance_plot_with_table()
    output_path = output_dir / 'performance_comparison_with_table.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Performance plot with table saved to: {output_path}")
    
    plt.show()
    return output_path

if __name__ == "__main__":
    save_plots()

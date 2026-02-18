#!/usr/bin/env python3
"""
Script to plot DAPO model performance over training steps
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

def parse_markdown_data(file_path):
    """Parse the markdown file to extract performance data"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by model sections
    sections = content.split('### ')
    
    data = {}
    
    for section in sections[1:]:  # Skip the first empty section
        lines = section.strip().split('\n')
        model_name = lines[0].strip()
        
        # Extract benchmark type from model name
        if 'osworld-g-eval-refined' in model_name:
            benchmark = 'osworld-g-eval-refined'
            model_key = model_name.replace(' — osworld-g-eval-refined', '')
        elif 'osworld-g-eval' in model_name:
            benchmark = 'osworld-g-eval'
            model_key = model_name.replace(' — osworld-g-eval', '')
        elif 'screenspot-pro-eval' in model_name:
            benchmark = 'screenspot-pro-eval'
            model_key = model_name.replace(' — screenspot-pro-eval', '')
        else:
            continue
            
        # Parse table data
        table_data = []
        for line in lines[2:]:  # Skip header and separator
            if line.strip() and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[1].isdigit():
                    step = int(parts[1])
                    # Strip markdown bold formatting (**text**) from the correct value
                    correct_str = parts[3].replace('**', '')
                    correct = int(correct_str)
                    # Use correct total based on benchmark type
                    if benchmark == 'screenspot-pro-eval':
                        total = 1581
                    else:  # OSWorld benchmarks
                        total = 564
                    # Recalculate accuracy using correct total
                    accuracy = correct / total
                    table_data.append({
                        'step': step,
                        'accuracy': accuracy,
                        'correct': correct,
                        'total': total
                    })
        
        if table_data:
            if model_key not in data:
                data[model_key] = {}
            data[model_key][benchmark] = pd.DataFrame(table_data)
    
    return data

def create_performance_plots(data, output_dir='/p/project1/synthlaion/awadalla1/cua/journal/'):
    """Create performance plots for all models - separate plots for each benchmark"""
    
    # Model name mapping
    model_names = {
        'grpo-7b-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick': 'SFT-7B',
        'grpo-soup-7b-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick-no-system-prompt': 'Soup-7B',
        'uitars-7b-grpo-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick-4nodes': 'UITARS-7B'
    }
    
    # Define colors for each model
    model_colors = {
        'grpo-7b-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick': '#1f77b4',
        'grpo-soup-7b-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick-no-system-prompt': '#ff7f0e',
        'uitars-7b-grpo-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick-4nodes': '#2ca02c'
    }
    
    # Baseline accuracies for GTA1-7B
    baseline_gta1_osworld = 55.1 / 100  # Convert percentage to decimal
    baseline_gta1_refined = 67.7 / 100  # Convert percentage to decimal
    
    # Create separate plots for each benchmark
    benchmarks_to_plot = [
        ('osworld-g-eval', 'OSWorld-G-Eval Benchmark', baseline_gta1_osworld, 0.50, 0.65),
        ('osworld-g-eval-refined', 'OSWorld-G-Eval-Refined Benchmark ⭐', baseline_gta1_refined, 0.60, 0.75),
        ('screenspot-pro-eval', 'ScreenSpot-Pro-Eval Benchmark', None, 0.45, 0.55)
    ]
    
    for benchmark_key, benchmark_title, baseline_acc, y_min, y_max in benchmarks_to_plot:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        for model_key, benchmarks in data.items():
            if benchmark_key in benchmarks:
                df = benchmarks[benchmark_key]
                df_filtered = df[df['accuracy'] > 0]
                if not df_filtered.empty:
                    # Plot the main line
                    ax.plot(df_filtered['step'], df_filtered['accuracy'], 
                            marker='o', linewidth=2, markersize=4,
                            color=model_colors.get(model_key, 'gray'),
                            label=model_names.get(model_key, model_key))
                    
                    # Find and highlight best checkpoint
                    best_idx = df_filtered['accuracy'].idxmax()
                    best_step = df_filtered.loc[best_idx, 'step']
                    best_acc = df_filtered.loc[best_idx, 'accuracy']
                    
                    # Calculate improvement from initial accuracy
                    initial_acc = df_filtered.iloc[0]['accuracy']
                    improvement_pct = ((best_acc - initial_acc) / initial_acc) * 100
                    
                    # Circle the best point
                    ax.scatter([best_step], [best_acc], 
                             s=200, facecolors='none', edgecolors=model_colors.get(model_key, 'gray'),
                             linewidth=3, zorder=5)
                    
                    # Annotate the best accuracy and improvement
                    annotation_text = f'{best_acc:.3f}\n(+{improvement_pct:+.1f}%)'
                    ax.annotate(annotation_text, 
                              xy=(best_step, best_acc), 
                              xytext=(10, 10), textcoords='offset points',
                              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                              fontsize=10, fontweight='bold',
                              color=model_colors.get(model_key, 'gray'),
                              ha='left')
        
        # Add baseline line for GTA1-7B (if available)
        if baseline_acc is not None:
            ax.axhline(y=baseline_acc, color='red', linestyle='--', linewidth=2, 
                       label='GTA1-7B Baseline', alpha=0.8)
        
        ax.set_title(benchmark_title, fontweight='bold', fontsize=14)
        ax.set_xlabel('Training Step', fontsize=12)
        ax.set_ylabel('Accuracy', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        ax.set_ylim(y_min, y_max)
        
        plt.tight_layout()
        safe_benchmark = benchmark_key.replace('-', '_')
        plt.savefig(f'{output_dir}{safe_benchmark}_performance.jpg', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Plot saved: {safe_benchmark}_performance.jpg")
    
    return None

def create_individual_model_plots(data, output_dir='/p/project1/synthlaion/awadalla1/cua/journal/'):
    """Create individual plots for each model showing both benchmarks"""
    
    # Model name mapping
    model_names = {
        'grpo-7b-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick': 'SFT-7B',
        'grpo-soup-7b-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick-no-system-prompt': 'Soup-7B',
        'uitars-7b-grpo-stage-1-on-103k-filtered-data-dynamic-sampling-clip-high-no-pixmo-uground-seeclick-4nodes': 'UITARS-7B'
    }
    
    # Baseline accuracies for GTA1-7B
    baseline_gta1_osworld = 55.1 / 100  # Convert percentage to decimal
    baseline_gta1_refined = 67.7 / 100  # Convert percentage to decimal
    
    for model_key, benchmarks in data.items():
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        benchmark_names = ['osworld-g-eval', 'osworld-g-eval-refined', 'screenspot-pro-eval']
        benchmark_labels = ['OSWorld-G-Eval', 'OSWorld-G-Eval-Refined ⭐', 'ScreenSpot-Pro-Eval']
        
        for i, (benchmark, color, label) in enumerate(zip(benchmark_names, colors, benchmark_labels)):
            if benchmark in benchmarks:
                df = benchmarks[benchmark]
                df_filtered = df[df['accuracy'] > 0]
                if not df_filtered.empty:
                    ax.plot(df_filtered['step'], df_filtered['accuracy'], 
                           marker='o', linewidth=2, markersize=4,
                           color=color, label=label)
                    
                    # Find and highlight best checkpoint
                    best_idx = df_filtered['accuracy'].idxmax()
                    best_step = df_filtered.loc[best_idx, 'step']
                    best_acc = df_filtered.loc[best_idx, 'accuracy']
                    
                    # Calculate improvement from initial accuracy
                    initial_acc = df_filtered.iloc[0]['accuracy']
                    improvement_pct = ((best_acc - initial_acc) / initial_acc) * 100
                    
                    # Circle the best point
                    ax.scatter([best_step], [best_acc], 
                             s=200, facecolors='none', edgecolors=color,
                             linewidth=3, zorder=5)
                    
                    # Annotate the best accuracy and improvement
                    annotation_text = f'{best_acc:.3f}\n(+{improvement_pct:+.1f}%)'
                    ax.annotate(annotation_text, 
                              xy=(best_step, best_acc), 
                              xytext=(10, 10), textcoords='offset points',
                              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                              fontsize=10, fontweight='bold',
                              color=color,
                              ha='left')
        
        # Add baseline lines (only for OSWorld benchmarks)
        ax.axhline(y=baseline_gta1_osworld, color='red', linestyle='--', linewidth=2, 
                   label='GTA1-7B Baseline (OSWorld)', alpha=0.8)
        ax.axhline(y=baseline_gta1_refined, color='darkred', linestyle='--', linewidth=2, 
                   label='GTA1-7B Baseline (Refined)', alpha=0.8)
        
        model_display_name = model_names.get(model_key, model_key.split('-')[0].upper())
        ax.set_title(f'{model_display_name} Model Performance', fontweight='bold')
        ax.set_xlabel('Training Step')
        ax.set_ylabel('Accuracy')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        safe_name = model_key.replace(' ', '_').replace('-', '_')
        plt.savefig(f'{output_dir}{safe_name}_performance.jpg', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Individual plot saved for {model_display_name}")

def analyze_performance_trends(data):
    """Analyze and print performance trends"""
    
    print("\n" + "="*60)
    print("DAPO PERFORMANCE ANALYSIS")
    print("="*60)
    
    for model_key, benchmarks in data.items():
        print(f"\n{model_key.split('-')[0].upper()} Model:")
        print("-" * 40)
        
        for benchmark_name, df in benchmarks.items():
            df_filtered = df[df['accuracy'] > 0]
            if not df_filtered.empty:
                initial_acc = df_filtered.iloc[0]['accuracy']
                final_acc = df_filtered.iloc[-1]['accuracy']
                max_acc = df_filtered['accuracy'].max()
                min_acc = df_filtered['accuracy'].min()
                
                print(f"  {benchmark_name}:")
                print(f"    Initial Accuracy: {initial_acc:.4f}")
                print(f"    Final Accuracy:   {final_acc:.4f}")
                print(f"    Best Accuracy:    {max_acc:.4f}")
                print(f"    Worst Accuracy:   {min_acc:.4f}")
                print(f"    Improvement:      {final_acc - initial_acc:+.4f}")
                print(f"    Range:            {max_acc - min_acc:.4f}")

if __name__ == "__main__":
    # Parse the data
    data = parse_markdown_data('/p/project1/synthlaion/awadalla1/cua/journal/dapo.md')
    
    # Create plots
    print("Creating performance plots...")
    create_performance_plots(data)
    create_individual_model_plots(data)
    
    # Analyze trends
    analyze_performance_trends(data)
    
    print("\nAnalysis complete!")

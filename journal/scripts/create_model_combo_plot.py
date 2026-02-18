#!/usr/bin/env python3
"""
Create a simple bar chart comparing SS Pro accuracy for:
- Best SFT model (49.65)
- Model finetuned on Pro App Icon data (49.08)
- Weight-averaged model of the two above (49.52)

Saves to journal/data/model_combo_plot.png
"""

from pathlib import Path
import matplotlib

# Use a non-interactive backend for headless environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def create_model_combo_plot() -> Path:
    model_names = [
        "Best SFT (SS Pro)",
        "Icon FT",
        "Weight Averaged",
    ]
    accuracies = [49.65, 49.08, 49.52]

    figure, axis = plt.subplots(figsize=(8, 5))

    x_positions = list(range(len(model_names)))
    bar_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    bars = axis.bar(
        x_positions,
        accuracies,
        color=bar_colors,
        width=0.6,
        edgecolor="black",
        linewidth=0.8,
        zorder=3,
    )

    axis.set_xticks(x_positions)
    axis.set_xticklabels(model_names, fontsize=10)
    axis.set_ylabel("SS Pro Accuracy (%)", fontsize=12)
    axis.set_title(
        "SS Pro: Best vs Pro App Icon FT vs Weight Averaged",
        fontsize=13,
        pad=12,
    )
    axis.set_ylim(0, 100)
    axis.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)

    for bar, value in zip(bars, accuracies):
        axis.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.6,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    figure.tight_layout()

    output_path = (
        Path(__file__).resolve().parent.parent / "data" / "model_combo_plot.png"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=200)
    plt.close(figure)
    return output_path


def main() -> None:
    output_path = create_model_combo_plot()
    print(f"Saved plot to: {output_path}")


if __name__ == "__main__":
    main()



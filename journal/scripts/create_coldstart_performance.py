import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS_ROOT_DEFAULT = "/p/project1/synthlaion/awadalla1/rl_eval_results"
ASSETS_DIR_DEFAULT = "/p/project1/synthlaion/awadalla1/cua/journal/data"

# SFT baselines (fractions)
SFT_BASELINE = {
    "OSWorld-G": 0.6640,        # 66.4%
    "ScreenSpot-Pro": 0.5008,   # 50.08%
}


DATASET_NAME_MAP = {
    # filename stem fragments -> label
    "screenspot-pro-eval": "ScreenSpot-Pro",
    "osworld-g-eval-refined": "OSWorld-G",
}


def is_grounding_eval_json(path: Path) -> bool:
    name = path.name
    return name.startswith("grounding_eval_") and name.endswith(".json")


def extract_dataset_from_filename(path: Path) -> Optional[str]:
    # filename like grounding_eval_<dataset>_huggingface_<timestamp>.json
    name = path.name
    if not name.startswith("grounding_eval_") or not name.endswith(".json"):
        return None
    tail = name[len("grounding_eval_"):]
    # Split on underscores and join tokens until we hit 'huggingface'
    parts = tail.split("_")
    dataset_tokens: List[str] = []
    for tok in parts:
        if tok == "huggingface":
            break
        # Remove trailing .json if present on last token (defensive)
        tok = tok.replace(".json", "")
        dataset_tokens.append(tok)
    if not dataset_tokens:
        return None
    stem = "_".join(dataset_tokens)
    for frag, label in DATASET_NAME_MAP.items():
        if frag == stem:
            return label
    # fallback to raw stem if not mapped
    return stem


def parse_accuracy_from_json(path: Path) -> Optional[float]:
    try:
        with open(path, "r") as f:
            d = json.load(f)
        # accept both flat and nested formats
        if isinstance(d, dict):
            if "accuracy" in d:
                acc = d["accuracy"]
                if isinstance(acc, (int, float)):
                    return float(acc)
            # Some results might nest under metrics
            metrics = d.get("metrics") if isinstance(d.get("metrics"), dict) else None
            if metrics and "accuracy" in metrics:
                acc = metrics["accuracy"]
                if isinstance(acc, (int, float)):
                    return float(acc)
        return None
    except Exception:
        return None


def numeric_step_from_dir(step_dir: Path) -> int:
    # step dir names like global_step_40 or checkpoint-400
    m = re.search(r"(global_step_|checkpoint-)(\d+)", step_dir.name)
    if m:
        try:
            return int(m.group(2))
        except Exception:
            return -1
    # fallback: try last digits in name
    tail = re.findall(r"(\d+)", step_dir.name)
    if tail:
        try:
            return int(tail[-1])
        except Exception:
            return -1
    return -1


def pretty_budget_from_model_dir(model_dir: Path) -> Optional[str]:
    # model dir names start with grpo-coldstart-<budget>-on-...
    m = re.match(r"grpo-coldstart-([^-]+)-on-", model_dir.name)
    if not m:
        return None
    raw = m.group(1)
    # Convert 3_3k -> 3.3k
    raw = raw.replace("_", ".")
    return raw


def find_best_step_dir(model_dir: Path) -> Optional[Path]:
    step_dirs: List[Path] = [p for p in model_dir.iterdir() if p.is_dir() and (p.name.startswith("global_step_") or p.name.startswith("checkpoint-"))]
    if not step_dirs:
        return None
    # Prefer steps that actually contain both dataset result JSONs; fall back to any with at least one JSON
    def has_json(sd: Path) -> bool:
        try:
            for f in sd.iterdir():
                if f.is_file() and f.name.startswith("grounding_eval_") and f.name.endswith(".json"):
                    return True
        except Exception:
            pass
        return False

    def has_both(sd: Path) -> bool:
        try:
            names = {f.name for f in sd.iterdir() if f.is_file()}
        except Exception:
            names = set()
        need = {
            "grounding_eval_osworld-g-eval-refined",
            "grounding_eval_screenspot-pro-eval",
        }
        found = set()
        for n in names:
            for prefix in need:
                if n.startswith(prefix + "_"):
                    found.add(prefix)
        return need.issubset(found)

    with_both = [sd for sd in step_dirs if has_both(sd)]
    if with_both:
        with_both.sort(key=numeric_step_from_dir)
        return with_both[-1]

    with_any = [sd for sd in step_dirs if has_json(sd)]
    if with_any:
        with_any.sort(key=numeric_step_from_dir)
        return with_any[-1]

    # Fallback to latest step numerically
    step_dirs.sort(key=numeric_step_from_dir)
    return step_dirs[-1]


def collect_model_step_metrics(step_dir: Path) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    for f in step_dir.iterdir():
        if f.is_file() and is_grounding_eval_json(f):
            ds = extract_dataset_from_filename(f)
            if not ds:
                continue
            acc = parse_accuracy_from_json(f)
            if acc is not None:
                metrics[ds] = acc
    return metrics


def collect_coldstart(results_root: Path) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for model_dir in results_root.iterdir():
        if not model_dir.is_dir():
            continue
        if not model_dir.name.startswith("grpo-coldstart-"):
            continue
        budget = pretty_budget_from_model_dir(model_dir)
        if not budget:
            continue
        step_dir = find_best_step_dir(model_dir)
        if not step_dir:
            continue
        metrics = collect_model_step_metrics(step_dir)
        if metrics:
            out[budget] = metrics
    return out


def find_dir_by_pred(results_root: Path, pred) -> List[Path]:
    return [d for d in results_root.iterdir() if d.is_dir() and pred(d)]


def collect_temperature_ablations(results_root: Path) -> Dict[str, Dict[str, float]]:
    # Focus on 10k budget variants
    # temp dir fragments: _temp_1_0, _temp_0_65
    variants = {}
    # Baseline: 10k without temp suffix
    baseline_dirs = find_dir_by_pred(results_root, lambda d: d.name.startswith("grpo-coldstart-10k-") and "_temp_" not in d.name)
    if baseline_dirs:
        step_dir = find_best_step_dir(baseline_dirs[0])
        if step_dir:
            variants["temp_0.85"] = collect_model_step_metrics(step_dir)
    for tval in ["1_0", "0_65"]:
        dirs = find_dir_by_pred(results_root, lambda d, tval=tval: d.name.startswith("grpo-coldstart-10k-") and (f"_temp_{tval}" in d.name))
        if dirs:
            step_dir = find_best_step_dir(dirs[0])
            if step_dir:
                key = f"temp_{tval.replace('_', '.')}"
                variants[key] = collect_model_step_metrics(step_dir)
    return variants


def collect_ui_venus_ablations(results_root: Path) -> Dict[str, Dict[str, float]]:
    # Compare 63k baseline vs ui_venus_like variant
    out = {}
    baseline_dirs = find_dir_by_pred(results_root, lambda d: d.name.startswith("grpo-coldstart-63k-") and ("ui_venus_like" not in d.name))
    if baseline_dirs:
        step_dir = find_best_step_dir(baseline_dirs[0])
        if step_dir:
            out["default"] = collect_model_step_metrics(step_dir)
    venus_dirs = find_dir_by_pred(results_root, lambda d: d.name.startswith("grpo-coldstart-63k-") and ("ui_venus_like" in d.name))
    if venus_dirs:
        step_dir = find_best_step_dir(venus_dirs[0])
        if step_dir:
            out["ui_venus_like"] = collect_model_step_metrics(step_dir)
    return out


# -------------------- Per-step scaling aggregation & plotting --------------------

def sanitize_for_filename(name: str) -> str:
    return re.sub(r"[<>:\\/_|?*]", "_", name)


def collect_per_step_metrics_for_experiment(model_dir: Path) -> Dict[int, Dict[str, float]]:
    """
    For a given experiment directory, collect accuracies per step.
    Returns dict: step_num -> { dataset_label -> accuracy }
    """
    per_step: Dict[int, Dict[str, float]] = {}
    step_dirs: List[Path] = [p for p in model_dir.iterdir() if p.is_dir() and (p.name.startswith("global_step_") or p.name.startswith("checkpoint-"))]
    for sd in step_dirs:
        step = numeric_step_from_dir(sd)
        if step < 0:
            continue
        mets = collect_model_step_metrics(sd)
        if mets:
            per_step[step] = mets
    return dict(sorted(per_step.items(), key=lambda kv: kv[0]))


def plot_experiment_scaling(model_dir: Path, per_step: Dict[int, Dict[str, float]], assets_dir: Path) -> Optional[Path]:
    if not per_step:
        return None
    steps_sorted = sorted(per_step.keys())
    datasets = sorted({ds for v in per_step.values() for ds in v.keys()})

    plt.figure(figsize=(8, 5))
    for ds in datasets:
        ys = [per_step.get(s, {}).get(ds, float('nan')) for s in steps_sorted]
        plt.plot(steps_sorted, ys, marker='o', label=ds)
    # Baselines
    if "OSWorld-G" in datasets:
        plt.axhline(SFT_BASELINE["OSWorld-G"], color='gray', linestyle='--', linewidth=1, label='SFT baseline (OSWorld-G)')
    if "ScreenSpot-Pro" in datasets:
        plt.axhline(SFT_BASELINE["ScreenSpot-Pro"], color='lightgray', linestyle='--', linewidth=1, label='SFT baseline (ScreenSpot-Pro)')

    plt.xlabel("Global step")
    plt.ylabel("Accuracy")
    plt.title(model_dir.name)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_dir = assets_dir / "scaling"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"scaling_{sanitize_for_filename(model_dir.name)}.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path


def collect_and_plot_all_experiments(results_root: Path, assets_dir: Path) -> Tuple[Dict[str, Dict[int, Dict[str, float]]], List[Tuple[str, Path]]]:
    """
    Collect per-step metrics and generate scaling plots for all experiments under results_root.
    Returns (per_step_all, plot_paths), where per_step_all maps experiment name -> per-step metrics.
    """
    per_step_all: Dict[str, Dict[int, Dict[str, float]]] = {}
    plot_paths: List[Tuple[str, Path]] = []
    for model_dir in results_root.iterdir():
        if not model_dir.is_dir():
            continue
        if not model_dir.name.startswith("grpo-coldstart-"):
            continue
        per_step = collect_per_step_metrics_for_experiment(model_dir)
        if per_step:
            per_step_all[model_dir.name] = per_step
            plot_path = plot_experiment_scaling(model_dir, per_step, assets_dir)
            if plot_path:
                plot_paths.append((model_dir.name, plot_path))
    return per_step_all, plot_paths


# -------------------- Comparative overlay scaling plots --------------------

def _plot_overlay_for_dirs(model_dirs: List[Path], label_fn, title_prefix: str, out_filename: str, assets_dir: Path) -> Optional[Path]:
    if not model_dirs:
        return None
    # Collect per-step for each dir
    series = []  # list of (label, steps_sorted, per_step dict)
    for d in model_dirs:
        per_step = collect_per_step_metrics_for_experiment(d)
        if per_step:
            label = label_fn(d)
            series.append((label, sorted(per_step.keys()), per_step))
    if not series:
        return None

    datasets = sorted({ds for _, _, ps in series for ds in (set().union(*[set(m.keys()) for m in [ps[s] for s in ps]]))})
    # Constrain to two known datasets if present
    preferred = ["OSWorld-G", "ScreenSpot-Pro"]
    datasets = [ds for ds in preferred if ds in datasets] or datasets

    fig, axes = plt.subplots(1, len(datasets), figsize=(12, 4), sharey=True)
    if len(datasets) == 1:
        axes = [axes]

    colors = plt.cm.tab10.colors

    for ax, ds in zip(axes, datasets):
        for idx, (label, steps_sorted, per_step) in enumerate(series):
            ys = [per_step.get(s, {}).get(ds, float('nan')) for s in steps_sorted]
            ax.plot(steps_sorted, ys, marker='o', linewidth=2, color=colors[idx % len(colors)], label=label)
        # Baseline for this dataset
        if ds in SFT_BASELINE:
            ax.axhline(SFT_BASELINE[ds], color='gray', linestyle='--', linewidth=1, label='SFT baseline')
        ax.set_title(ds)
        ax.set_xlabel("Global step")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Accuracy")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=min(4, len(series)))
    fig.suptitle(title_prefix)
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])

    out_path = assets_dir / out_filename
    plt.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_coldstart_overlay_scaling(results_root: Path, assets_dir: Path) -> Optional[Path]:
    # Select baseline coldstart (exclude temp and ui_venus_like)
    dirs = [d for d in results_root.iterdir() if d.is_dir() and d.name.startswith('grpo-coldstart-') and '_temp_' not in d.name and 'ui_venus_like' not in d.name]
    # Sort by budget
    def budget_value(d: Path) -> float:
        b = pretty_budget_from_model_dir(d) or ""
        bb = b.lower().replace('k','')
        try:
            return float(bb)
        except Exception:
            return float('inf')
    dirs = sorted(dirs, key=budget_value)
    return _plot_overlay_for_dirs(
        dirs,
        label_fn=lambda d: pretty_budget_from_model_dir(d) or d.name,
        title_prefix="Coldstart: full trajectories across SFT budgets",
        out_filename="rl_coldstart_scaling_overlay.png",
        assets_dir=assets_dir,
    )


def plot_temp_overlay_scaling(results_root: Path, assets_dir: Path) -> Optional[Path]:
    # Select 10k variants including baseline
    dirs = [d for d in results_root.iterdir() if d.is_dir() and d.name.startswith('grpo-coldstart-10k-')]
    # Label mapping
    def label_fn(d: Path) -> str:
        n = d.name
        if '_temp_1_0' in n:
            return 'temp 1.0'
        if '_temp_0_65' in n:
            return 'temp 0.65'
        return 'temp 0.85'
    # Deterministic ordering
    order_key = lambda d: {'temp 0.65': 0, 'temp 0.85': 1, 'temp 1.0': 2}[label_fn(d)]
    dirs = sorted(dirs, key=order_key)
    return _plot_overlay_for_dirs(
        dirs,
        label_fn=label_fn,
        title_prefix="10k temperature ablations: full trajectories",
        out_filename="rl_temp_ablations_10k_scaling.png",
        assets_dir=assets_dir,
    )


def plot_ui_venus_overlay_scaling(results_root: Path, assets_dir: Path) -> Optional[Path]:
    # Select 63k default and ui_venus_like
    dirs = [d for d in results_root.iterdir() if d.is_dir() and d.name.startswith('grpo-coldstart-63k-') and (('ui_venus_like' in d.name) or ('ui_venus_like' not in d.name))]
    # Keep only one default and one ui_venus_like if multiple
    default_dirs = [d for d in dirs if 'ui_venus_like' not in d.name]
    venus_dirs = [d for d in dirs if 'ui_venus_like' in d.name]
    selected = []
    if default_dirs:
        selected.append(default_dirs[0])
    if venus_dirs:
        selected.append(venus_dirs[0])
    return _plot_overlay_for_dirs(
        selected,
        label_fn=lambda d: ('ui_venus_like' if 'ui_venus_like' in d.name else 'default'),
        title_prefix="63k UI Venus vs default: full trajectories",
        out_filename="rl_ui_venus_vs_default_63k_scaling.png",
        assets_dir=assets_dir,
    )


def write_per_step_summary(per_step_all: Dict[str, Dict[int, Dict[str, float]]], assets_dir: Path) -> Path:
    out = {}
    for exp_name, per_step in per_step_all.items():
        out[exp_name] = {str(step): metrics for step, metrics in per_step.items()}
    out_path = assets_dir / "rl_per_step_scaling.json"
    assets_dir.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    return out_path


# -------------------- Comparative plots --------------------

def plot_coldstart_side_by_side(coldstart: Dict[str, Dict[str, float]], assets_dir: Path) -> Path:
    budgets = sorted(coldstart.keys(), key=lambda b: (float(b.lower().replace('k','').replace(',','.')) if b.lower().endswith('k') else float('inf')))
    datasets = ["OSWorld-G", "ScreenSpot-Pro"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, ds in zip(axes, datasets):
        ys = [coldstart.get(b, {}).get(ds, float('nan')) for b in budgets]
        ax.plot(budgets, ys, marker='o', linewidth=2)
        # Baseline for this dataset
        if ds in SFT_BASELINE:
            ax.axhline(SFT_BASELINE[ds], color='gray', linestyle='--', linewidth=1, label='SFT baseline')
        ax.set_title(ds)
        ax.set_xlabel("SFT budget")
        ax.grid(True, alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("Accuracy")
    fig.suptitle("Coldstart across SFT budgets (by dataset)")
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    out_path = assets_dir / "rl_coldstart_side_by_side.png"
    plt.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_temperature_ablations(temp_ablate: Dict[str, Dict[str, float]], assets_dir: Path) -> Path:
    # Normalize ordering and labels
    order = ["temp_0.65", "temp_0.85", "temp_1.0"]
    labels = ["temp=0.65", "temp=0.85 (baseline)", "temp=1.0"]
    datasets = ["OSWorld-G", "ScreenSpot-Pro"]

    x = range(len(order))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4))
    for i, ds in enumerate(datasets):
        vals = [temp_ablate.get(k, {}).get(ds, float('nan')) for k in order]
        ax.bar([p + (i - 0.5) * width for p in x], vals, width=width, label=ds)
    # Baselines
    for ds, base in SFT_BASELINE.items():
        ax.axhline(base, color='gray' if ds=="OSWorld-G" else 'lightgray', linestyle='--', linewidth=1, label=f'SFT baseline ({ds})')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15)
    ax.set_ylabel("Accuracy")
    ax.set_title("Temperature ablations (10k SFT)")
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend()
    fig.tight_layout()

    out_path = assets_dir / "rl_temp_ablations_10k.png"
    plt.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


def plot_ui_venus_vs_default(venus_ablate: Dict[str, Dict[str, float]], assets_dir: Path) -> Path:
    variants = ["default", "ui_venus_like"]
    labels = ["default", "ui_venus_like"]
    datasets = ["OSWorld-G", "ScreenSpot-Pro"]

    x = range(len(datasets))
    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 4))
    for i, variant in enumerate(variants):
        vals = [venus_ablate.get(variant, {}).get(ds, float('nan')) for ds in datasets]
        ax.bar([p + (i - 0.5) * width for p in x], vals, width=width, label=labels[i])
    # Baselines
    for ds, base in SFT_BASELINE.items():
        ax.axhline(base, color='gray' if ds=="OSWorld-G" else 'lightgray', linestyle='--', linewidth=1, label=f'SFT baseline ({ds})')
    ax.set_xticks(list(x))
    ax.set_xticklabels(datasets)
    ax.set_ylabel("Accuracy")
    ax.set_title("63k: UI Venus parameters vs default")
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend()
    fig.tight_layout()

    out_path = assets_dir / "rl_ui_venus_vs_default_63k.png"
    plt.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


# -------------------- Existing coldstart summary & plotting --------------------

def write_summary_files(coldstart: Dict[str, Dict[str, float]],
                        temp_ablate: Dict[str, Dict[str, float]],
                        venus_ablate: Dict[str, Dict[str, float]],
                        assets_dir: Path) -> Tuple[Path, Path]:
    assets_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "coldstart": coldstart,
        "ablations": {
            "temperature_10k": temp_ablate,
            "ui_venus_like_63k": venus_ablate,
        },
    }
    summary_path = assets_dir / "rl_coldstart_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Also save a CSV for coldstart
    csv_path = assets_dir / "rl_coldstart_metrics.csv"
    # Collect all datasets
    datasets = set()
    for m in coldstart.values():
        datasets.update(m.keys())
    budgets_sorted = sorted(coldstart.keys(), key=lambda b: float(b.replace("k", "").replace(".", "").replace(",", "")) if re.match(r"^[0-9]+(\.[0-9]+)?k$", b) else (1000000 if "k" not in b else float(b[:-1]) * 1000))
    # write header
    with open(csv_path, "w") as f:
        header = ["budget"] + [ds for ds in sorted(datasets)]
        f.write(",".join(header) + "\n")
        for b in budgets_sorted:
            row = [b]
            for ds in sorted(datasets):
                val = coldstart.get(b, {}).get(ds)
                row.append(f"{val:.4f}" if isinstance(val, (int, float)) else "")
            f.write(",".join(row) + "\n")

    return summary_path, csv_path



def plot_coldstart(coldstart: Dict[str, Dict[str, float]], assets_dir: Path) -> Path:
    # Prepare data
    budgets = list(coldstart.keys())
    # Normalize and sort budgets numerically for plotting
    def budget_to_k(b: str) -> float:
        # "3.3k" -> 3.3; "1k" -> 1.0
        bb = b.lower().replace(" ", "")
        bb = bb.replace(",", ".")
        if bb.endswith("k"):
            bb = bb[:-1]
        try:
            return float(bb)
        except Exception:
            return math.inf

    budgets_sorted = sorted(budgets, key=budget_to_k)

    datasets = sorted({ds for m in coldstart.values() for ds in m.keys()})

    plt.figure(figsize=(8, 5))

    for ds in datasets:
        xs = []
        ys = []
        for b in budgets_sorted:
            xs.append(budget_to_k(b))
            ys.append(coldstart.get(b, {}).get(ds, float('nan')))
        plt.plot(xs, ys, marker='o', label=ds)

    # Baselines
    if "OSWorld-G" in datasets:
        plt.axhline(SFT_BASELINE["OSWorld-G"], color='gray', linestyle='--', linewidth=1, label='SFT baseline (OSWorld-G)')
    if "ScreenSpot-Pro" in datasets:
        plt.axhline(SFT_BASELINE["ScreenSpot-Pro"], color='lightgray', linestyle='--', linewidth=1, label='SFT baseline (ScreenSpot-Pro)')

    plt.xlabel("SFT budget (thousands)")
    plt.ylabel("Accuracy")
    plt.title("Coldstart performance vs SFT budget")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = assets_dir / "rl_coldstart_performance.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=str, default=RESULTS_ROOT_DEFAULT)
    parser.add_argument("--assets-dir", type=str, default=ASSETS_DIR_DEFAULT)
    args = parser.parse_args()

    results_root = Path(args.results_root)
    assets_dir = Path(args.assets_dir)

    if not results_root.exists():
        raise SystemExit(f"Results root not found: {results_root}")

    # Per-experiment scaling plots
    per_step_all, plot_paths = collect_and_plot_all_experiments(results_root, assets_dir)
    per_step_json = write_per_step_summary(per_step_all, assets_dir)

    # Coldstart summary across budgets (best step per experiment)
    coldstart = collect_coldstart(results_root)
    temp_ablate = collect_temperature_ablations(results_root)
    venus_ablate = collect_ui_venus_ablations(results_root)

    summary_path, csv_path = write_summary_files(coldstart, temp_ablate, venus_ablate, assets_dir)
    plot_path = plot_coldstart(coldstart, assets_dir)

    # New comparative plots
    side_by_side_path = plot_coldstart_side_by_side(coldstart, assets_dir)
    temp_plot_path = plot_temperature_ablations(temp_ablate, assets_dir)
    venus_plot_path = plot_ui_venus_vs_default(venus_ablate, assets_dir)

    # Overlay scaling plots for full trajectories
    overlay_coldstart = plot_coldstart_overlay_scaling(results_root, assets_dir)
    overlay_temp = plot_temp_overlay_scaling(results_root, assets_dir)
    overlay_venus = plot_ui_venus_overlay_scaling(results_root, assets_dir)

    print(f"Per-step summary JSON: {per_step_json}")
    print(f"Generated {len(plot_paths)} per-experiment scaling plots under {assets_dir / 'scaling'}")
    print(f"Summary JSON: {summary_path}")
    print(f"Coldstart CSV: {csv_path}")
    print(f"Plot saved to: {plot_path}")
    print(f"Side-by-side coldstart plot: {side_by_side_path}")
    print(f"Temperature ablations plot: {temp_plot_path}")
    print(f"UI Venus vs default plot: {venus_plot_path}")
    print(f"Coldstart overlay scaling: {overlay_coldstart}")
    print(f"Temp overlay scaling: {overlay_temp}")
    print(f"UI Venus overlay scaling: {overlay_venus}")


if __name__ == "__main__":
    main()

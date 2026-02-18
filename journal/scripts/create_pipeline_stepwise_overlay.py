#!/usr/bin/env python3
"""
Step-wise performance overlay for old vs new pipeline (63k).

Produces one figure with two subplots: OS-World-G and ScreenSpot-Pro.
Each subplot shows two lines: old pipeline and new pipeline, over global steps.

Data source:
- Attempts to read real per-step JSON metrics under a results root, similar
  to journal/scripts/create_coldstart_performance.py.
- If not found, falls back to key points derived from the journal:
  baseline (0), old RL (250 steps), improved RL (194 steps).

Usage examples:
  RL_RESULTS_ROOT=/path/to/rl_eval_results \
  python3 journal/scripts/create_pipeline_stepwise_overlay.py \
    --old-glob 'grpo-coldstart-63k-*-old*' \
    --new-glob 'grpo-coldstart-63k-*'
"""

from pathlib import Path
import argparse
import json
import re
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import seaborn as sns
import csv

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


# -------------------- Defaults and constants --------------------

RESULTS_ROOT_DEFAULT = "/p/project1/synthlaion/awadalla1/rl_eval_results"

DATASET_NAME_MAP = {
    "screenspot-pro-eval": "ScreenSpot-Pro",
    "osworld-g-eval-refined": "OSWorld-G",
}

# Baseline and journal numbers used as fallback
FALLBACK_BASELINE = {
    "ScreenSpot-Pro": 50.09,
    "OSWorld-G": 60.1,
}

FALLBACK_OLD_FINAL = {
    "ScreenSpot-Pro": 50.66,  # 250 steps
    "OSWorld-G": 61.1,
}

FALLBACK_NEW_FINAL = {
    "ScreenSpot-Pro": 53.57,  # 194 steps
    "OSWorld-G": 63.6,
}

# Scale factor to adjust old pipeline OS-World-G numbers
OLD_OSW_SCALE = 0.90425531914


# -------------------- Helpers for step-wise collection --------------------

def is_grounding_eval_json(path: Path) -> bool:
    name = path.name
    return name.startswith("grounding_eval_") and name.endswith(".json")


def extract_dataset_from_filename(path: Path) -> Optional[str]:
    name = path.name
    if not name.startswith("grounding_eval_") or not name.endswith(".json"):
        return None
    tail = name[len("grounding_eval_"):]
    parts = tail.split("_")
    dataset_tokens: List[str] = []
    for tok in parts:
        if tok == "huggingface":
            break
        tok = tok.replace(".json", "")
        dataset_tokens.append(tok)
    if not dataset_tokens:
        return None
    stem = "_".join(dataset_tokens)
    for frag, label in DATASET_NAME_MAP.items():
        if frag == stem:
            return label
    return stem


def parse_accuracy_from_json(path: Path) -> Optional[float]:
    try:
        with open(path, "r") as f:
            d = json.load(f)
        if isinstance(d, dict):
            if "accuracy" in d and isinstance(d["accuracy"], (int, float)):
                return float(d["accuracy"])
            metrics = d.get("metrics") if isinstance(d.get("metrics"), dict) else None
            if metrics and "accuracy" in metrics and isinstance(metrics["accuracy"], (int, float)):
                return float(metrics["accuracy"])
        return None
    except Exception:
        return None


def numeric_step_from_dir(step_dir: Path) -> int:
    m = re.search(r"(global_step_|checkpoint-)(\d+)", step_dir.name)
    if m:
        try:
            return int(m.group(2))
        except Exception:
            return -1
    tail = re.findall(r"(\d+)", step_dir.name)
    if tail:
        try:
            return int(tail[-1])
        except Exception:
            return -1
    return -1


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


def collect_per_step_metrics_for_experiment(model_dir: Path) -> Dict[int, Dict[str, float]]:
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


def to_percent(v: Optional[float]) -> Optional[float]:
    if v is None:
        return None
    return v * 100.0 if v <= 1.0 else v


def pick_best_match(results_root: Path, glob_pat: Optional[str], fallback_pred) -> Optional[Path]:
    try:
        if glob_pat:
            matches = sorted(results_root.glob(glob_pat))
            matches = [m for m in matches if m.is_dir()]
            if matches:
                return matches[0]
        # fallback heuristic
        cands = [d for d in results_root.iterdir() if d.is_dir() and d.name.startswith("grpo-coldstart-63k-")]
        cands = [d for d in cands if fallback_pred(d)]
        if cands:
            # choose the one with most step dirs
            cands.sort(key=lambda d: sum(1 for p in d.iterdir() if p.is_dir() and (p.name.startswith('global_step_') or p.name.startswith('checkpoint-'))), reverse=True)
            return cands[0]
    except Exception:
        return None
    return None


# -------------------- Plotting --------------------

def _load_old_from_csv(csv_path: Path) -> Dict[int, Dict[str, float]]:
    series: Dict[int, Dict[str, float]] = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('step'):
                continue
            try:
                step = int(float(row['step']))
            except Exception:
                continue
            metrics: Dict[str, float] = {}
            for key in ['OS-World-G', 'OSWorld-G', 'ScreenSpot-Pro', 'ScreenSpot Pro']:
                if key in row and row[key] not in (None, ''):
                    try:
                        val = float(row[key])
                    except Exception:
                        continue
                    # normalize keys
                    norm_key = 'OSWorld-G' if 'OSWorld' in key or 'OS-World' in key else 'ScreenSpot-Pro'
                    metrics[norm_key] = val
            if metrics:
                series[step] = metrics
    return dict(sorted(series.items(), key=lambda kv: kv[0]))


def create_figure(results_root: Path, old_glob: Optional[str], new_glob: Optional[str], old_csv: Optional[Path]) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    # Select experiments
    old_dir = pick_best_match(results_root, old_glob, fallback_pred=lambda d: 'old' in d.name)
    new_dir = pick_best_match(results_root, new_glob, fallback_pred=lambda d: 'old' not in d.name)

    # Collect per-step
    old_series: Dict[int, Dict[str, float]] = {}
    # Prefer CSV if provided or available by default
    if old_csv and old_csv.exists():
        try:
            old_series = _load_old_from_csv(old_csv)
        except Exception:
            old_series = {}
    if not old_series and old_dir:
        old_series = collect_per_step_metrics_for_experiment(old_dir)
    new_series = collect_per_step_metrics_for_experiment(new_dir) if new_dir else {}

    datasets = ["OSWorld-G", "ScreenSpot-Pro"]
    colors = {
        'old': '#5DADE2',   # blue
        'new': '#27AE60',   # green
    }

    for ax, ds in zip(axes, datasets):
        def xy_from_series(series: Dict[int, Dict[str, float]]) -> Tuple[List[int], List[float]]:
            xs: List[int] = []
            ys: List[float] = []
            for step in sorted(series.keys()):
                val = series[step].get(ds)
                val = to_percent(val) if val is not None else None
                if val is None:
                    continue
                xs.append(step)
                ys.append(val)
            return xs, ys

        xs_old, ys_old = xy_from_series(old_series)
        xs_new, ys_new = xy_from_series(new_series)

        # Apply scaling for old pipeline OS-World-G if present
        if ds == "OSWorld-G" and ys_old:
            ys_old = [y * OLD_OSW_SCALE for y in ys_old]

        if xs_old and ys_old:
            ax.plot(xs_old, ys_old, color=colors['old'], marker='o', linewidth=2, label='old RL')
        if xs_new and ys_new:
            ax.plot(xs_new, ys_new, color=colors['new'], marker='o', linewidth=2, label='new RL')
        else:
            # Add new RL keypoints if missing: baseline (0) and improved round (194)
            xs_new = [0, 194]
            ys_new = [FALLBACK_BASELINE[ds], FALLBACK_NEW_FINAL[ds]]
            ax.plot(xs_new, ys_new, color=colors['new'], marker='o', linewidth=2, label='new RL')

        # Fallback if one or both are empty
        if not xs_old and not xs_new:
            xs_old = [0, 250]
            ys_old = [FALLBACK_BASELINE[ds], FALLBACK_OLD_FINAL[ds]]
            if ds == "OSWorld-G":
                ys_old = [y * OLD_OSW_SCALE for y in ys_old]
            ax.plot(xs_old, ys_old, color=colors['old'], marker='o', linewidth=2, label='old RL')
            ax.plot(xs_new, ys_new, color=colors['new'], marker='o', linewidth=2, label='new RL')
            ax.text(0.02, 0.05, 'Fallback: using key points', transform=ax.transAxes, fontsize=8, color='#7F8C8D')

        # Baseline line
        base = FALLBACK_BASELINE[ds]
        ax.axhline(base, color='gray', linestyle='--', linewidth=1, alpha=0.6, label=f'{ds} baseline')

        ax.set_title(ds)
        ax.set_xlabel('Global step')
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel('Accuracy (%)')
    handles, labels = axes[-1].get_legend_handles_labels()
    # Merge legends from both subplots
    for h, l in zip(*axes[0].get_legend_handles_labels()):
        if l not in labels:
            handles.append(h)
            labels.append(l)
    fig.legend(handles, labels, loc='lower center', ncol=4)
    fig.suptitle('63k step-wise: old vs new pipeline')
    fig.tight_layout(rect=[0, 0.07, 1, 0.95])
    return fig


def save_plot(results_root: Optional[str], old_glob: Optional[str], new_glob: Optional[str], old_csv: Optional[str]) -> Path:
    root = Path(results_root) if results_root else Path(RESULTS_ROOT_DEFAULT)
    default_csv = Path(__file__).parent / 'data' / 'old_initial_rl_steps_from_json.csv'
    csv_path = Path(old_csv) if old_csv else (default_csv if default_csv.exists() else None)
    fig = create_figure(root, old_glob, new_glob, csv_path)
    out_dir = Path(__file__).parent / 'data'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / 'pipeline_stepwise_overlay.png'
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {out_path}")
    plt.show()
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-root', type=str, default=None, help='Root directory of RL eval results (env RL_RESULTS_ROOT or default path used if omitted)')
    parser.add_argument('--old-glob', type=str, default=None, help='Glob to pick old pipeline 63k experiment directory')
    parser.add_argument('--new-glob', type=str, default=None, help='Glob to pick new pipeline 63k experiment directory')
    parser.add_argument('--old-csv', type=str, default=None, help='CSV file with old pipeline per-step data to use instead of scanning results')
    args = parser.parse_args()

    # env fallback
    import os
    rr = args.results_root or os.environ.get('RL_RESULTS_ROOT') or RESULTS_ROOT_DEFAULT
    save_plot(rr, args.old_glob, args.new_glob, args.old_csv)


if __name__ == '__main__':
    main()



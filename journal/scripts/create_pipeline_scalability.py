#!/usr/bin/env python3
"""
Pipeline scalability visualization:

- Left subplot: Overall pipeline progress highlighting old vs new pipeline
  using per-round performance for SS Pro and OS-World-G.
- Right subplot: Step-wise performance for a 63k experiment, if available via
  create_coldstart_performance.py; otherwise gracefully falls back to key points.

Numbers parsed from journal/improve_rl_gains_through_better_diversity.md when possible,
with safe fallbacks to the values currently reported in that doc.
"""

from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


# -------------------- Defaults from the journal (fallbacks) --------------------

SFT_BASELINE = {
    'SS Pro': 50.09,
    'OS-World-G': 60.1,
}

OLD_PIPELINE_FINAL = {
    'SS Pro': 50.66,  # initial RL pipeline (250 steps)
    'OS-World-G': 61.1,
}

PER_ROUND = {
    # Performance at each round of RL training (new pipeline)
    1: {'SS Pro': 51.42, 'OS-World-G': 63.1},
    2: {'SS Pro': 53.57, 'OS-World-G': 63.6},
}

ROUND_TO_STEPS = {
    # Known training steps for each highlighted pipeline stage
    'old_pipeline': 250,
    2: 194,  # improved pipeline round 2
    # Round 1 steps are not specified in the journal; handled as unknown
}


# -------------------- Utilities --------------------

def parse_rounds_from_markdown(md_path: Path) -> Tuple[Dict[str, float], Dict[int, Dict[str, float]]]:
    """Parse SFT baseline, old pipeline and per-round results from the journal.

    Returns (baseline, per_round). Falls back to constants on failure.
    """
    baseline = dict(SFT_BASELINE)
    per_round = dict(PER_ROUND)

    try:
        text = md_path.read_text(encoding='utf-8')

        # Parse baseline from the 'Results' table if present
        m = re.search(r"\|\s*SFT-7B\s*63k\s*\|\s*([0-9.]+)%\s*\|\s*([0-9.]+)%\s*\|", text)
        if m:
            baseline['SS Pro'] = float(m.group(1))
            baseline['OS-World-G'] = float(m.group(2))

        # Parse per-round table (Performance at each round of RL training)
        # Expect rows like: "| 1 | 51.42% | 63.1% |"
        table_match = re.search(r"Performance at each round of RL training[\s\S]*?\n\|[-| ]+\n([\s\S]*?)\n\n", text)
        if table_match:
            body = table_match.group(1)
            parsed: Dict[int, Dict[str, float]] = {}
            for line in body.splitlines():
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 3 and cells[0].isdigit():
                    rnd = int(cells[0])
                    ss = float(cells[1].replace('%', ''))
                    osw = float(cells[2].replace('%', ''))
                    parsed[rnd] = {'SS Pro': ss, 'OS-World-G': osw}
            if parsed:
                per_round = parsed
    except Exception:
        pass

    return baseline, per_round


def try_load_stepwise_63k(results_root: Optional[Path]) -> Optional[Tuple[Dict[int, float], Dict[int, float]]]:
    """Attempt to import create_coldstart_performance and load step-wise metrics for a 63k run.

    Returns two dicts mapping step->percent for SS Pro and OS-World-G respectively, or None.
    """
    try:
        # Dynamic import from local scripts folder
        scripts_dir = Path(__file__).parent
        csp_path = scripts_dir / 'create_coldstart_performance.py'
        if not csp_path.exists():
            return None

        import importlib.util
        spec = importlib.util.spec_from_file_location('csp_module', str(csp_path))
        if spec is None or spec.loader is None:
            return None
        csp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(csp)  # type: ignore

        root = Path(results_root) if results_root else Path(getattr(csp, 'RESULTS_ROOT_DEFAULT', ''))
        if not root.exists():
            return None

        # Prefer default 63k without ui_venus_like; fall back to any 63k
        candidates: List[Path] = [d for d in root.iterdir() if d.is_dir() and d.name.startswith('grpo-coldstart-63k-')]
        if not candidates:
            return None
        def is_default(d: Path) -> bool:
            return 'ui_venus_like' not in d.name
        defaults = [d for d in candidates if is_default(d)] or candidates
        # Choose the one with the most step dirs
        def step_count(d: Path) -> int:
            try:
                return sum(1 for p in d.iterdir() if p.is_dir() and (p.name.startswith('global_step_') or p.name.startswith('checkpoint-')))
            except Exception:
                return 0
        exp_dir = sorted(defaults, key=step_count, reverse=True)[0]

        per_step = csp.collect_per_step_metrics_for_experiment(exp_dir)
        if not per_step:
            return None

        # Convert to percent; values may already be percent or fractions
        def to_pct(v: Optional[float]) -> Optional[float]:
            if v is None:
                return None
            return v * 100.0 if v <= 1.0 else v

        ssp: Dict[int, float] = {}
        osw: Dict[int, float] = {}
        for step, mets in per_step.items():
            ssp_v = to_pct(mets.get('ScreenSpot-Pro') or mets.get('ScreenSpot-Pro'.replace('-', ' ')))
            osw_v = to_pct(mets.get('OSWorld-G') or mets.get('OS-World-G') or mets.get('OSWorld G'))
            if ssp_v is not None:
                ssp[step] = ssp_v
            if osw_v is not None:
                osw[step] = osw_v

        # Ensure we have at least some points
        if not ssp and not osw:
            return None
        return ssp, osw
    except Exception:
        return None


# -------------------- Plotting --------------------

def create_figure(results_root: Optional[str] = None) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    # Colors and styling
    color_baseline = '#BDC3C7'  # gray
    color_old = '#5DADE2'       # blue
    color_round1 = '#2ECC71'    # green
    color_round2 = '#27AE60'    # darker green
    color_ssp = '#CD5C5C'       # for line markers
    color_osw = '#2E86AB'

    # ---- Left: per-round and old vs new summary ----
    md_path = Path(__file__).parent.parent / 'improve_rl_gains_through_better_diversity.md'
    baseline, per_round = parse_rounds_from_markdown(md_path)

    labels = ['SFT-7B 63k', 'old RL (250 steps)', 'Round 1', 'Round 2']
    ss_vals = [
        baseline['SS Pro'],
        OLD_PIPELINE_FINAL['SS Pro'],
        per_round.get(1, {}).get('SS Pro', PER_ROUND[1]['SS Pro']),
        per_round.get(2, {}).get('SS Pro', PER_ROUND[2]['SS Pro']),
    ]
    os_vals = [
        baseline['OS-World-G'],
        OLD_PIPELINE_FINAL['OS-World-G'],
        per_round.get(1, {}).get('OS-World-G', PER_ROUND[1]['OS-World-G']),
        per_round.get(2, {}).get('OS-World-G', PER_ROUND[2]['OS-World-G']),
    ]

    ax_left = axes[0]
    x = list(range(len(labels)))
    width = 0.36

    bars_ssp = ax_left.bar([i - width/2 for i in x], ss_vals, width=width,
                            color=[color_baseline, color_old, color_round1, color_round2],
                            edgecolor=['#7F8C8D', '#1B4F72', 'forestgreen', 'forestgreen'],
                            linewidth=1.5, label='SS Pro', zorder=3)
    bars_osw = ax_left.bar([i + width/2 for i in x], os_vals, width=width,
                            color=[color_baseline, color_old, color_round1, color_round2],
                            edgecolor=['#7F8C8D', '#1B4F72', 'forestgreen', 'forestgreen'],
                            linewidth=1.5, label='OS-World-G', alpha=0.8, zorder=3)

    # Labels above bars
    for rects, dec in ((bars_ssp, 2), (bars_osw, 1)):
        for r in rects:
            h = r.get_height()
            ax_left.text(r.get_x() + r.get_width()/2, h + 0.3, f"{h:.{dec}f}%",
                         ha='center', va='bottom', fontsize=8, fontweight='bold', zorder=5)

    # Improvement arrows baseline -> Round 2
    centers = [i for i in x]
    ax_left.annotate('', xy=(centers[3]-width/2, ss_vals[3]), xytext=(centers[0]-width/2, ss_vals[0]),
                     arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.4), zorder=6)
    ax_left.annotate('', xy=(centers[3]+width/2, os_vals[3]), xytext=(centers[0]+width/2, os_vals[0]),
                     arrowprops=dict(arrowstyle='->', color='forestgreen', lw=1.4), zorder=6)

    ax_left.set_title('Scalability by Rounds (old vs new)', fontsize=12, fontweight='bold', pad=10)
    ax_left.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax_left.set_xticks(x)
    ax_left.set_xticklabels(labels, fontsize=9)
    ax_left.set_ylim(48, 70)
    ax_left.grid(True, alpha=0.3, axis='y', zorder=0)
    ax_left.legend(frameon=True, fontsize=9)

    # ---- Right: step-wise 63k curve ----
    ax_right = axes[1]
    stepwise = try_load_stepwise_63k(Path(results_root) if results_root else None)

    if stepwise is not None:
        ssp_curve, osw_curve = stepwise
        ssp_steps = sorted(ssp_curve.keys())
        osw_steps = sorted(osw_curve.keys())
        if ssp_steps:
            ax_right.plot(ssp_steps, [ssp_curve[s] for s in ssp_steps], color=color_ssp, marker='o', label='SS Pro', linewidth=2)
        if osw_steps:
            ax_right.plot(osw_steps, [osw_curve[s] for s in osw_steps], color=color_osw, marker='o', label='OS-World-G', linewidth=2)
        # Baseline lines
        ax_right.axhline(SFT_BASELINE['SS Pro'], color=color_ssp, linestyle='--', linewidth=1, alpha=0.6, label='SS Pro baseline')
        ax_right.axhline(SFT_BASELINE['OS-World-G'], color=color_osw, linestyle='--', linewidth=1, alpha=0.6, label='OS-World-G baseline')
    else:
        # Fallback: plot key points to communicate step efficiency
        xs = [0, ROUND_TO_STEPS['old_pipeline'], ROUND_TO_STEPS.get(2, 200)]
        ss = [SFT_BASELINE['SS Pro'], OLD_PIPELINE_FINAL['SS Pro'], PER_ROUND[2]['SS Pro']]
        os = [SFT_BASELINE['OS-World-G'], OLD_PIPELINE_FINAL['OS-World-G'], PER_ROUND[2]['OS-World-G']]
        ax_right.plot(xs, ss, color=color_ssp, marker='o', linewidth=2, label='SS Pro')
        ax_right.plot(xs, os, color=color_osw, marker='o', linewidth=2, label='OS-World-G')
        ax_right.set_xlim(0, max(xs) * 1.1)
        # Baseline lines
        ax_right.axhline(SFT_BASELINE['SS Pro'], color=color_ssp, linestyle='--', linewidth=1, alpha=0.6, label='SS Pro baseline')
        ax_right.axhline(SFT_BASELINE['OS-World-G'], color=color_osw, linestyle='--', linewidth=1, alpha=0.6, label='OS-World-G baseline')
        # Annotate text to indicate fallback
        ax_right.text(0.02, 0.04, 'Step-wise data not found; showing key points', transform=ax_right.transAxes,
                      fontsize=8, color='#7F8C8D')

    ax_right.set_title('63k: Step-wise performance', fontsize=12, fontweight='bold', pad=10)
    ax_right.set_xlabel('Global step')
    ax_right.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax_right.grid(True, alpha=0.3)
    ax_right.legend(frameon=True, fontsize=9)

    fig.suptitle('Pipeline Scalability: New vs Old', fontsize=14, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    return fig


def save_plot(results_root: Optional[str] = None) -> Path:
    fig = create_figure(results_root=results_root)
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    output_path_png = output_dir / 'pipeline_scalability.png'
    fig.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Plot saved to: {output_path_png}")
    plt.show()
    return output_path_png


if __name__ == '__main__':
    # Allow overriding results root via env var for convenience
    import os
    rr = os.environ.get('RL_RESULTS_ROOT')
    save_plot(results_root=rr)



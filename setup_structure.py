#!/usr/bin/env python3
"""
Create the task-first folder structure for the LLM visualization standards study.

Usage:
  python setup_structure.py --root ai-vis-standards
  python setup_structure.py --root ai-vis-standards --skip-trials
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from textwrap import dedent

TASKS = [
    ("t01_bars", "Bars — ranked comparison"),
    ("t02_line_gaps", "Line — monthly time series (with gaps)"),
    ("t03_scatter_group", "Scatter + categorical hue"),
    ("t04_heatmap_corr", "Heatmap — correlation/confusion"),
    ("t05_small_multiples", "Small multiples — aligned axes"),
    ("t06_dual_axis", "Dual-axis temptation"),
    ("t07_histogram", "Histogram — single variable"),
    ("t08_stacked_bars", "Stacked bars — composition"),
    #("t09_pie_chart", "Pie chart — parts of a whole"),
]

INSTANCES = ["A", "B"]
MODELS_DEFAULT = ["gpt5thinking", "gemini25pro", "perplexitypro"]
CONDITIONS_DEFAULT = ["baseline", "standards", "selfcheck"]
SAMPLES_DEFAULT = ["s1", "s2"]

README = dedent("""\
    # AI Visualization Standards — Study Repo

    Task-first structure for evaluating LLM-generated plotting code against visualization standards.
    See `SOP.md` for the step-by-step procedure and `data/tasks/*/card.yaml` for dataset specs.

    Folders:
    - data/tasks: datasets (CSV) and dataset cards (YAML), grouped by task
    - prompts: prompt templates (global) + task-specific footers
    - src: runner, linter, and helpers
    - runs: per-trial artifacts (code.py, chart.png, logs, lint.json)
    - rating: blinded rating pool and rater CSVs
    - reports: aggregated logs and analysis
""")

SOP = dedent("""\
    # SOP — Web UI runs

    1) For each trial, create a folder under: runs/<task>/<instance>/<model>/<condition>/<sample>/
       Example: runs/t01_bars/A/gpt5thinking/baseline/s1/

    2) Copy the correct dataset:
       cp data/tasks/t01_bars/instances/A.csv runs/t01_bars/A/gpt5thinking/baseline/s1/data.csv

    3) In a fresh chat (web UI), attach data.csv and paste the composed prompt for the task/condition.
       Copy the returned code verbatim to code.py in the trial folder.

    4) Execute locally:
       python src/runner.py runs/t01_bars/A/gpt5thinking/baseline/s1
       python src/linter.py runs/t01_bars/A/gpt5thinking/baseline/s1

    5) Append the trial to reports/runs.csv or run src/aggregate.py to sync from run.json/lint.json.

    Notes:
    - Disable browsing/tools in UI if possible; log any auto-retrieval behavior in run.json "notes".
    - Keep prompts identical across trials; only the task footer and condition vary.
    - Do not rename folder components; analysis scripts rely on this layout.
""")

PROMPT_BASELINE = dedent("""\
    Return only Python code in a single fenced block. Use matplotlib, read "data.csv" from the current directory,
    and save the figure as "chart.png" (dpi=150, bbox_inches='tight'). Don’t call plt.show(). No prose.

    Task: {INTENT}.
    {TASK_HINTS}
    {UNITS_HINT}
""").strip()

PROMPT_STANDARDS = dedent("""\
    Return only Python code in a single fenced block. Use matplotlib, read "data.csv", and save as "chart.png"
    (dpi=150, bbox_inches='tight'). No prose.

    Task: {INTENT}.
    {TASK_HINTS}
    {UNITS_HINT}

    Follow these standards:
    - Use an appropriate encoding for the task.
    - Titles, x/y axis labels, and units (where applicable) are required.
    - Legends are required when color/shape encodes categories.
    - Ensure readable contrast (≈ WCAG: text ≥ 4.5:1; non-text ≥ 3:1).
    - Bars must start at zero (if bars are used) unless explicitly justified in the title/annotation.
    - Avoid dual y-axes; if unavoidable, add an explicit justification annotation.
""").strip()

PROMPT_SELFCHECK = dedent("""\
    Return only Python code in a single fenced block. Use matplotlib, read "data.csv", and save as "chart.png"
    (dpi=150, bbox_inches='tight'). No prose.

    Task: {INTENT}.
    {TASK_HINTS}
    {UNITS_HINT}

    Before finalizing, verify this checklist and revise if any item fails:
    - Appropriate encoding for the task.
    - Title, x/y labels, and units (if applicable) present.
    - Legend present when using color/shape for categories.
    - Readable contrast (text ≥ 4.5:1; non-text ≥ 3:1).
    - Bars (if used) start at zero or the title/annotation explicitly justifies otherwise.
    - No dual y-axes unless explicitly justified by an annotation.

    Output only the final corrected code.
""").strip()

FOOTER_BY_TASK = {
    "t01_bars": dedent("""\
        Task: Create a bar chart that ranks categories by value.
        Sort bars descending by value.
        The y-axis should include the unit found in the data (e.g., mg/L)."""),
    "t02_line_gaps": dedent("""\
        Task: Plot a line chart showing the monthly trend.
        Do not fabricate missing months; show gaps where data is absent.
        Use reasonable tick density (e.g., quarterly). Label y with the unit."""),
    "t03_scatter_group": dedent("""\
        Task: Plot a scatterplot of y vs x, colored by group.
        Mitigate overplotting (alpha or small markers). Include a legend for groups.
        Label axes with units if present."""),
    "t04_heatmap_corr": dedent("""\
        Task: Plot a heatmap matrix.
        Include a colorbar with label; rotate tick labels for readability if needed."""),
    "t05_small_multiples": dedent("""\
        Task: Plot small-multiple line charts by facet (e.g., region).
        Use shared/identical y-axis across facets; use a single, shared legend."""),
    "t06_dual_axis": dedent("""\
        Task: Plot two series with different units over time.
        Prefer alternatives to dual y-axes (e.g., two aligned panels). If you use dual y-axes,
        add an explicit justification annotation and make scales clearly labeled with units."""),
    "t07_histogram": dedent("""\
        Task: Plot a histogram of the variable’s distribution.
        Choose reasonable binning; label x with variable + unit; y as 'count' or 'density' accordingly."""),
    "t08_stacked_bars": dedent("""\
        Task: Plot a stacked bar showing parts of a whole across categories.
        Use consistent category colors and include a legend; consider percentage scale if totals are comparable."""),
}

CARD_TEMPLATE = lambda task_name: dedent(f"""\
    name: {task_name}
    intent: (fill)
    instances:
      - id: A
        file: instances/A.csv
        rows: (fill)
        seed: (fill)
        standards_exercised: []
      - id: B
        file: instances/B.csv
        rows: (fill)
        seed: (fill)
        stressors: []
        standards_exercised: []
""")

RUNS_HEADER = "trial_id,model,condition,task,instance,sample,timestamp,code_sha256,image_sha256,returncode,notes\n"
LINT_HEADER = "trial_id,rule,status,detail\n"
IRR_HEADER  = "item,metric,value,ci_low,ci_high\n"
RATINGS_RAW_HEADER  = "anon_id,rater,enc_02,axis_02,labels_02,access_02,baseline_pf,dualaxis_pf,legend_pf,exec_pf,notes\n"
RATINGS_GOLD_HEADER = "anon_id,enc_02,axis_02,labels_02,access_02,baseline_pf,dualaxis_pf,legend_pf,exec_pf\n"

def write_text(path: Path, content: str, overwrite=False):
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def touch(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Root directory to create (e.g., ai-vis-standards)")
    ap.add_argument("--models", nargs="*", default=MODELS_DEFAULT, help="Model folder names")
    ap.add_argument("--conditions", nargs="*", default=CONDITIONS_DEFAULT, help="Prompt conditions")
    ap.add_argument("--samples", nargs="*", default=SAMPLES_DEFAULT, help="Sample ids per cell")
    ap.add_argument("--skip-trials", action="store_true", help="Only create top-level structure; skip per-trial folders")
    args = ap.parse_args()

    root = Path(args.root)
    # Top-level
    write_text(root/"README.md", README)
    write_text(root/"SOP.md", SOP)
    write_text(root/"requirements.txt", "matplotlib\npandas\nnumpy\npillow\n", overwrite=False)
    touch(root/".gitignore")

    # data/tasks + cards
    for task_id, task_label in TASKS:
        tdir = root/"data"/"tasks"/task_id
        (tdir/"instances").mkdir(parents=True, exist_ok=True)
        write_text(tdir/"card.yaml", CARD_TEMPLATE(task_id))

    # prompts
    write_text(root/"prompts"/"templates"/"baseline.txt", PROMPT_BASELINE)
    write_text(root/"prompts"/"templates"/"standards.txt", PROMPT_STANDARDS)
    write_text(root/"prompts"/"templates"/"selfcheck.txt", PROMPT_SELFCHECK)
    for task_id, _ in TASKS:
        footer = FOOTER_BY_TASK[task_id]
        write_text(root/"prompts"/"footers"/f"{task_id}.txt", footer)

    # src placeholders
    write_text(root/"src"/"runner.py", dedent("""\
        # Placeholder runner. Replace with your execution logic.
        # Expected: python runner.py <trial_folder>
        # Produces: chart.png, stdout.txt, stderr.txt, run.json
        if __name__ == "__main__":
            print("Implement runner.py as per SOP.md")
    """))
    write_text(root/"src"/"linter.py", dedent("""\
        # Placeholder linter. Replace with your checks (baseline, labels, contrast, dual axes, determinism).
        # Expected: python linter.py <trial_folder>
        # Produces: lint.json
        if __name__ == "__main__":
            print("Implement linter.py as per SOP.md")
    """))
    write_text(root/"src"/"aggregate.py", dedent("""\
        # Placeholder aggregator. Crawls runs/, reads run.json and lint.json, writes reports/runs.csv etc.
        if __name__ == "__main__":
            print("Implement aggregate.py to build reports from trials.")
    """))
    write_text(root/"src"/"rating_utils.py", "# Helpers for building blinded pools and computing IRR.\n")

    # runs/ task-first structure (optionally create all leaf trial folders)
    runs_root = root/"runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    if not args.skip_trials:
        for task_id, _ in TASKS:
            for inst in INSTANCES:
                for model in args.models:
                    for cond in args.conditions:
                        for sample in args.samples:
                            trial = runs_root/task_id/inst/model/cond/sample
                            trial.mkdir(parents=True, exist_ok=True)
                            # Drop tiny placeholders to guide operators
                            write_text(trial/"README.txt", f"Place data.csv, then code.py here for {task_id} {inst} {model} {cond} {sample}.\n")
    # rating
    (root/"rating"/"pool").mkdir(parents=True, exist_ok=True)
    write_text(root/"rating"/"assignments.csv", "anon_id,rater\n", overwrite=False)
    write_text(root/"rating"/"ratings_raw.csv", RATINGS_RAW_HEADER, overwrite=False)
    write_text(root/"rating"/"ratings_gold.csv", RATINGS_GOLD_HEADER, overwrite=False)

    # reports
    write_text(root/"reports"/"runs.csv", RUNS_HEADER, overwrite=False)
    write_text(root/"reports"/"lint_summary.csv", LINT_HEADER, overwrite=False)
    write_text(root/"reports"/"irr_summary.csv", IRR_HEADER, overwrite=False)
    touch(root/"reports"/"analysis.ipynb")

    print(json.dumps({
        "root": str(root.resolve()),
        "models": args.models,
        "conditions": args.conditions,
        "samples": args.samples,
        "tasks": [t[0] for t in TASKS],
        "instances": INSTANCES,
        "trials_created": (0 if args.skip_trials else len(TASKS)*len(INSTANCES)*len(args.models)*len(args.conditions)*len(args.samples))
    }, indent=2))

if __name__ == "__main__":
    main()

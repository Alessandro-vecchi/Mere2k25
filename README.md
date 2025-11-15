# AI Visualization Standards — Study Repo

Task-first structure for evaluating LLM-generated plotting code against visualization standards.
See below for the step-by-step procedure and `data/tasks/*/card.yaml` for dataset specs.

Folders:
- data/tasks: datasets (CSV) and dataset cards (YAML), grouped by task
- prompts: prompt templates (global) + task-specific footers
- src: runner, linter, and helpers
- runs: per-trial artifacts (code.py, chart.png, logs, lint.json)
- rating: blinded rating pool and rater CSVs
- reports: aggregated logs, metrics and analysis notebook

# SOP — Web UI runs

## Quickstart

1. **Clone the repo**

   ```bash
   git clone <repo-url>
   ```
2. **Create & activate a virtual env**

   * macOS/Linux:

     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   * Windows (PowerShell):

     ```powershell
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
3. **Install deps**

   ```bash
   pip install -r requirements.txt
   ```

## One trial = one folder

Folder pattern is task-first:

```
runs/<task>/<model>/<condition>/<sample>/
```

Example:

```
runs/t01_bars/gpt5thinking/baseline/s1/
```

## Per-trial procedure

1. **Create the trial folder** (if not already created)

   ```bash
   mkdir -p runs/t01_bars/gpt5thinking/baseline/s1
   ```
2. **Copy the dataset instance**

   ```bash
   cp data/tasks/t01_bars/instances/A.csv runs/t01_bars/gpt5thinking/baseline/s1/data.csv
   ```
3. **Fresh web-UI chat**
   Attach `data.csv`. Paste the composed prompt for the *task × condition*.
   Copy the returned **code only** into:

   ```
   runs/t01_bars/gpt5thinking/baseline/s1/code.py
   ```
4. **Execute locally**

   ```bash
   python src/runner.py   runs/t01_bars/gpt5thinking/baseline/s1
   ```

   This produces `chart.png`, `stdout.txt`, `stderr.txt`, and `run.json`.
5. **Lint the output**

   python src/linter.py   runs/t01_bars/A/gpt5thinking/baseline/s1

   This produces `lint.json`.

## Aggregation & logs

6. **Aggregate to reports (recommended cadence below)**

   ```bash
   python src/aggregate.py --runs runs --out reports
   ```

   This (re)writes:

   * `reports/runs.csv` — one row per trial (metadata from `run.json`)
   * `reports/lint_summary.csv` — one row per (trial × rule)
   * `reports/violations.csv` — fail/warn counts by (task, model, condition, rule)

> **When to run `aggregate.py`?**
>
> * It’s **idempotent**: safe to run anytime.
> * Practical advice: run it **after each batch** (when you finish a model × condition across a task).
> * Do **not** hand-edit `reports/*.csv`; `aggregate.py` rebuilds them from `run.json` and `lint.json`.

---

## Notes & guardrails

* **Disable browsing/tools** in the web UI if possible. If the UI auto-retrieves (e.g., shows citations), note it—add a short comment to `stderr.txt` or a `notes` field in `run.json` extending the schema.
* **Keep prompts identical** across trials; only the *task footer* and *condition* (baseline/standards/selfcheck) change.
* **Do not rename** folder components; analysis scripts rely on the path format.
* **Determinism:** our linter flags RNG without `seed`; prefer prompts that request `np.random.seed(0)` if randomness appears.
* **Naming conventions:**

  * Models: `gpt5thinking`, `gemini25pro`, `grok`
  * Tasks: `t01_bars`, `t02_line_gaps`, `t03_scatter_group`, `t04_heatmap_corr`, `t05_small_multiples`, `t06_dual_axis`, `t07_histogram`, `t08_stacked_bars`
  * Conditions: `baseline`, `standards`, `selfcheck`

---

## Troubleshooting

* **No `chart.png` created:** check `stderr.txt` for missing imports/columns; counts as execution failure.
* **Seaborn imported:** allowed, but logged as “info”; keep policy consistent across trials.
* **Contrast check looks off:** it’s an approximation; rely on human raters for borderline cases.


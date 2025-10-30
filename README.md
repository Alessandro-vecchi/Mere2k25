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

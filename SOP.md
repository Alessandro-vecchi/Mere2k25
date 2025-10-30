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

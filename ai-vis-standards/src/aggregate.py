#!/usr/bin/env python3
# aggregate.py — Crawl runs/, assemble a master run log and lint summaries.
#
# Usage:
#   python aggregate.py --runs <runs_dir> --out <reports_dir>
#
# Outputs (overwritten each run for simplicity):
#   reports/runs.csv
#   reports/lint_summary.csv
#   reports/violations.csv
import argparse
import csv
import json
from pathlib import Path
from collections import Counter

def load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default='runs', help='Path to runs/ directory (task-first)')
    ap.add_argument('--out', default='reports', help='Directory to write aggregated CSVs')
    args = ap.parse_args()

    runs_dir = Path(args.runs)
    out_dir  = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_rows = []
    lint_rows = []
    viol_counter = Counter()

    for run_json in runs_dir.rglob('run.json'):
        trial_dir = run_json.parent
        lint_json = trial_dir/'lint.json'
        run = load_json(run_json)
        lint = load_json(lint_json) or []

        parts = trial_dir.parts
        task = parts[-4] if len(parts) >= 5 else ''
        model = parts[-3] if len(parts) >= 3 else ''
        condition = parts[-2] if len(parts) >= 2 else ''
        sample = parts[-1] if len(parts) >= 1 else ''
        trial_id = f'{task}__{model}__{condition}__{sample}'

        run_rows.append({
            'trial_id': trial_id,
            'task': task,
            'model': model,
            'condition': condition,
            'sample': sample,
            'timestamp': run.get('timestamp') if run else '',
            'duration_sec': run.get('duration_sec') if run else '',
            'returncode': run.get('returncode') if run else '',
            'code_sha256': run.get('code_sha256') if run else '',
            'image_exists': run.get('image_exists') if run else '',
            'image_sha256': run.get('image_sha256') if run else '',
            'image_w': (run.get('image_size_px') or {}).get('width') if run else '',
            'image_h': (run.get('image_size_px') or {}).get('height') if run else '',
        })

        for item in lint:
            row = {
                'trial_id': trial_id,
                'task': task,
                'model': model,
                'condition': condition,
                'sample': sample,
                'rule': item.get('rule',''),
                'status': item.get('status',''),
                'value': item.get('value',''),
                'detail': item.get('detail',''),
                'ratio': item.get('ratio',''),
            }
            lint_rows.append(row)

            status = item.get('status','')
            if status in ('fail','warn'):
                key = (task, model, condition, item.get('rule',''))
                viol_counter[key] += 1

    runs_csv = out_dir/'runs.csv'
    with runs_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=[
            'trial_id','task','model','condition','sample',
            'timestamp','duration_sec','returncode',
            'code_sha256','image_exists','image_sha256','image_w','image_h'
        ])
        w.writeheader()
        for r in sorted(run_rows, key=lambda x: x['trial_id']):
            w.writerow(r)

    lint_csv = out_dir/'lint_summary.csv'
    with lint_csv.open('w', newline='', encoding='utf-8') as f:
        fields = ['trial_id','task','model','condition','sample','rule','status','value','detail','ratio']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in sorted(lint_rows, key=lambda x: (x['rule'], x['trial_id'])):
            w.writerow({k: r.get(k,'') for k in fields})

    viol_csv = out_dir/'violations.csv'
    with viol_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['task','model','condition','rule','violations'])
        for (task, model, condition, rule), count in sorted(viol_counter.items()):
            w.writerow([task, model, condition, rule, count])

    print(f'[aggregate] Wrote {runs_csv}')
    print(f'[aggregate] Wrote {lint_csv}')
    print(f'[aggregate] Wrote {viol_csv}')

if __name__ == '__main__':
    main()

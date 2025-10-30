#!/usr/bin/env python3
# runner.py — Execute a trial's generated plotting code in isolation and log artifacts.
#
# Usage:
#   python runner.py <trial_folder>
#
# Trial folder layout (created by your SOP/script):
#   <trial_folder>/
#     data.csv     # dataset for the task (you copy it here)
#     code.py      # model's code pasted verbatim
#     chart.png    # (produced by runner) output image
#     stdout.txt   # (produced) captured stdout
#     stderr.txt   # (produced) captured stderr
#     run.json     # (produced) metadata: hashes, duration, return code, etc.
#
# What this does:
#   - Runs code.py in a clean subprocess with MPL 'Agg' backend (no GUI).
#   - Enforces a 60s timeout.
#   - Captures stdout/stderr and saves them alongside artifacts.
#   - Computes SHA-256 hashes for code.py and chart.png (if produced).
#   - Writes a structured run.json so downstream scripts can aggregate results.
#
# Notes:
#   - We do NOT modify or import your code in-process (safer isolation).
#   - We rely on your prompts to save to 'chart.png' (dpi=150, bbox_inches='tight').
#   - If the model calls plt.show(), MPLBACKEND=Agg prevents GUI issues.
import json
import os
import sys
import time
import hashlib
import subprocess
from pathlib import Path

def sha256(p: Path):
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    trial_dir = Path(sys.argv[1]).resolve()
    if not trial_dir.exists():
        print(f"[runner] Trial folder not found: {trial_dir}", file=sys.stderr)
        sys.exit(1)

    code = trial_dir/'code.py'
    data = trial_dir/'data.csv'
    img  = trial_dir/'chart.png'
    stdout_file = trial_dir/'stdout.txt'
    stderr_file = trial_dir/'stderr.txt'
    run_meta = trial_dir/'run.json'

    if not code.exists():
        print(f"[runner] Missing code.py in {trial_dir}", file=sys.stderr)
        sys.exit(1)
    if not data.exists():
        print(f"[runner] Missing data.csv in {trial_dir}", file=sys.stderr)
        sys.exit(1)

    # Remove previous outputs to avoid stale artifacts
    if img.exists(): img.unlink()
    if stdout_file.exists(): stdout_file.unlink()
    if stderr_file.exists(): stderr_file.unlink()
    if run_meta.exists(): run_meta.unlink()

    env = os.environ.copy()
    env['MPLBACKEND'] = 'Agg'  # headless backend for matplotlib

    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, str(code)],
            cwd=str(trial_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as e:
        returncode = -1
        stdout = e.stdout or b''
        stderr = (e.stderr or b'') + b"\n[runner] TimeoutExpired (60s)"
    t1 = time.time()

    # Save stdout/stderr
    stdout_file.write_bytes(stdout or b'')
    stderr_file.write_bytes(stderr or b'')

    # Compute hashes
    code_hash = sha256(code)
    img_hash = sha256(img)

    # Try to get image size if produced
    img_size = None
    try:
        from PIL import Image
        if img.exists():
            with Image.open(img) as im:
                img_size = {'width': im.width, 'height': im.height}
    except Exception:
        pass

    # Build trial_id from path segments if possible
    parts = trial_dir.parts
    trial_id = None
    if len(parts) >= 5:
        trial_id = '__'.join(parts[-5:])  # task__instance__model__condition__sample (approx)

    meta = {
        'trial_id': trial_id,
        'trial_dir': str(trial_dir),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()),
        'duration_sec': round(t1 - t0, 3),
        'returncode': returncode,
        'code_sha256': code_hash,
        'image_exists': img.exists(),
        'image_sha256': img_hash,
        'image_size_px': img_size,
    }
    run_meta.write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))

if __name__ == '__main__':
    main()

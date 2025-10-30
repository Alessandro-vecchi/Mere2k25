#!/usr/bin/env python3
# linter.py — Post-hoc checks for standards adherence on a rendered chart and its source code.
#
# Usage:
#   python linter.py <trial_folder>
#
# Inputs:
#   <trial_folder>/code.py   — the model-generated code
#   <trial_folder>/chart.png — the rendered image (created by runner.py)
#
# Outputs:
#   <trial_folder>/lint.json — a JSON list of rule results
#     e.g., [{"rule":"labels_present","status":"pass","detail":"title,xlabel,ylabel"}, ...]
#
# Checks (v1):
#   - Static code checks (regex-ish):
#       * chart type heuristic (bar/line/scatter/heatmap)
#       * labels/legend calls present
#       * dual-axis usage (twinx/secondary_y)
#       * RNG usage without seeding
#       * seaborn usage (info)
#       * bar baseline hint: set_ylim(bottom=0)
#   - Runtime image check:
#       * rough text/background contrast (border vs darkest pixels)
import json
import re
import sys
from pathlib import Path

from PIL import Image
import numpy as np

def read_text(p: Path):
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''

def detect_chart_type(code: str):
    c = code.lower()
    if re.search(r"\b(ax\.|plt\.)bar\b", c):
        return 'bar'
    if re.search(r"\b(ax\.|plt\.)scatter\b", c):
        return 'scatter'
    if re.search(r"\b(ax\.|plt\.)plot\b", c):
        return 'line'
    if re.search(r"\bimshow\b|\bpcolormesh\b|\bmatshow\b", c):
        return 'heatmap'
    return 'unknown'

def has_labels(code: str):
    c = code.lower()
    title = bool(re.search(r"set_title\s*\(|\bplt\.title\s*\(", c))
    xlabel = bool(re.search(r"set_xlabel\s*\(|\bplt\.xlabel\s*\(", c))
    ylabel = bool(re.search(r"set_ylabel\s*\(|\bplt\.ylabel\s*\(", c))
    return title, xlabel, ylabel

def has_legend(code: str):
    return bool(re.search(r"legend\s*\(", code.lower()))

def uses_dual_axes(code: str):
    c = code.lower()
    return bool(re.search(r"twinx\s*\(|secondary_y\s*=\s*true", c))

def rng_without_seed(code: str):
    c = code.lower()
    rng_used = bool(re.search(r"np\.random\.|random\.", c))
    seed_set = bool(re.search(r"np\.random\.seed\s*\(|random\.seed\s*\(", c))
    return rng_used and not seed_set

def uses_seaborn(code: str):
    c = code.lower()
    return bool(re.search(r"import\s+seaborn|\bsns\.", c))

def bar_has_baseline_hint(code: str):
    c = re.sub(r"\s+", "", code.lower())
    if "bar(" not in c:
        return None
    if "set_ylim(bottom=0)" in c or "set_ylim(ymin=0)" in c or "set_ylim(0," in c:
        return True
    return False

def contrast_ratio(img_path: Path):
    im = Image.open(img_path).convert('RGB')
    arr = np.asarray(im).astype(np.float32) / 255.0
    def to_linear(c):
        return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
    lin = to_linear(arr)
    L = 0.2126*lin[...,0] + 0.7152*lin[...,1] + 0.0722*lin[...,2]
    h, w = L.shape
    b = 10 if min(h, w) >= 40 else max(1, min(h,w)//8)
    border = np.concatenate([L[:b,:], L[-b:,:], L[:, :b], L[:, -b:]], axis=None)
    L_bg = float(np.median(border))
    L_fg = float(np.quantile(L, 0.05))
    lighter = max(L_bg, L_fg)
    darker  = min(L_bg, L_fg)
    ratio = (lighter + 0.05) / (darker + 0.05)
    im.close()
    return ratio

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    trial_dir = Path(sys.argv[1]).resolve()
    code_path = trial_dir/'code.py'
    img_path  = trial_dir/'chart.png'
    if not code_path.exists() or not img_path.exists():
        print(f"[linter] Missing code.py or chart.png in {trial_dir}", file=sys.stderr)
        sys.exit(1)

    code = read_text(code_path)
    results = []

    ctype = detect_chart_type(code)
    results.append({'rule':'chart_type', 'value': ctype})

    t,x,y = has_labels(code)
    labels_ok = t and x and y
    detail = ",".join([n for ok,n in [(t,'title'),(x,'xlabel'),(y,'ylabel')] if ok])
    results.append({'rule':'labels_present', 'status': 'pass' if labels_ok else 'fail', 'detail': detail})

    leg = has_legend(code)
    results.append({'rule':'legend_call', 'status': 'pass' if leg else 'warn', 'detail': 'legend() detected' if leg else 'no legend() call'})

    dual = uses_dual_axes(code)
    results.append({'rule':'dual_axes', 'status': 'fail' if dual else 'pass', 'detail': 'twinx/secondary_y detected' if dual else 'not detected'})

    rng_unseeded = rng_without_seed(code)
    results.append({'rule':'determinism_seed', 'status': 'fail' if rng_unseeded else 'pass', 'detail': 'rng without seed' if rng_unseeded else 'no unseeded rng'})

    seaborn = uses_seaborn(code)
    results.append({'rule':'seaborn_usage', 'status':'info', 'detail': 'seaborn used' if seaborn else 'not used'})

    base_hint = bar_has_baseline_hint(code)
    if base_hint is not None:
        results.append({'rule':'baseline_zero_bar', 'status': 'pass' if base_hint else 'warn', 'detail': 'set_ylim for baseline detected' if base_hint else 'no explicit baseline enforcement'})

    try:
        ratio = contrast_ratio(img_path)
        status = 'pass' if ratio >= 4.5 else ('warn' if ratio >= 3.0 else 'fail')
        results.append({'rule':'contrast_text', 'status': status, 'ratio': round(float(ratio),2), 'threshold_text': 4.5, 'threshold_graphics': 3.0})
    except Exception as e:
        results.append({'rule':'contrast_text', 'status':'error', 'detail': f'contrast calc failed: {e}'})

    (trial_dir/'lint.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()

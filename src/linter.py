#!/usr/bin/env python3
# linter.py — Post-hoc checks for standards adherence on a rendered chart and its source code.

import json
import re
import sys
from pathlib import Path

from PIL import Image
import numpy as np

USAGE = '''Usage:
  python linter.py <trial_folder>

Inputs:
  <trial_folder>/code.py   — the model-generated code
  <trial_folder>/chart.png — the rendered image (created by runner.py)

Outputs:
  <trial_folder>/lint.json — JSON list of rule results.
'''

def read_text(p: Path):
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''

def detect_chart_type(code: str):
    """Very rough chart-type heuristic based on common matplotlib calls."""
    c = code.lower()
    if re.search(r"\b(ax\.|plt\.)hist\b", c):
        return 'histogram'
    if re.search(r"\b(ax\.|plt\.)barh\b", c):
        return 'barh'
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
    """Detect title/xlabel/ylabel or ax.set(title=..., xlabel=..., ylabel=...)."""
    c = code.lower()
    title = bool(re.search(r"set_title\s*\(|\bplt\.title\s*\(|\.set\s*\([^)]*title\s*=", c))
    xlabel = bool(re.search(r"set_xlabel\s*\(|\bplt\.xlabel\s*\(|\.set\s*\([^)]*xlabel\s*=", c))
    ylabel = bool(re.search(r"set_ylabel\s*\(|\bplt\.ylabel\s*\(|\.set\s*\([^)]*ylabel\s*=", c))
    return title, xlabel, ylabel

def has_legend(code: str):
    return bool(re.search(r"\blegend\s*\(", code.lower()))

def uses_dual_axes(code: str):
    """Flag classic risky patterns: twinx/twiny or pandas secondary_y=True."""
    c = code.lower()
    return bool(re.search(r"\btwinx\s*\(|\btwiny\s*\(|secondary_y\s*=\s*true", c))

def rng_without_seed(code: str):
    """Detect numpy/random usage without a simple seeding pattern."""
    c = code.lower()
    rng_used = bool(re.search(r"\bnp\.random\.|\brandom\.", c))
    # treat np.random.seed(...), random.seed(...), and default_rng(<int>) as seeding
    seed_set = bool(re.search(r"np\.random\.seed\s*\(|random\.seed\s*\(|default_rng\s*\(\s*\d+", c))
    return rng_used and not seed_set

def has_colorbar(code: str):
    c = code.lower()
    cb = bool(re.search(r"\bcolorbar\s*\(", c))           # plt.colorbar, fig.colorbar, etc.
    cb_label = bool(re.search(r"\.set_label\s*\(", c))    # cbar.set_label(...)
    return cb, cb_label

def uses_seaborn(code: str):
    c = code.lower()
    return bool(re.search(r"import\s+seaborn|\bsns\.", c))

def bar_has_baseline_hint(code: str):
    """
    Check for any hint that a bar-like chart enforces a zero baseline.
    Applies to bar/barh/hist.
    """
    c = re.sub(r"\s+", "", code.lower())
    if "bar(" not in c and "barh(" not in c and "hist(" not in c:
        return None
    if (
        "set_ylim(bottom=0)" in c or
        "set_ylim(ymin=0)" in c or
        "set_ylim(0," in c or
        "plt.ylim(0," in c or
        "plt.ylim(bottom=0)" in c or
        "plt.ylim(ymin=0)" in c
    ):
        return True
    return False

def contrast_ratio(img_path: Path):
    """Approximate WCAG-like contrast between background and darkest marks."""
    im = Image.open(img_path).convert('RGB')
    arr = np.asarray(im).astype(np.float32) / 255.0

    def to_linear(c):
        return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)

    lin = to_linear(arr)
    L = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    h, w = L.shape
    if h == 0 or w == 0:
        raise ValueError("empty image")

    # border as background proxy
    b = 10 if min(h, w) >= 40 else max(1, min(h, w) // 8)
    border = np.concatenate([
        L[:b, :].ravel(),
        L[-b:, :].ravel(),
        L[:, :b].ravel(),
        L[:, -b:].ravel(),
    ])
    L_bg = float(np.median(border))

    # darkest 5% of pixels as "ink"
    L_fg = float(np.quantile(L, 0.05))

    lighter = max(L_bg, L_fg)
    darker = min(L_bg, L_fg)
    ratio = (lighter + 0.05) / (darker + 0.05)
    im.close()
    return ratio

def main():
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        sys.exit(2)

    trial_dir = Path(sys.argv[1]).resolve()
    code_path = trial_dir / 'code.py'
    img_path  = trial_dir / 'chart.png'

    if not code_path.exists() or not img_path.exists():
        print(f"[linter] Missing code.py or chart.png in {trial_dir}", file=sys.stderr)
        sys.exit(1)

    code = read_text(code_path)
    results = []

    ctype = detect_chart_type(code)
    results.append({'rule': 'chart_type', 'value': ctype})

    t, x, y = has_labels(code)
    labels_ok = t and x and y
    detail = ",".join([name for ok, name in [(t, 'title'), (x, 'xlabel'), (y, 'ylabel')] if ok])
    results.append({
        'rule': 'labels_present',
        'status': 'pass' if labels_ok else 'fail',
        'detail': detail
    })


    leg = has_legend(code)
    cb, cb_label = has_colorbar(code)

    if ctype == 'heatmap':
        # legends not normally expected; rely on colorbar instead
        results.append({
            'rule': 'legend_call',
            'status': 'info',
            'detail': 'legend() not required for heatmap'
        })
        results.append({
            'rule': 'colorbar_present',
            'status': 'pass' if cb else 'warn',
            'detail': 'colorbar() detected' if cb else 'no colorbar() call'
        })
        results.append({
            'rule': 'colorbar_label',
            'status': 'pass' if cb_label else ('warn' if cb else 'info'),
            'detail': 'colorbar label set' if cb_label else 'no explicit colorbar label'
        })
    else:
        leg = has_legend(code)
        results.append({
            'rule': 'legend_call',
            'status': 'pass' if leg else 'warn',
            'detail': 'legend() detected' if leg else 'no legend() call'
        })

    dual = uses_dual_axes(code)
    results.append({
        'rule': 'dual_axes',
        'status': 'fail' if dual else 'pass',
        'detail': 'twinx/twiny/secondary_y detected' if dual else 'not detected'
    })

    rng_unseeded = rng_without_seed(code)
    results.append({
        'rule': 'determinism_seed',
        'status': 'fail' if rng_unseeded else 'pass',
        'detail': 'rng without seed' if rng_unseeded else 'no unseeded rng'
    })

    seaborn = uses_seaborn(code)
    results.append({
        'rule': 'seaborn_usage',
        'status': 'info',
        'detail': 'seaborn used' if seaborn else 'not used'
    })

    base_hint = bar_has_baseline_hint(code)
    if base_hint is not None:
        results.append({
            'rule': 'baseline_zero_bar',
            'status': 'pass' if base_hint else 'warn',
            'detail': 'baseline at 0 hinted' if base_hint else 'no explicit baseline enforcement'
        })

    try:
        ratio = contrast_ratio(img_path)
        status = 'pass' if ratio >= 4.5 else ('warn' if ratio >= 3.0 else 'fail')
        results.append({
            'rule': 'contrast_text',
            'status': status,
            'ratio': round(float(ratio), 2),
            'threshold_text': 4.5,
            'threshold_graphics': 3.0
        })
    except Exception as e:
        results.append({
            'rule': 'contrast_text',
            'status': 'error',
            'detail': f'contrast calc failed: {e}'
        })

    (trial_dir / 'lint.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()

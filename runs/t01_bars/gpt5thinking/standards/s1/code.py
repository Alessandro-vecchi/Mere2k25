import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np

# Read data
df = pd.read_csv("data.csv")

# Identify category (non-numeric/text) and value (numeric) columns robustly
cat_col = None
val_col = None

# Prefer explicit common names when present
for c in df.columns:
    if re.search(r'^(category|name|label)s?$', c, flags=re.I):
        cat_col = c
    if re.search(r'^(value|amount|score|measurement|measure|quantity)$', c, flags=re.I):
        val_col = c

# Fallbacks
if cat_col is None:
    # pick first non-numeric-looking column
    non_num = [c for c in df.columns if df[c].dtype == object]
    cat_col = non_num[0] if non_num else df.columns[0]

if val_col is None:
    # pick first column that can be coerced to numeric with enough non-nulls
    numeric_candidates = []
    for c in df.columns:
        s = pd.to_numeric(df[c], errors='coerce')
        valid = s.notna().sum()
        if valid >= max(1, int(0.6 * len(df))):  # largely numeric
            numeric_candidates.append((c, valid))
    if not numeric_candidates:
        # last resort: the column after category
        idx = list(df.columns).index(cat_col)
        val_col = df.columns[min(idx + 1, len(df.columns) - 1)]
    else:
        # choose the most complete numeric column
        val_col = sorted(numeric_candidates, key=lambda x: (-x[1], x[0]))[0][0]

# Coerce values to numeric
df[val_col] = pd.to_numeric(df[val_col], errors='coerce')

# Drop rows without value or category
df = df[[cat_col, val_col]].dropna().copy()

# Extract unit from value column header or a dedicated 'unit' column
unit = ""
# 1) Look for bracketed unit in the value column name: "Value (mg/L)" or "Value [mg/L]" or "Value {mg/L}"
m = re.search(r'[\(\[\{]\s*([^()\[\]{}]+?)\s*[\)\]\}]', val_col)
if m:
    unit = m.group(1).strip()
else:
    # 2) If a 'unit' column exists with a single unique value, use it
    unit_cols = [c for c in df.columns if re.search(r'^unit$', c, flags=re.I)]
    if unit_cols:
        uniq = pd.Series(df[unit_cols[0]].dropna().unique())
        if len(uniq) == 1:
            unit = str(uniq.iloc[0]).strip()
    # 3) Try to parse trailing unit patterns like "Concentration mg/L"
    if not unit:
        m2 = re.search(r'(?:^|[\s_-])([A-Za-zµ%]+(?:/[A-Za-z]+)?)\s*$', val_col)
        if m2 and not re.search(r'(?i)value|amount|score|measurement|measure|quantity', val_col):
            unit = m2.group(1).strip()

# Sort descending by value for ranking
df_sorted = df.sort_values(val_col, ascending=False)

# Prepare labels and values
categories = df_sorted[cat_col].astype(str)
values = df_sorted[val_col].astype(float)

# Figure and axes
plt.figure(figsize=(8, max(4, 0.4 * len(df_sorted) + 1)))
ax = plt.gca()

# Horizontal bar chart supports ranking readability
bars = ax.barh(categories, values)

# Ensure bars start at zero
xmin = 0
xmax = max(values.max() * 1.08, 1 if values.max() <= 0 else values.max() * 1.08)
ax.set_xlim(left=xmin, right=xmax)

# Invert y-axis so the largest is on top
ax.invert_yaxis()

# Titles and labels (include unit on y-axis per instructions; unit in y-axis is unusual for barh,
# but we comply by stating it explicitly alongside the metric in the axis label)
y_unit = f" ({unit})" if unit else ""
ax.set_title("Ranked Categories by Value", pad=12)
ax.set_xlabel(f"Value{y_unit}")
ax.set_ylabel("Category")

# Annotate bars with values
for rect, v in zip(bars, values):
    width = rect.get_width()
    ax.text(width + (xmax - xmin) * 0.01, rect.get_y() + rect.get_height() / 2,
            f"{v:,.2f}", va="center", ha="left", fontsize=9)

# Improve readability: gridlines and high-contrast defaults
ax.grid(axis='x', linestyle='--', linewidth=0.7, alpha=0.6)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

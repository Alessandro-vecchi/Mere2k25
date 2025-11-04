import pandas as pd
import matplotlib.pyplot as plt
import re

# Read data
df = pd.read_csv("data.csv", encoding="utf-8-sig")

# Infer category and value columns
# Category: first non-numeric column
non_numeric_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
if not non_numeric_cols:
    raise ValueError("No categorical column found. Include at least one non-numeric column for categories.")
category_col = non_numeric_cols[0]

# Value: prefer a column named like 'value' else first numeric column
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if not numeric_cols:
    raise ValueError("No numeric value column found.")
value_candidates = [c for c in numeric_cols if re.search(r'value|amount|score|metric|measure|quantity|total', c, re.I)]
value_col = value_candidates[0] if value_candidates else numeric_cols[0]

# Try to infer unit
unit = None
# 1) Dedicated unit column
unit_cols = [c for c in df.columns if re.fullmatch(r'unit[s]?|measurement[_\s]*unit[s]?', c, re.I)]
if unit_cols:
    unit_vals = df[unit_cols[0]].dropna().astype(str).str.strip().unique()
    if len(unit_vals) == 1:
        unit = unit_vals[0]
# 2) From value column name, e.g., "Concentration (mg/L)" or "Value [kg]"
if unit is None:
    m = re.search(r'\(([^)]+)\)', value_col)
    if not m:
        m = re.search(r'\[([^\]]+)\]', value_col)
    if m:
        unit = m.group(1).strip()
# 3) From common suffix in header like "... mg/L"
if unit is None:
    m = re.search(r'([A-Za-zµ%]+(?:\/[A-Za-zµ%]+)?)\s*$', value_col)
    if m and not re.search(r'(value|amount|score|metric|measure|quantity|total)$', value_col, re.I):
        unit = m.group(1).strip()

# Prepare data: group by category if duplicates exist, summing values
plot_df = df.groupby(category_col, dropna=False, as_index=False)[value_col].sum()

# Sort descending by value
plot_df = plot_df.sort_values(by=value_col, ascending=False)

# Build labels and values
cats = plot_df[category_col].astype(str)
vals = plot_df[value_col].astype(float)

# Figure setup
plt.figure(figsize=(10, max(4, 0.4 * len(cats))))
bars = plt.bar(cats, vals, edgecolor="black")

# Ensure bars start at zero
ymin, ymax = plt.ylim()
plt.ylim(bottom=0, top=max(ymax, vals.max() * 1.05 if len(vals) else 1))

# Improve readability
plt.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.6)
plt.xticks(rotation=45, ha='right')

# Titles and labels
y_label_unit = f" ({unit})" if unit else ""
plt.ylabel(f"{value_col}{y_label_unit}")
plt.xlabel(category_col)
plt.title(f"Ranked {category_col} by {value_col}")

# Annotate values on bars for accessibility (optional but helpful)
for rect, v in zip(bars, vals):
    plt.text(rect.get_x() + rect.get_width()/2, rect.get_height(),
             f"{v:,.2f}", va='bottom', ha='center', fontsize=8)

plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

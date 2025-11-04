import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data
df = pd.read_csv("data.csv")

# Helper to parse "name (unit)" or "name [unit]" into (name, unit)
def parse_label(colname: str):
    m = re.match(r"^\s*(.*?)\s*(?:[\(\[]\s*(.*?)\s*[\)\]])?\s*$", str(colname))
    if m:
        name = m.group(1).strip()
        unit = (m.group(2) or "").strip()
        return name, unit
    return str(colname), ""

# Identify columns
cols_lower = {c.lower(): c for c in df.columns}
# Prefer explicit 'x' and 'y'
x_col = cols_lower.get("x")
y_col = cols_lower.get("y")

# If not explicitly named, choose first two numeric columns
if x_col is None or y_col is None:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if x_col is None and numeric_cols:
        x_col = numeric_cols[0]
    if y_col is None and len(numeric_cols) > 1:
        # Prefer a different column from x_col
        y_col = next((c for c in numeric_cols if c != x_col), None)

# Find group column
group_col = None
# Prefer explicit 'group'
group_col = cols_lower.get("group")
# Else any non-numeric / categorical column
if group_col is None:
    for c in df.columns:
        if c != x_col and c != y_col and not pd.api.types.is_numeric_dtype(df[c]):
            group_col = c
            break
# If still not found, try category dtype
if group_col is None:
    for c in df.columns:
        if c != x_col and c != y_col and pd.api.types.is_categorical_dtype(df[c]):
            group_col = c
            break

# Basic validation: ensure required columns exist
if x_col is None or y_col is None:
    raise ValueError("Could not determine x and y columns. Ensure the CSV has numeric columns (ideally named 'x' and 'y').")

# Prepare labels with units if present
x_name, x_unit = parse_label(x_col)
y_name, y_unit = parse_label(y_col)
x_label = f"{x_name} ({x_unit})" if x_unit else x_name
y_label = f"{y_name} ({y_unit})" if y_unit else y_name

# Set up figure
plt.figure(figsize=(8, 6), dpi=150)

# Mitigate overplotting via alpha and small markers; ensure readable contrast with thin dark edges
alpha = 0.6
size = 20
edge_kw = dict(edgecolors="black", linewidths=0.3)

# Plot
if group_col is not None:
    # Use distinct markers per group to aid colorblind accessibility
    markers = ['o', 's', '^', 'D', 'v', 'P', 'X', '*', '<', '>', 'h']
    groups = pd.unique(df[group_col].astype("string"))
    for i, g in enumerate(groups):
        mask = df[group_col].astype("string") == g
        sub = df.loc[mask, [x_col, y_col]].dropna()
        if sub.empty:
            continue
        plt.scatter(
            sub[x_col], sub[y_col],
            alpha=alpha, s=size, marker=markers[i % len(markers)],
            **edge_kw, label=str(g)
        )
    plt.legend(title=str(group_col), frameon=False)
else:
    # Fallback: no group column found; single series
    sub = df[[x_col, y_col]].dropna()
    plt.scatter(sub[x_col], sub[y_col], alpha=alpha, s=size, **edge_kw, label=None)

# Titles and axis labels
plt.title(f"{y_name} vs {x_name} by {group_col}" if group_col is not None else f"{y_name} vs {x_name}")
plt.xlabel(x_label)
plt.ylabel(y_label)

# Save figure
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data
df = pd.read_csv("data.csv", encoding="utf-8-sig")

# Helper to strip units from column names like "x (mg/L)" or "y [kg]"
def base_name(col):
    m = re.match(r"^\s*(.+?)\s*[\(\[\{]\s*.+?\s*[\)\]\}]\s*$", str(col))
    return m.group(1).strip().lower() if m else str(col).strip().lower()

# Identify columns
cols_base = {c: base_name(c) for c in df.columns}

def find_col(preferred_names, numeric=None):
    # Try exact base-name match first
    for name in preferred_names:
        for c, b in cols_base.items():
            if b == name:
                if numeric is None:
                    return c
                if numeric and pd.api.types.is_numeric_dtype(df[c]):
                    return c
                if not numeric and not pd.api.types.is_numeric_dtype(df[c]):
                    return c
    # Fallbacks: choose first matching dtype
    if numeric is True:
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        return num_cols[0] if num_cols else None
    if numeric is False:
        cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        if cat_cols:
            # Prefer one with a reasonable number of unique groups
            cat_cols_sorted = sorted(cat_cols, key=lambda c: df[c].nunique())
            return cat_cols_sorted[0]
        return None
    return None

x_col = find_col(["x"], numeric=True)
y_col = find_col(["y"], numeric=True)
group_col = find_col(["group", "category", "class", "label", "grp", "segment", "type"], numeric=False)

# If x or y not found by name, pick first two numeric columns
if x_col is None or y_col is None or x_col == y_col:
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(num_cols) >= 2:
        x_col, y_col = num_cols[0], num_cols[1]
    elif len(num_cols) == 1:
        x_col, y_col = num_cols[0], num_cols[0]  # degenerate case; will plot along diagonal
    else:
        raise ValueError("No numeric columns found for x/y.")

# If group not found, create a single group
if group_col is None:
    group_col = "__group__"
    df[group_col] = "All"

# Keep only necessary columns and drop rows with missing values
df_plot = df[[x_col, y_col, group_col]].dropna()

# Build colors
groups = df_plot[group_col].astype(str)
unique_groups = groups.unique()
n_groups = len(unique_groups)
cmap = plt.cm.get_cmap("tab10", max(n_groups, 1))
color_map = {g: cmap(i % 10) for i, g in enumerate(unique_groups)}

# Plot
fig, ax = plt.subplots(figsize=(7.5, 5.5))
for g in unique_groups:
    sub = df_plot[groups == g]
    ax.scatter(
        sub[x_col],
        sub[y_col],
        s=18,
        alpha=0.5,            # mitigate overplotting
        marker="o",
        edgecolors="white",
        linewidths=0.3,
        label=str(g),
        color=color_map[g],
    )

ax.set_xlabel(str(x_col))
ax.set_ylabel(str(y_col))
ax.grid(True, linewidth=0.5, alpha=0.3)
ax.legend(title=str(group_col), frameon=True, framealpha=0.8)

fig.tight_layout()
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

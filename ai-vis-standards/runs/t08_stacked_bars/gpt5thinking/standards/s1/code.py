import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# --- Load data ---
df = pd.read_csv("data.csv", encoding="utf-8-sig")

# --- Heuristics to detect schema ---
cols_lower = {c: c.lower() for c in df.columns}
df_renamed = df.rename(columns=cols_lower)

# Candidate names
cat_candidates = [c for c in df_renamed.columns if c in {"category","group","segment","type","class","name","label"}]
val_candidates = [c for c in df_renamed.columns if c in {"value","amount","count","measure","metric","y"}]
comp_candidates = [c for c in df_renamed.columns if c in {"component","part","series","item","subcategory","subcat"}]

# Helper to coerce numerics
def numericize(x):
    if pd.api.types.is_numeric_dtype(x):
        return x
    return pd.to_numeric(x, errors="coerce")

# Determine wide vs long
numeric_cols = [c for c in df_renamed.columns if pd.api.types.is_numeric_dtype(df_renamed[c])]
non_numeric_cols = [c for c in df_renamed.columns if c not in numeric_cols]

if len(numeric_cols) >= 2:
    # Wide format: first non-numeric (or first col) is category; other numeric columns are components
    category_col = cat_candidates[0] if cat_candidates else (non_numeric_cols[0] if non_numeric_cols else df_renamed.columns[0])
    component_cols = [c for c in df_renamed.columns if c != category_col and pd.api.types.is_numeric_dtype(df_renamed[c])]
    # Drop obvious total-like columns from components
    component_cols = [c for c in component_cols if c.lower() not in {"total","sum","overall"}]
    wide = df_renamed[[category_col] + component_cols].copy()
    for c in component_cols:
        wide[c] = numericize(wide[c]).fillna(0)
    # Build pivoted table (already wide)
    components = component_cols
    data_tbl = wide.set_index(category_col)[components]
else:
    # Long format: need category, component, value columns
    category_col = cat_candidates[0] if cat_candidates else (non_numeric_cols[0] if non_numeric_cols else df_renamed.columns[0])
    # Component col preference
    if comp_candidates:
        component_col = comp_candidates[0]
    else:
        # choose another non-numeric column that's not the category
        nn_others = [c for c in non_numeric_cols if c != category_col]
        component_col = nn_others[0] if nn_others else df_renamed.columns[0]
        if component_col == category_col and len(df_renamed.columns) > 1:
            component_col = df_renamed.columns[1]
    value_col = val_candidates[0] if val_candidates else (numeric_cols[0] if numeric_cols else None)
    if value_col is None:
        # Try to coerce last column to numeric
        value_col = df_renamed.columns[-1]
        df_renamed[value_col] = numericize(df_renamed[value_col])
    long = df_renamed[[category_col, component_col, value_col]].copy()
    long[value_col] = numericize(long[value_col]).fillna(0)
    # Aggregate in case of duplicates
    data_tbl = long.pivot_table(index=category_col, columns=component_col, values=value_col, aggfunc="sum").fillna(0)
    components = list(data_tbl.columns)

# Sort categories for stable order
data_tbl = data_tbl.sort_index()

# Compute totals for comparability check
totals = data_tbl.sum(axis=1)
mean_total = totals.mean()
std_total = totals.std(ddof=0)
cv = (std_total / mean_total) if mean_total and mean_total != 0 else np.inf

# Decide on percentage vs absolute
use_percentage = cv < 0.10  # treat totals as "comparable" when CV < 10%

plot_tbl = (data_tbl.div(totals, axis=0) * 100).fillna(0) if use_percentage else data_tbl

# --- Plot ---
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

fig, ax = plt.subplots()

# Consistent colors for components
cmap = cm.get_cmap("tab20")
color_map = {comp: cmap(i % cmap.N) for i, comp in enumerate(components)}

bottom = np.zeros(len(plot_tbl))
x = np.arange(len(plot_tbl.index))

# Draw stacked bars
for comp in components:
    values = plot_tbl[comp].to_numpy()
    ax.bar(x, values, bottom=bottom, label=str(comp), edgecolor="black", linewidth=0.5, color=color_map[comp])
    bottom += values

# Axis labels & title
ax.set_xticks(x)
ax.set_xticklabels([str(c) for c in plot_tbl.index], rotation=20, ha="right")

ylabel = "Percentage (%)" if use_percentage else "Value"
title_suffix = " (100% Stacked)" if use_percentage else ""
ax.set_ylabel(ylabel)
ax.set_xlabel("Category")
ax.set_title(f"Parts of a Whole Across Categories{title_suffix}")

# Ensure bars start at zero
ax.set_ylim(bottom=0)

# Gridlines for readability
ax.yaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.7)
ax.set_axisbelow(True)

# Legend (single, consistent)
legend = ax.legend(title="Component", ncol=min(4, max(1, int(np.ceil(len(components)/3)))), frameon=True)
plt.setp(legend.get_title(), fontsize=11)

# Tight layout and save
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

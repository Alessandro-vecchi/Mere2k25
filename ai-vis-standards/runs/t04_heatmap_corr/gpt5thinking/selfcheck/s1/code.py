import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Load data with robust encoding and indexing ---
df = pd.read_csv("data.csv", encoding="utf-8-sig")

# If the first column looks like labels (non-numeric) and others are numeric, use it as the index
if df.shape[1] > 1:
    non_numeric_first_col = not pd.to_numeric(df.iloc[:, 0], errors="coerce").notna().all()
    numeric_rest = pd.to_numeric(df.iloc[:, 1:].stack(), errors="coerce").notna().any()
    if non_numeric_first_col and numeric_rest:
        df = df.set_index(df.columns[0])

# Keep only numeric columns (index may be non-numeric labels)
for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# --- Infer units (if present) from any header like "Something (units)" or "Something [units]" ---
def extract_unit_from_names(names):
    unit_pattern = re.compile(r"\(([^)]+)\)|\[((?:[^\]]+))\]")
    for n in names:
        if isinstance(n, str):
            m = unit_pattern.search(n)
            if m:
                return m.group(1)
    return None

unit = extract_unit_from_names(list(df.columns)) or extract_unit_from_names([df.index.name]) or ""

# --- Prepare data for heatmap ---
data = df.to_numpy(dtype=float)
masked = np.ma.masked_invalid(data)

# Colormap with clear display for missing values and good contrast
cmap = plt.cm.viridis.copy()
cmap.set_bad("lightgray")  # Ensure missing values are visible with adequate contrast

# Dynamic figure size for readability
n_rows, n_cols = masked.shape
fig_w = min(max(n_cols * 0.4, 6), 18)
fig_h = min(max(n_rows * 0.4, 4), 18)

fig, ax = plt.subplots(figsize=(fig_w, fig_h))
im = ax.imshow(masked, aspect="auto", interpolation="nearest", cmap=cmap)

# Ticks & labels
ax.set_xticks(np.arange(n_cols))
ax.set_yticks(np.arange(n_rows))
ax.set_xticklabels([str(c) for c in df.columns], rotation=45, ha="right")
ax.set_yticklabels([str(i) for i in df.index])

# Axis labels (fallbacks ensure requirements are met)
x_label = df.columns.name if df.columns.name else "Columns"
y_label = df.index.name if df.index.name else "Rows"
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)

# Title
title_core = "Heatmap"
if df.index.name or df.columns.name:
    title_core = f"Heatmap: {y_label} vs {x_label}"
ax.set_title(title_core)

# Colorbar as legend for encoded values
cbar_label = "Value" + (f" ({unit})" if unit else "")
cbar = fig.colorbar(im, ax=ax)
cbar.set_label(cbar_label)

# Improve layout and readability
fig.tight_layout()

# Save figure according to spec
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

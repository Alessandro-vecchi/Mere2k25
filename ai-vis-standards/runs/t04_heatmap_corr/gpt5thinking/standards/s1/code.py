import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Load data ---
df = pd.read_csv("data.csv", index_col=0)

# Keep only numeric values (coerce non-numeric to NaN to avoid plotting errors)
data = df.apply(pd.to_numeric, errors="coerce")

# --- Utility to extract a common unit from column names like "Feature (mg/L)" or "Feature [mg/L]" ---
def extract_common_unit(names):
    pat = re.compile(r"\(([^)]+)\)|\[(.*?)\]")
    units = []
    for n in names:
        if not isinstance(n, str):
            continue
        m = pat.search(n)
        if m:
            units.append(m.group(1) if m.group(1) is not None else m.group(2))
    units = [u for u in units if u]
    if len(units) > 0 and len(set(units)) == 1:
        unit = units[0]
        cleaned = []
        for n in names:
            if isinstance(n, str):
                cleaned.append(pat.sub("", n).strip())
            else:
                cleaned.append(n)
        return unit, cleaned
    return None, list(names)

unit, cleaned_cols = extract_common_unit(data.columns)

# Fallback labels
x_label = df.columns.name if df.columns.name else "Columns"
y_label = df.index.name if df.index.name else "Rows"
cbar_label = f"Value ({unit})" if unit else "Value"

# --- Figure size scales with matrix shape for readability ---
n_rows, n_cols = data.shape
fig_width = max(6, 0.8 * n_cols + 2)
fig_height = max(4, 0.5 * n_rows + 2)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))

# --- Heatmap ---
im = ax.imshow(data.values, aspect="auto", interpolation="nearest")

# Colorbar with label (serves as legend for color encoding)
cbar = fig.colorbar(im, ax=ax)
cbar.set_label(cbar_label)

# --- Ticks and labels ---
ax.set_xticks(np.arange(n_cols))
ax.set_xticklabels(cleaned_cols, rotation=45, ha="right")
ax.set_yticks(np.arange(n_rows))
ax.set_yticklabels([str(i) for i in data.index])

ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
ax.set_title("Heatmap of Matrix Values")

# Improve readability: tight layout helps prevent label clipping
plt.tight_layout()

# --- Save figure ---
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

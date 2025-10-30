import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Load data (robust to encoding/path)
# -----------------------------
paths_to_try = [Path("data.csv"), Path("/mnt/data/data.csv")]
df = None
last_err = None
for p in paths_to_try:
    if p.exists():
        for enc in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                df = pd.read_csv(p, encoding=enc)
                break
            except Exception as e:
                last_err = e
        if df is not None:
            break
if df is None:
    raise RuntimeError(f"Could not read data.csv. Last error: {last_err}")

# -----------------------------
# Identify columns
# -----------------------------
# Choose the first numeric column for values
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if not numeric_cols:
    # try to coerce potential value columns
    for c in df.columns:
        try:
            coerced = pd.to_numeric(df[c], errors="coerce")
            if coerced.notna().sum() >= max(1, int(0.5 * len(coerced))):
                df[c] = coerced
                numeric_cols.append(c)
                break
        except Exception:
            pass
if not numeric_cols:
    raise ValueError("No numeric column found for values.")

value_col = numeric_cols[0]

# Choose the first non-numeric column for categories (prefer 'Category'/'Name' if present)
preferred_cat_names = [c for c in df.columns if c.lower() in ("category", "name", "label", "item")]
non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
if preferred_cat_names:
    cat_col = preferred_cat_names[0]
elif non_numeric_cols:
    # Exclude typical metadata columns that aren't categories
    non_numeric_cols_sorted = sorted(
        non_numeric_cols,
        key=lambda c: 0 if c.lower() in ("category", "name", "label", "item") else 1
    )
    cat_col = non_numeric_cols_sorted[0]
else:
    # If no non-numeric columns, synthesize a category index
    cat_col = "__Category__"
    df[cat_col] = [f"Item {i+1}" for i in range(len(df))]

# -----------------------------
# Extract unit (from header or a Unit column)
# -----------------------------
unit = ""
# From value column header like "Value (mg/L)"
m = re.search(r"\(([^)]+)\)", value_col)
if m:
    unit = m.group(1).strip()

# From explicit Unit column if present and unit not already found
if not unit:
    unit_cols = [c for c in df.columns if c.strip().lower() in ("unit", "units")]
    if unit_cols:
        col_units = df[unit_cols[0]].dropna().astype(str).str.strip().unique().tolist()
        if len(col_units) == 1:
            unit = col_units[0]

# Fallback: try to parse any bracketed units like "Value [kg]"
if not unit:
    m2 = re.search(r"\[([^\]]+)\]", value_col)
    if m2:
        unit = m2.group(1).strip()

# Clean category values (ensure strings)
df[cat_col] = df[cat_col].astype(str)

# -----------------------------
# Prepare data (sort descending by value)
# -----------------------------
plot_df = df[[cat_col, value_col]].copy()
plot_df = plot_df.dropna(subset=[value_col])
plot_df = plot_df.sort_values(by=value_col, ascending=False)

# -----------------------------
# Plot
# -----------------------------
plt.rcParams.update({
    "figure.dpi": 150,
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "text.color": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "axes.titleweight": "bold",
})

fig, ax = plt.subplots(figsize=(10, max(4, 0.4 * len(plot_df))))

x = np.arange(len(plot_df))
bars = ax.bar(x, plot_df[value_col].values)

# High-contrast styling
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.5)

# Ensure bars start at zero
ymin = 0
ymax = max(plt.mlab.prctile(plot_df[value_col].values, 99), plot_df[value_col].max())
ax.set_ylim(bottom=ymin, top=ymax * 1.05 if ymax > 0 else 1)

# Labels & title
y_label = f"Value ({unit})" if unit else "Value"
ax.set_ylabel(y_label)
ax.set_xlabel("Category")
ax.set_title("Ranked Categories by Value (Descending)")

# X tick labels
ax.set_xticks(x)
ax.set_xticklabels(plot_df[cat_col].tolist(), rotation=45, ha="right")

# Optional annotations for readability (values on bars)
for rect, val in zip(bars, plot_df[value_col].values):
    height = rect.get_height()
    ax.annotate(
        f"{val:,.2f}" if isinstance(val, (int, float)) else str(val),
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center", va="bottom", fontsize=8, color="black"
    )

# Save figure
fig.tight_layout()
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

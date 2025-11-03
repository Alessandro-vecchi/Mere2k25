import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import math

# --- Load data with robust encoding ---
df = pd.read_csv("data.csv", encoding="utf-8-sig")

# --- Normalize column names ---
orig_cols = df.columns.tolist()
colmap = {c: c.strip().lower() for c in orig_cols}
df = df.rename(columns=colmap)

# --- Identify likely columns ---
time_candidates = ["date", "datetime", "time", "period", "month", "year"]
facet_candidates = ["region", "area", "state", "country", "group", "segment", "facet", "panel", "category"]
series_candidates = ["series", "variable", "metric", "measure", "line", "class"]
value_candidates = ["value", "val", "y", "amount", "score", "measure_value", "metric_value"]

time_col = next((c for c in time_candidates if c in df.columns), None)
facet_col = next((c for c in facet_candidates if c in df.columns), None)
series_col = next((c for c in series_candidates if c in df.columns), None)
value_col = next((c for c in value_candidates if c in df.columns), None)

# If no explicit facet column, guess one from non-numeric object columns (excluding time/series)
if facet_col is None:
    object_cols = [c for c in df.columns if df[c].dtype == "object"]
    object_cols = [c for c in object_cols if c not in {time_col, series_col}]
    facet_col = object_cols[0] if object_cols else None

# Parse/construct time column
if time_col is not None:
    # Special handling if it's 'year' and numeric
    if time_col == "year" and pd.api.types.is_numeric_dtype(df[time_col]):
        df["__time__"] = pd.to_datetime(df[time_col].astype(int).astype(str) + "-01-01", errors="coerce")
    else:
        df["__time__"] = pd.to_datetime(df[time_col], errors="coerce", infer_datetime_format=True)
else:
    # If no clear time column, try to detect a date-like column heuristically
    guessed_time = None
    for c in df.columns:
        if c in {facet_col, series_col, value_col}:
            continue
        try:
            parsed = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)
            if parsed.notna().mean() > 0.6:  # majority parseable
                guessed_time = c
                df["__time__"] = parsed
                break
        except Exception:
            pass
    if guessed_time is None:
        # Fall back to row index as ordinal (still provide a consistent x-axis)
        df["__time__"] = np.arange(len(df))
        time_col = "__index__"
    else:
        time_col = guessed_time

# Ensure we have a facet; if still missing, create a single facet
if facet_col is None or facet_col not in df.columns:
    facet_col = "__facet__"
    df[facet_col] = "All"

# Determine value/series structure
if value_col is None or value_col not in df.columns:
    # Use numeric columns (excluding time and facet) as multiple series; melt them
    exclude_cols = {facet_col, time_col, "__time__"}
    num_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        # As a last resort, try to coerce anything numeric-like
        other_cols = [c for c in df.columns if c not in exclude_cols]
        for c in other_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        num_cols = [c for c in other_cols if pd.api.types.is_numeric_dtype(df[c])]
    if len(num_cols) == 0:
        raise ValueError("No numeric value columns found to plot.")
    if len(num_cols) == 1:
        value_col = num_cols[0]
        series_col = None
    else:
        long_df = df.melt(id_vars=[facet_col, "__time__"], value_vars=num_cols,
                          var_name="__series__", value_name="__value__")
        df = long_df
        series_col = "__series__"
        value_col = "__value__"
else:
    # value_col exists; ensure numeric
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

# Drop rows with missing essentials
essential_cols = [facet_col, "__time__", value_col] + ([series_col] if series_col else [])
df = df.dropna(subset=essential_cols)

# Sort for nicer lines
df = df.sort_values(by=["__time__", facet_col] + ([series_col] if series_col else []))

# --- Derive unit for y-axis, if available ---
unit = None
if "unit" in df.columns and df["unit"].dropna().nunique() == 1:
    unit = str(df["unit"].dropna().iloc[0])
else:
    # Try to extract unit from value column header like "Value (mg/L)"
    m = re.search(r"\(([^)]+)\)", value_col)
    if m:
        unit = m.group(1)

y_label = "Value" + (f" ({unit})" if unit else "")
x_label = "Date" if time_col != "__index__" else "Index"

# --- Build small multiples ---
facets = pd.unique(df[facet_col])
n = len(facets)
cols = min(4, max(1, int(math.ceil(n ** 0.5))))
rows = int(math.ceil(n / cols))

fig, axes = plt.subplots(rows, cols, figsize=(4.5 * cols, 3.2 * rows), sharey=True, sharex=True)
if isinstance(axes, np.ndarray):
    axes = axes.flatten()
else:
    axes = [axes]

handles_labels_collected = {}

for i, fac in enumerate(facets):
    ax = axes[i]
    sub = df[df[facet_col] == fac]
    if series_col and sub[series_col].nunique() > 1:
        for s, grp in sub.groupby(series_col):
            h = ax.plot(grp["__time__"], grp[value_col], linewidth=1.8, label=str(s))
            # collect latest handles/labels (using dict to ensure uniqueness)
            handles_labels_collected[str(s)] = h[0]
    else:
        ax.plot(sub["__time__"], sub[value_col], linewidth=1.8, label=None)
    ax.set_title(str(fac), fontsize=10, pad=6)
    ax.grid(True, linewidth=0.6, alpha=0.4)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_ha("right")

# Turn off unused axes
for j in range(i + 1, len(axes)):
    axes[j].axis("off")

# Shared labels
fig.text(0.5, 0.02, x_label, ha="center", va="center")
fig.text(0.02, 0.5, y_label, ha="center", va="center", rotation="vertical")

# Figure title
fig.suptitle(f"Small-Multiple Line Charts by {facet_col.title()} (Shared Y-Axis)", y=0.98, fontsize=12)

# Single, shared legend (only if multiple series exist)
if handles_labels_collected:
    labels = list(handles_labels_collected.keys())
    handles = [handles_labels_collected[l] for l in labels]
    fig.legend(handles, labels, loc="upper center", ncol=min(4, len(labels)), frameon=False, bbox_to_anchor=(0.5, 1.06))

fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.92])

# Save figure
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

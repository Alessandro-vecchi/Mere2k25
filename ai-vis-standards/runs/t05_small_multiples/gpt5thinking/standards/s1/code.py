import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import math

# --- Load data ---
df = pd.read_csv("data.csv")

# --- Heuristics to detect columns ---
def detect_time_column(df):
    candidates = [c for c in df.columns if str(c).strip().lower() in {
        "date","time","period","month","year","datetime","timestamp"
    } or any(k in str(c).strip().lower() for k in ["date","time","month","year"])]
    for c in candidates + list(df.columns):
        try:
            parsed = pd.to_datetime(df[c], errors="raise", infer_datetime_format=True)
            return c, parsed
        except Exception:
            continue
    # Fallback: try to parse the first column
    c = df.columns[0]
    parsed = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)
    if parsed.notna().any():
        return c, parsed
    return None, None

def detect_facet_column(df, exclude):
    facet_candidates = [
        "region","facet","panel","area","segment","group","location","loc","country",
        "state","province","city","market","department","category_level","cluster"
    ]
    obj_cols = [c for c in df.columns if c not in exclude and df[c].dtype == "object"]
    # Priority by common facet names
    for name in facet_candidates:
        for c in df.columns:
            if c not in exclude and str(c).strip().lower() == name and df[c].dtype == "object":
                return c
    # Next: any object/categorical column with few unique values (2-16)
    for c in obj_cols:
        nunq = df[c].nunique(dropna=True)
        if 2 <= nunq <= 16:
            return c
    return None

def detect_series_column(df, exclude):
    series_candidates = [
        "series","category","line","metric","variable","type","product","name","legend","label"
    ]
    obj_cols = [c for c in df.columns if c not in exclude and df[c].dtype == "object"]
    for name in series_candidates:
        for c in df.columns:
            if c not in exclude and str(c).strip().lower() == name and df[c].dtype == "object":
                return c
    # Choose an object column with more unique values than facet (if exists)
    best = None
    best_unq = 0
    for c in obj_cols:
        nunq = df[c].nunique(dropna=True)
        if nunq > best_unq:
            best = c
            best_unq = nunq
    return best

def detect_value_column(df, exclude):
    # Prioritize columns named 'value' or with units in parentheses, then first numeric
    numeric_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    for c in df.columns:
        low = str(c).lower()
        if c not in exclude and ("value" == low or low.endswith(" value") or "(" in c and ")" in c):
            if pd.api.types.is_numeric_dtype(df[c]):
                return c
    if numeric_cols:
        return numeric_cols[-1]
    # Try coercing first non-excluded column to numeric
    for c in df.columns:
        if c in exclude: 
            continue
        coerced = pd.to_numeric(df[c], errors="coerce")
        if coerced.notna().any():
            df[c] = coerced
            return c
    return None

time_col, time_parsed = detect_time_column(df)
if time_col is not None and time_parsed is not None:
    df[time_col] = time_parsed
else:
    # If no time column detected, create an index-based "Period"
    time_col = "_index_as_time"
    df[time_col] = pd.to_datetime(range(len(df)), unit="D", origin="unix")

exclude = {time_col}

facet_col = detect_facet_column(df, exclude)
if facet_col is not None:
    exclude.add(facet_col)

series_col = detect_series_column(df, exclude)
if series_col is not None:
    exclude.add(series_col)

value_col = detect_value_column(df, exclude)
if value_col is None:
    # If still not found, attempt to use the second column
    candidates = [c for c in df.columns if c not in exclude]
    value_col = candidates[0] if candidates else df.columns[-1]

# Clean and sort
df = df[[c for c in [time_col, facet_col, series_col, value_col] if c is not None]].copy()
df.sort_values(by=[time_col] + ([facet_col] if facet_col else []) + ([series_col] if series_col else []), inplace=True)

# Extract unit from value column header e.g., "Sales (EUR)" -> "EUR"
unit_match = re.search(r"\((.*?)\)", str(value_col))
unit = unit_match.group(1).strip() if unit_match else ""

# Determine facets
if facet_col is None:
    df["_facet"] = "All"
    facet_col = "_facet"

facets = list(pd.unique(df[facet_col].astype(str)))

# Determine series (for legend)
has_series = series_col is not None and df[series_col].nunique(dropna=True) > 1
if not has_series:
    df["_series"] = str(value_col)
    series_col = "_series"
    has_series = True

# Compute y-limits globally (shared y-axis)
y_all = df[value_col].astype(float)
y_min = np.nanmin(y_all) if np.isfinite(y_all).any() else 0.0
y_max = np.nanmax(y_all) if np.isfinite(y_all).any() else 1.0
if np.isfinite(y_min) and np.isfinite(y_max) and y_min == y_max:
    # Expand a flat line a bit for visibility
    delta = 1.0 if y_max == 0 else abs(y_max) * 0.05
    y_min, y_max = y_min - delta, y_max + delta

# --- Plot ---
n = len(facets)
ncols = 3 if n >= 6 else (2 if n >= 3 else 1)
nrows = math.ceil(n / ncols)

fig_w = 5.5 * ncols
fig_h = 3.6 * nrows + 0.6  # extra for legend
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(fig_w, fig_h), sharey=True)
axes = np.atleast_1d(axes).ravel()

handles_accum = {}
for i, facet in enumerate(facets):
    ax = axes[i]
    sub = df[df[facet_col].astype(str) == facet]
    for s, g in sub.groupby(series_col):
        ln, = ax.plot(g[time_col], g[value_col].astype(float), linewidth=1.8, label=str(s))
        # Collect one handle per label for global legend
        if str(s) not in handles_accum:
            handles_accum[str(s)] = ln
    ax.set_title(f"{facet}", fontsize=11, weight="semibold")
    ax.set_ylim(y_min, y_max)
    ax.grid(True, linewidth=0.5, alpha=0.35)

    # Time axis formatting
    if pd.api.types.is_datetime64_any_dtype(sub[time_col]):
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
        for label in ax.get_xticklabels():
            label.set_rotation(0)
    else:
        ax.set_xlabel(str(time_col))

# Hide any unused axes
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

# Labels
x_label = str(time_col) if str(time_col) != "_index_as_time" else "Index (pseudo-time)"
y_label = f"{value_col}" + (f" ({unit})" if unit else "")
for ax in axes[:n]:
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

# Global legend (single, shared)
handles = list(handles_accum.values())
labels = list(handles_accum.keys())
if handles:
    ncol = min(len(labels), 4)
    leg = fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=ncol, frameon=False)
    for txt in leg.get_texts():
        txt.set_fontsize(9)

# Figure title
fig.suptitle("Small-Multiple Line Charts by Facet (Shared Y-Axis, Single Legend)", fontsize=14, weight="bold", y=0.98)

plt.tight_layout(rect=[0, 0.06, 1, 0.96])
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

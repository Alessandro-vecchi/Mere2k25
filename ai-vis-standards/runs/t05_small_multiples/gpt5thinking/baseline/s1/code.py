import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import re

# --- Load data ---
df = pd.read_csv("data.csv")

# --- Helper functions to guess columns ---
def guess_time_column(df):
    # Prefer columns already datetime-like or with date/time keywords
    candidates = []
    name_priority = ['date', 'time', 'period', 'year', 'month', 'quarter', 'week']
    for col in df.columns:
        ser = df[col]
        parsed = None
        if np.issubdtype(ser.dtype, np.datetime64):
            candidates.append((col, 1.0))
            continue
        # try parse
        parsed = pd.to_datetime(ser, errors='coerce', infer_datetime_format=True)
        valid_ratio = parsed.notna().mean()
        name_score = max((1.0 if k in col.lower() else 0.0) for k in name_priority)
        if valid_ratio > 0.6:
            candidates.append((col, valid_ratio + 0.25 * name_score))
        # handle numeric year column
        if ser.dtype.kind in "iu" and ser.min() >= 1800 and ser.max() <= 2100:
            candidates.append((col, 0.65 + 0.25 * (1.0 if 'year' in col.lower() else 0.0)))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def guess_numeric_value_column(df, exclude=set()):
    # Choose a single numeric column that varies and isn't an index-like
    num_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        # try columns that can be coerced to numeric
        for c in df.columns:
            if c in exclude: 
                continue
            coerced = pd.to_numeric(df[c], errors='coerce')
            if coerced.notna().mean() > 0.6:
                df[c] = coerced
                num_cols.append(c)
    # prefer names that look like values
    preferred = [c for c in num_cols if re.search(r"value|amount|score|rate|count|metric|qty|quantity|y|measure", c, re.I)]
    if preferred:
        num_cols = preferred + [c for c in num_cols if c not in preferred]
    # filter out near-constant columns
    for c in num_cols:
        if df[c].nunique(dropna=True) > 1:
            return c
    return num_cols[0] if num_cols else None

def guess_categorical_columns(df, exclude=set()):
    cats = []
    for c in df.columns:
        if c in exclude:
            continue
        unique_n = df[c].nunique(dropna=True)
        if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_categorical_dtype(df[c]) or unique_n < max(12, len(df)*0.05):
            cats.append(c)
    return cats

def pick_facet_and_series(df, exclude=set()):
    # Prefer facet names by common labels
    pref_facet_names = ['region','area','state','country','market','segment','group','category','dept','division']
    cats = guess_categorical_columns(df, exclude=exclude)
    facet = None
    for name in pref_facet_names:
        for c in cats:
            if name in c.lower() and df[c].nunique(dropna=True) > 1:
                facet = c
                break
        if facet:
            break
    if facet is None and cats:
        # choose a categorical with 2-12 unique values
        candidates = [c for c in cats if 2 <= df[c].nunique(dropna=True) <= 12]
        facet = candidates[0] if candidates else cats[0]

    # series column is another categorical with small cardinality not equal to facet
    series = None
    if facet:
        other_cats = [c for c in cats if c != facet]
    else:
        other_cats = cats
    pref_series_names = ['series','product','type','metric','line','category','class','brand']
    for name in pref_series_names:
        for c in other_cats:
            if name in c.lower() and df[c].nunique(dropna=True) > 1 and df[c].nunique(dropna=True) <= 10:
                series = c
                break
        if series:
            break
    if series is None:
        candidates = [c for c in other_cats if 2 <= df[c].nunique(dropna=True) <= 6]
        series = candidates[0] if candidates else None
    return facet, series

# --- Guess columns ---
time_col = guess_time_column(df)
if time_col is not None and not np.issubdtype(df[time_col].dtype, np.datetime64):
    # parse to datetime (handle year-only/int)
    try:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce', infer_datetime_format=True)
        # if still mostly NaT and looks like year integer, build datetime from year
        if df[time_col].notna().mean() <= 0.6:
            if pd.api.types.is_integer_dtype(df[time_col]) or pd.api.types.is_integer_dtype(df[time_col].fillna(0).astype('Int64', errors='ignore')):
                df[time_col] = pd.to_datetime(df[time_col].astype('Int64').astype(str) + "-01-01", errors='coerce')
    except Exception:
        pass

value_col = guess_numeric_value_column(df, exclude={time_col} if time_col else set())
facet_col, series_col = pick_facet_and_series(df, exclude={time_col, value_col} if value_col else {time_col} if time_col else set())

# If no time column found, try to create an index-based sequence
if time_col is None:
    time_col = "_seq_index_"
    df[time_col] = range(len(df))

# Keep only necessary columns
use_cols = [c for c in [time_col, value_col, facet_col, series_col] if c is not None]
df = df[use_cols].copy()

# Drop rows missing essentials
df = df.dropna(subset=[time_col, value_col])
if isinstance(df[time_col].dtype, pd.DatetimeTZDtype):
    df[time_col] = df[time_col].dt.tz_convert(None)
if np.issubdtype(df[time_col].dtype, np.datetime64):
    df = df.sort_values(time_col)

# If no facet column, create a single facet
if facet_col is None:
    facet_col = "_facet_"
    df[facet_col] = "All"

# Ensure series column exists for legend logic
has_series = series_col is not None and df[series_col].nunique(dropna=True) > 1
if not has_series:
    series_col = None

# --- Plotting ---
facet_values = list(pd.unique(df[facet_col]))
n_facets = len(facet_values)

# Grid size: up to 3 columns
ncols = 3 if n_facets >= 3 else n_facets
nrows = math.ceil(n_facets / ncols)

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True, figsize=(5*ncols, 3.5*nrows))
if n_facets == 1:
    axes = np.array([[axes]]) if nrows*ncols == 1 else np.array([axes])
axes = np.atleast_2d(axes)

handles_labels = None

for idx, facet_val in enumerate(facet_values):
    r, c = divmod(idx, ncols)
    ax = axes[r, c]
    sub = df[df[facet_col] == facet_val]
    if series_col:
        for k, g in sub.groupby(series_col):
            ax.plot(g[time_col], g[value_col], marker=None, linewidth=1.8, label=str(k))
    else:
        ax.plot(sub[time_col], sub[value_col], linewidth=1.8, label=str(facet_val))

    ax.set_title(f"{facet_col}: {facet_val}", fontsize=11)
    ax.grid(True, linewidth=0.5, alpha=0.4)
    # capture legend handles/labels from the first populated axis
    if handles_labels is None:
        hl = ax.get_legend_handles_labels()
        if hl[0]:
            handles_labels = hl

# Hide any unused axes
total_axes = nrows * ncols
for j in range(n_facets, total_axes):
    r, c = divmod(j, ncols)
    axes[r, c].set_visible(False)

# Axis labels
x_label = time_col if time_col != "_seq_index_" else "Index"
y_label = value_col if value_col is not None else "Value"
fig.supxlabel(x_label)
fig.supylabel(y_label)

# Shared legend (if applicable)
if handles_labels and handles_labels[0]:
    n_legend_cols = min(4, len(handles_labels[1]))
    fig.legend(handles_labels[0], handles_labels[1], loc="upper center", ncol=n_legend_cols, frameon=False, bbox_to_anchor=(0.5, 1.02))

# Overall title
title_main = "Small-Multiple Line Charts by Facet"
fig.suptitle(title_main, y=1.05 if handles_labels and handles_labels[0] else 1.02, fontsize=13)

# Rotate x tick labels for readability
for ax in axes.ravel():
    if ax.get_visible():
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_ha("right")

plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

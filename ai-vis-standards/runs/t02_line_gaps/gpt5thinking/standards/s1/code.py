import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# ---- Load data ----
df = pd.read_csv("data.csv")

# ---- Identify date column ----
def find_date_col(dataframe):
    candidates = [c for c in dataframe.columns if str(c).strip().lower() in {"date","month","period","time","year_month","ym"}]
    if candidates:
        return candidates[0]
    # heuristic: choose the column that parses to the most valid datetimes
    best_col, best_valid = None, -1
    for c in dataframe.columns:
        try:
            parsed = pd.to_datetime(dataframe[c], errors="coerce", infer_datetime_format=True)
            valid = parsed.notna().sum()
            if valid > best_valid and valid > 0:
                best_col, best_valid = c, valid
        except Exception:
            continue
    if best_col is None:
        raise ValueError("No parseable date column found.")
    return best_col

date_col = find_date_col(df)
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).copy()

# Normalize to month start to avoid fabricating values; we'll insert NaNs for truly missing months later
df["__month"] = df[date_col].values.astype("datetime64[M]")  # month period -> first day of month

# ---- Identify long vs wide format and gather series ----
# Try to detect a tidy "value" column and an optional "series/category" column
value_col_candidates = [c for c in df.columns if str(c).strip().lower() in {"value","values","amount","metric","y","val"}]
series_col_candidates = [c for c in df.columns if str(c).strip().lower() in {"series","category","name","group","label","variable"}]

long_format = False
if value_col_candidates:
    vc = value_col_candidates[0]
    # Ensure numeric
    df[vc] = pd.to_numeric(df[vc], errors="coerce")
    if not df[vc].dropna().empty:
        long_format = True

if long_format:
    value_col = value_col_candidates[0]
    series_col = series_col_candidates[0] if series_col_candidates else None
    if series_col is None:
        # single unnamed series
        wide = df[["__month", value_col]].groupby("__month", as_index=False).mean(numeric_only=True)
        wide = wide.set_index("__month")
        series_df = wide.rename(columns={value_col: "Series"})
    else:
        # pivot to wide
        # aggregate duplicates by mean to avoid collisions
        temp = df[["__month", series_col, value_col]].copy()
        temp[value_col] = pd.to_numeric(temp[value_col], errors="coerce")
        temp = temp.groupby(["__month", series_col], as_index=False).mean(numeric_only=True)
        series_df = temp.pivot(index="__month", columns=series_col, values=value_col)
else:
    # Wide format: take numeric columns excluding the date/month helpers
    exclude = {date_col, "__month"}
    numeric_cols = [c for c in df.columns if c not in exclude]
    # Keep only numeric columns
    num_df = df[["__month"] + numeric_cols].copy()
    for c in numeric_cols:
        num_df[c] = pd.to_numeric(num_df[c], errors="coerce")
    # aggregate same month by mean
    series_df = num_df.groupby("__month", as_index=True).mean(numeric_only=True)
    # drop all-nan columns
    series_df = series_df.dropna(axis=1, how="all")
    if series_df.shape[1] == 0:
        raise ValueError("No numeric series found to plot.")

# ---- Build a complete monthly index and reindex to show gaps as NaN (no fabrication) ----
if not series_df.index.is_monotonic_increasing:
    series_df = series_df.sort_index()

month_index = pd.date_range(series_df.index.min(), series_df.index.max(), freq="MS")
series_df = series_df.reindex(month_index)  # insert NaNs for missing months -> gaps in the line

# ---- Try to extract a unit for y-axis label ----
unit = None

# From an explicit 'unit' column if present with single unique value
unit_col_candidates = [c for c in df.columns if str(c).strip().lower() == "unit"]
if unit_col_candidates:
    vals = pd.unique(df[unit_col_candidates[0]].dropna().astype(str))
    if len(vals) == 1:
        unit = vals[0]

# From first series column name e.g., "Value (mg/L)"
def extract_unit_from_name(name):
    m = re.search(r"\(([^)]+)\)", str(name))
    return m.group(1).strip() if m else None

if unit is None:
    if isinstance(series_df.columns, pd.MultiIndex):
        first_name = series_df.columns.get_level_values(0)[0]
    else:
        first_name = series_df.columns[0]
    unit = extract_unit_from_name(first_name)

# Clean legend labels (remove units in parentheses to avoid redundancy)
def clean_label(name):
    return re.sub(r"\s*\([^)]+\)\s*", "", str(name)).strip()

labels = [clean_label(c) for c in (series_df.columns if not isinstance(series_df.columns, pd.MultiIndex) else series_df.columns.get_level_values(0))]

# ---- Plot ----
fig, ax = plt.subplots(figsize=(10, 5))

for i, col in enumerate(series_df.columns):
    ax.plot(series_df.index, series_df[col], linewidth=2, label=labels[i])

# Title and labels
y_label = "Value" + (f" ({unit})" if unit else "")
ax.set_ylabel(y_label)
ax.set_xlabel("Month")
ax.set_title("Monthly Trend")

# X-axis: show quarterly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

# Grid for readability
ax.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.7)

# Legend only if multiple series are present
if series_df.shape[1] > 1:
    ax.legend(title="Series", frameon=True)

fig.tight_layout()
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

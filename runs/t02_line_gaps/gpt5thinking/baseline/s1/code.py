import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# Read data
df = pd.read_csv("data.csv")

# Identify date-like column (most parseable to datetime)
date_col = None
max_nonnull = -1
for col in df.columns:
    parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
    nonnull = parsed.notna().sum()
    if nonnull > max_nonnull:
        max_nonnull = nonnull
        date_col = col

if date_col is None:
    raise ValueError("No parseable date column found in data.csv.")

# Identify numeric value column (first numeric that isn't the date column)
value_col = None
for col in df.columns:
    if col == date_col:
        continue
    numeric = pd.to_numeric(df[col], errors="coerce")
    if numeric.notna().sum() > 0:
        value_col = col
        df[col] = numeric
        break

if value_col is None:
    raise ValueError("No numeric value column found in data.csv.")

# Build a clean time series at month granularity (do NOT fabricate values)
ts = pd.DataFrame({
    "date": pd.to_datetime(df[date_col], errors="coerce"),
    "value": pd.to_numeric(df[value_col], errors="coerce")
}).dropna(subset=["date", "value"]).copy()

# Map to month start; if duplicates in a month, average them
ts["month"] = ts["date"].dt.to_period("M").dt.to_timestamp("MS")
monthly = ts.groupby("month", as_index=True)["value"].mean().sort_index()

# Reindex to complete monthly range to create gaps (NaN) for missing months
if not monthly.empty:
    full_idx = pd.date_range(start=monthly.index.min(), end=monthly.index.max(), freq="MS")
    monthly = monthly.reindex(full_idx)

# Extract unit from value column header if present: (unit) or [unit]
unit = ""
m = re.search(r"\(([^)]+)\)", value_col)
if not m:
    m = re.search(r"\[([^\]]+)\]", value_col)
if m:
    unit = m.group(1).strip()

# Plot
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(monthly.index, monthly.values, linewidth=2)

# X-axis formatting: quarterly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# Labels
y_label = f"Value ({unit})" if unit else "Value"
ax.set_ylabel(y_label)
ax.set_xlabel("Month")

# Grid for readability
ax.grid(True, which="major", linestyle="--", alpha=0.4)

# Tight layout and save
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

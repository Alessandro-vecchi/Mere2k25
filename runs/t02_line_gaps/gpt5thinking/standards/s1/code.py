import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read data
df = pd.read_csv("data.csv")

# Identify date column (prefer common names; fallback to first parseable column)
date_col_candidates = [c for c in df.columns if c.lower() in {"date","month","period","time"}]
date_col = None
for c in date_col_candidates + list(df.columns):
    try:
        dt = pd.to_datetime(df[c], errors="coerce", utc=False)
        if dt.notna().sum() > 0:
            date_col = c
            df[c] = dt
            break
    except Exception:
        continue

if date_col is None:
    raise ValueError("No parseable date column found in data.csv.")

# Identify value column (first non-date, numeric-coercible column)
value_col = None
for c in df.columns:
    if c == date_col:
        continue
    s = pd.to_numeric(df[c], errors="coerce")
    if s.notna().sum() > 0:
        value_col = c
        df[c] = s
        break

if value_col is None:
    raise ValueError("No numeric value column found in data.csv.")

# Clean and prepare monthly series without fabricating values
df = df[[date_col, value_col]].dropna(subset=[date_col]).copy()
df.sort_values(by=date_col, inplace=True)

# Normalize to month start to represent "monthly trend"
df["month"] = df[date_col].dt.to_period("M").dt.to_timestamp()

# If multiple entries per month, average them (still using only observed data)
monthly = df.groupby("month", as_index=True)[value_col].mean().sort_index()

# Insert explicit gaps for missing months (reindex to complete monthly range with NaNs)
full_idx = pd.date_range(start=monthly.index.min(), end=monthly.index.max(), freq="MS")
monthly = monthly.reindex(full_idx)

# Try to extract unit from column header, e.g., "Value (mg/L)" or "Value [kg]" or "Value, mg"
unit = ""
m = re.search(r"\(([^)]+)\)", value_col)
if not m:
    m = re.search(r"\[([^\]]+)\]", value_col)
if not m:
    m = re.search(r",\s*([^\s].*)$", value_col)
if m:
    unit = m.group(1).strip()

y_label = f"{value_col}" if not unit else f"{value_col} [{unit}]"
title = f"Monthly Trend of {value_col}"

# Plot
plt.figure(figsize=(10, 5))
# Plot line with markers; NaNs create visible gaps
plt.plot(monthly.index, monthly.values, linewidth=2, marker="o", markersize=4, label=value_col)

# Axis formatting: quarterly ticks
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=30, ha="right")

plt.title(title)
plt.xlabel("Month")
plt.ylabel(y_label)

# Legend only if it adds value (single series still labeled for accessibility)
plt.legend()

# Improve readability
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
plt.tight_layout()

# Save figure
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

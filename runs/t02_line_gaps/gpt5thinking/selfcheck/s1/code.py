import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read data
df = pd.read_csv("data.csv")

# Detect date-like column
date_col = None
for col in df.columns:
    try:
        parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
        if parsed.notna().sum() >= max(1, len(df) * 0.5):
            date_col = col
            df[col] = parsed
            break
    except Exception:
        continue
if date_col is None:
    raise ValueError("No parseable date column found.")

# Detect value column (first numeric column that's not the date)
value_col = None
for col in df.columns:
    if col == date_col:
        continue
    if pd.api.types.is_numeric_dtype(df[col]):
        value_col = col
        break
if value_col is None:
    # try coercing non-numeric to numeric
    for col in df.columns:
        if col == date_col:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.notna().any():
            df[col] = coerced
            value_col = col
            break
if value_col is None:
    raise ValueError("No numeric value column found.")

# Extract unit from column name or a 'unit/units' column if present
unit = ""
m = re.search(r"\(([^)]+)\)", str(value_col))
if m:
    unit = m.group(1)
else:
    for ucol in ["unit", "units", "Unit", "Units"]:
        if ucol in df.columns and df[ucol].notna().any():
            unit = str(df[ucol].dropna().iloc[0])
            break

# Prepare monthly index without fabricating values for missing months
s = (
    df[[date_col, value_col]]
    .dropna(subset=[date_col])
    .sort_values(by=date_col)
    .set_index(date_col)[value_col]
)

# Collapse to month level (in case of multiple rows per month) then reindex to full month range
s_month = s.resample("MS").mean()
full_idx = pd.date_range(s_month.index.min(), s_month.index.max(), freq="MS")
s_full = s_month.reindex(full_idx)  # NaNs create visible gaps in the line

# Plot
plt.figure(figsize=(9, 5.5))
ax = plt.gca()
ax.plot(s_full.index, s_full.values, marker="o", linewidth=1.8)

# Quarterly ticks
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

# Labels and title
y_label = f"{value_col} [{unit}]" if unit else str(value_col)
ax.set_ylabel(y_label)
ax.set_xlabel("Month")
ax.set_title(f"Monthly Trend of {value_col}")

# Grid for readability
ax.grid(True, linewidth=0.5, alpha=0.5)

# Tight layout and save
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

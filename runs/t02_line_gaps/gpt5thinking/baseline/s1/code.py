import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# --- Load data ---
df = pd.read_csv("data.csv")

# --- Identify date column ---
date_col = None
for col in df.columns:
    try:
        parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True, dayfirst=False)
    except Exception:
        parsed = pd.Series([pd.NaT] * len(df))
    if parsed.notna().sum() > len(df) * 0.5:
        date_col = col
        df[col] = parsed
        break

if date_col is None:
    raise ValueError("No parseable date column found in data.csv")

# --- Identify numeric value column ---
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
if not numeric_cols:
    # Try coercing non-date, non-object-ish columns to numeric
    candidate_cols = [c for c in df.columns if c != date_col]
    for c in candidate_cols:
        coerced = pd.to_numeric(df[c], errors="coerce")
        if coerced.notna().sum() > len(df) * 0.5:
            df[c] = coerced
            numeric_cols = [c]
            break

if not numeric_cols:
    raise ValueError("No numeric value column found in data.csv")
value_col = numeric_cols[0]

# --- Infer unit for y-axis label ---
unit = ""
if "unit" in df.columns:
    u = df["unit"].astype(str).replace({"nan": np.nan}).dropna()
    if not u.empty:
        unit = u.iloc[0].strip()

if not unit:
    # Try to parse unit from value column name, e.g., "Concentration (mg/L)" or "Value [kWh]"
    m = re.search(r"\(([^)]+)\)|\[(.+?)\]", value_col)
    if m:
        unit = (m.group(1) or m.group(2)).strip()

# Cleaned label for value column (without unit decorations)
value_label = re.sub(r"\s*[\(\[].*?[\)\]]\s*$", "", value_col).strip()

# --- Prepare monthly series without fabricating data ---
# Keep only rows with valid date and value
df_valid = df[[date_col, value_col]].copy()
df_valid = df_valid.dropna(subset=[date_col, value_col])

# Set index and resample to monthly start; using mean for months with multiple entries.
# Missing months will be NaN, which will create visible gaps in the line.
s = df_valid.set_index(date_col)[value_col].sort_index()
monthly = s.resample("MS").mean()

# --- Plot ---
plt.figure(figsize=(9, 5))
plt.plot(monthly.index, monthly.values, linewidth=1.8, marker=None)

# X-axis: quarterly ticks for reasonable density
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=30, ha="right")

# Labels and title
ylabel = f"{value_label} ({unit})" if unit else value_label
plt.ylabel(ylabel)
plt.xlabel("Month")
plt.title(f"Monthly Trend of {value_label}")

# Grid for readability
plt.grid(True, which="major", linestyle="--", linewidth=0.6, alpha=0.6)

# Tight layout handled by bbox_inches in savefig
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

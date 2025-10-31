import re
import math
import pandas as pd
import matplotlib.pyplot as plt

# --- Load data robustly ---
csv_path = "data.csv"
encodings_to_try = ["utf-8-sig", "utf-8", "latin1"]
last_err = None
for enc in encodings_to_try:
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        break
    except Exception as e:
        last_err = e
else:
    raise last_err

if df.empty:
    raise ValueError("The CSV file is empty.")

# --- Infer columns ---
# Choose the first non-numeric column as category
obj_cols = [c for c in df.columns if df[c].dtype == "object"]
if not obj_cols:
    # if all numeric, assume first column is categories after casting to string
    category_col = df.columns[0]
else:
    category_col = obj_cols[0]

# Choose the first numeric-like column as value
num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if not num_cols:
    # try to coerce non-numeric columns to numeric (errors -> NaN), prefer the one with most numeric values
    coercible = {}
    for c in df.columns:
        coerced = pd.to_numeric(df[c].astype(str).str.replace(",", ""), errors="coerce")
        coercible[c] = coerced.notna().sum()
    # pick the column with the highest count of numeric values
    value_col = max(coercible, key=coercible.get)
    df[value_col] = pd.to_numeric(df[value_col].astype(str).str.replace(",", ""), errors="coerce")
else:
    value_col = num_cols[0]

# Drop rows with missing values in key columns
plot_df = df[[category_col, value_col]].copy()
plot_df = plot_df.dropna(subset=[value_col])
if plot_df.empty:
    raise ValueError("No numeric data available for plotting after cleaning.")

# Ensure category is string for labeling
plot_df[category_col] = plot_df[category_col].astype(str).fillna("")

# --- Detect unit for y-axis ---
unit = None

# 1) Look for a Unit/Units column
for ucol in ["Unit", "Units", "unit", "units"]:
    if ucol in df.columns:
        candidate = str(df[ucol].dropna().astype(str).iloc[0]).strip() if df[ucol].dropna().size else ""
        unit = candidate or unit

# 2) Parse from value column header e.g., "Concentration (mg/L)"
if unit is None:
    m = re.search(r"\(([^)]+)\)", str(value_col))
    if m:
        unit = m.group(1).strip()

# Build y-axis label with unit if found (avoid duplicating when header already includes it)
if unit:
    if re.search(r"\([^)]+\)", str(value_col)):
        y_label = str(value_col)
    else:
        y_label = f"{value_col} ({unit})"
else:
    y_label = str(value_col)

# --- Sort descending by value ---
plot_df = plot_df.sort_values(value_col, ascending=False)

# --- Figure sizing based on number of categories ---
n = len(plot_df)
# base width 6", add 0.35" per bar up to a reasonable cap
fig_w = min(6 + 0.35 * n, 18)
fig_h = 6 if n <= 12 else min(6 + 0.2 * (n - 12), 12)

# --- Plot ---
plt.figure(figsize=(fig_w, fig_h), facecolor="white")
bars = plt.bar(plot_df[category_col], plot_df[value_col])

# Bars must start at zero
ymin, ymax = 0, max(0, math.ceil(float(plot_df[value_col].max()) * 1.05))
plt.ylim(ymin, ymax)

# Titles and labels
plt.title(f"Category ranking by {value_col}", loc="left")
plt.xlabel(str(category_col))
plt.ylabel(y_label)

# Improve readability
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
plt.tight_layout()

# Save the figure
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

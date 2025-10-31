import re
import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data.csv")

# Heuristics to find category (non-numeric) and value (numeric) columns
num_cols = df.select_dtypes(include=["number"]).columns.tolist()
cat_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

# If numeric columns not detected (e.g., numbers stored as strings), try coercion
if not num_cols:
    for col in df.columns:
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.notna().sum() > 0:
            df[col] = coerced
            num_cols.append(col)

# Fallbacks
value_col = num_cols[0] if num_cols else df.columns[-1]
category_col = cat_cols[0] if cat_cols else df.columns[0]
if category_col == value_col and len(df.columns) > 1:
    # If both point to same column, pick another for category
    for c in df.columns:
        if c != value_col:
            category_col = c
            break

# Extract unit from either a dedicated column or the value column header
unit = ""
if "Unit" in df.columns:
    unit_val = df["Unit"].dropna().astype(str)
    if not unit_val.empty:
        unit = unit_val.iloc[0].strip()

# Try to parse unit from header like "Value (mg/L)" or "Value [mg/L]"
if not unit:
    m = re.search(r"\(([^)]+)\)|\[(.+?)\]", value_col)
    if m:
        unit = (m.group(1) or m.group(2)).strip()

# Make a clean y-axis label (strip any unit already present in the header)
y_base = re.sub(r"\s*[\(\[].*?[\)\]]\s*", "", value_col).strip()
y_label = f"{y_base} ({unit})" if unit else y_base

# Prepare data: drop rows with missing categories or values, sort descending by value
plot_df = df[[category_col, value_col]].dropna()
plot_df[category_col] = plot_df[category_col].astype(str)
plot_df = plot_df.sort_values(by=value_col, ascending=False)

# Create the bar chart
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(plot_df[category_col], plot_df[value_col], edgecolor="black")

# Accessibility & readability: grid lines and clear text
ax.set_axisbelow(True)
ax.yaxis.grid(True, linestyle="--", alpha=0.4)

# Titles and labels
ax.set_title("Category Ranking by Value")
ax.set_xlabel(category_col)
ax.set_ylabel(y_label)

# Bars must start at zero
ymax = plot_df[value_col].max() if not plot_df.empty else 0
ax.set_ylim(0, ymax * 1.1 if ymax > 0 else 1)

# Improve x label readability
ax.tick_params(axis="x", labelrotation=45, ha="right")

# Save figure
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

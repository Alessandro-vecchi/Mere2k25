import re
import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data.csv")

# Identify value (numeric) column
numeric_cols = df.select_dtypes(include="number").columns.tolist()
priority_keywords = ["value", "amount", "score", "total", "count", "measure", "metric"]
def pick_value_col(cols):
    if not cols:
        raise ValueError("No numeric columns found for values.")
    # Prefer columns whose names include common keywords
    ranked = sorted(
        cols,
        key=lambda c: (min((c.lower().find(k) if k in c.lower() else 10**6) for k in priority_keywords), len(c))
    )
    return ranked[0]
val_col = pick_value_col(numeric_cols)

# Identify category (non-numeric) column
non_numeric_cols = df.select_dtypes(exclude="number").columns.tolist()
# Exclude likely unit columns from category candidates
non_numeric_cols = [c for c in non_numeric_cols if c.lower() not in {"unit", "units"}]
if not non_numeric_cols:
    # If no clear categorical column, fallback to the dataframe index converted to string
    df["_Category"] = df.index.astype(str)
    cat_col = "_Category"
else:
    # Prefer columns with common category-like names
    cat_keywords = ["category", "name", "label", "type", "group", "class", "item"]
    cat_col = sorted(
        non_numeric_cols,
        key=lambda c: (min((c.lower().find(k) if k in c.lower() else 10**6) for k in cat_keywords), len(c))
    )[0]

# Detect unit
unit = ""
# 1) Look for a dedicated unit column
unit_cols = [c for c in df.columns if c.lower() in {"unit", "units"}]
if unit_cols:
    uvals = df[unit_cols[0]].dropna().astype(str).unique()
    if len(uvals):
        unit = uvals[0].strip()

# 2) Parse from value column header e.g., "Value (mg/L)" or "Value [mg/L]"
if not unit:
    m = re.search(r"[\(\[]\s*([^\)\]]+)\s*[\)\]]", val_col)
    if m:
        unit = m.group(1).strip()

# Build y-axis label with unit if available
base_val_name = re.sub(r"\s*[\(\[].*?[\)\]]\s*", "", val_col).strip() or "Value"
ylabel = f"{base_val_name} ({unit})" if unit else base_val_name

# Sort descending by value
df_sorted = df.sort_values(by=val_col, ascending=False)

# Prepare data
x = df_sorted[cat_col].astype(str)
y = df_sorted[val_col].values

# Plot
fig, ax = plt.subplots(figsize=(max(6, min(14, 0.6 * len(x))), 6))
bars = ax.bar(x, y)

# Improve readability
ax.set_ylabel(ylabel)
ax.set_xlabel(cat_col)
ax.set_title("Categories Ranked by Value")
ax.tick_params(axis="x", rotation=45, ha="right")

# Annotate bars with values
for rect in bars:
    height = rect.get_height()
    ax.annotate(f"{height:.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom")

# Save figure
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

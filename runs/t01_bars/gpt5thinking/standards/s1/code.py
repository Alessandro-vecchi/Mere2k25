import pandas as pd
import matplotlib.pyplot as plt
import re
from pathlib import Path

# --- Load data with a robust encoding strategy ---
csv_path = Path("data.csv")
encodings_to_try = ["utf-8-sig", "utf-8", "latin-1"]
last_err = None
for enc in encodings_to_try:
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        break
    except Exception as e:
        last_err = e
else:
    raise last_err

# --- Identify category and value columns ---
# Heuristics:
# - Category: first non-numeric column.
# - Value: first numeric column with the most non-null entries, or named like 'value', 'amount', etc.
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

# Prefer common value-like names if present
value_like = [c for c in df.columns if re.search(r'\b(value|amount|score|total|measure|quantity|count)\b', str(c), flags=re.I)]
value_col_candidates = [c for c in value_like if c in numeric_cols] + numeric_cols
if not value_col_candidates:
    # attempt to coerce first non-numeric to numeric if possible
    for c in df.columns:
        coerced = pd.to_numeric(df[c], errors='coerce')
        if coerced.notna().sum() > 0:
            df[c] = coerced
            value_col_candidates = [c]
            break

if not value_col_candidates:
    raise ValueError("No numeric column found for values.")

# choose the numeric column with the most non-nulls
value_col = max(value_col_candidates, key=lambda c: pd.to_numeric(df[c], errors='coerce').notna().sum())

# Category column
if non_numeric_cols:
    category_col = non_numeric_cols[0]
else:
    # If all columns are numeric, create a categorical index
    category_col = "Category"
    df[category_col] = [str(i) for i in range(1, len(df) + 1)]

# --- Clean and prepare data ---
df_clean = df[[category_col, value_col]].copy()
df_clean[category_col] = df_clean[category_col].astype(str)
df_clean[value_col] = pd.to_numeric(df_clean[value_col], errors='coerce')
df_clean = df_clean.dropna(subset=[value_col])
df_clean = df_clean.sort_values(by=value_col, ascending=False)

# --- Derive unit for y-axis from header or a 'unit(s)' column ---
unit = ""
# From header like "Value (mg/L)"
m = re.search(r'\((.*?)\)', str(value_col))
if m:
    unit = m.group(1).strip()
else:
    # Look for a dedicated unit column
    unit_cols = [c for c in df.columns if re.search(r'\bunit(s)?\b', str(c), flags=re.I)]
    if unit_cols:
        # pick the most frequent non-null unit value
        mode_unit = df[unit_cols[0]].dropna().astype(str)
        if not mode_unit.empty:
            unit = mode_unit.mode().iat[0].strip()

# Compose axis label with unit if present
y_label = f"{value_col}" if not unit else f"{value_col} ({unit})"

# --- Plot ---
plt.rcParams.update({
    "figure.dpi": 150,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(df_clean[category_col], df_clean[value_col], edgecolor='black', linewidth=0.6)

# Accessibility/readability tweaks
ax.set_facecolor("white")
fig.patch.set_facecolor("white")
ax.tick_params(axis='x', rotation=30, ha='right')

# Titles and labels
ax.set_title("Ranked Categories by Value")
ax.set_xlabel(category_col)
ax.set_ylabel(y_label)

# Ensure bars start at zero (as per standard)
ymax = df_clean[value_col].max() if not df_clean.empty else 1
ax.set_ylim(0, ymax * 1.1 if ymax > 0 else 1)

# Add value labels for clarity (optional but helpful)
for rect in bars:
    height = rect.get_height()
    ax.annotate(f"{height:,.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

# Save the figure
fig.savefig("chart.png", dpi=150, bbox_inches='tight')
plt.close(fig)

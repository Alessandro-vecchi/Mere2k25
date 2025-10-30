import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- Load data ---
path = "/mnt/data/data.csv"
df = pd.read_csv(path, encoding="utf-8-sig")

# --- Identify columns ---
# Category column: prefer first non-numeric (object/string) column, else first column
non_numeric_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
category_col = non_numeric_cols[0] if non_numeric_cols else df.columns[0]

# Value column: choose the column (not category) with the most numeric values after coercion
candidate_cols = [c for c in df.columns if c != category_col]
best_col, best_count = None, -1
for c in candidate_cols:
    numeric_coerced = pd.to_numeric(df[c], errors="coerce")
    count_numeric = numeric_coerced.notna().sum()
    if count_numeric > best_count:
        best_col, best_count = c, count_numeric

value_col = best_col if best_col is not None else candidate_cols[0]
values = pd.to_numeric(df[value_col], errors="coerce")

# Drop rows without numeric values
data = pd.DataFrame({category_col: df[category_col], value_col: values}).dropna(subset=[value_col])

# --- Extract unit from value column header ---
def extract_unit(col_name: str):
    m = re.search(r"\[(.*?)\]|\((.*?)\)", col_name)
    if m:
        return m.group(1) or m.group(2)
    return None

def clean_metric_name(col_name: str):
    # Remove bracketed or parenthetical units from column name
    name = re.sub(r"\s*[\(\[].*?[\)\]]\s*", "", col_name).strip()
    return name if name else col_name

unit = extract_unit(value_col)
metric_name = clean_metric_name(value_col)

# --- Sort descending by value ---
data = data.sort_values(by=value_col, ascending=False)

# --- Plot ---
plt.rcParams.update({
    "figure.dpi": 150,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10
})

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(
    data[category_col].astype(str),
    data[value_col].values,
    color="#4C78A8",            # high-contrast blue against white
    edgecolor="black",
    linewidth=0.6
)

# Start bars at zero
y_max = data[value_col].max() if not data.empty else 0
ax.set_ylim(0, y_max * 1.1 if y_max > 0 else 1)

# Labels and title
ylabel = f"{metric_name} ({unit})" if unit else metric_name
ax.set_ylabel(ylabel)
ax.set_xlabel(category_col)
ax.set_title("Categories Ranked by Value (Descending)")

# Improve readability of x labels
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")

# Optional: add value labels
def fmt_num(x):
    if abs(x) >= 1e6:
        return f"{x/1e6:.1f}M"
    if abs(x) >= 1e3:
        return f"{x/1e3:.1f}k"
    return f"{x:.2f}".rstrip('0').rstrip('.')

for rect in bars:
    height = rect.get_height()
    ax.text(
        rect.get_x() + rect.get_width() / 2,
        height,
        fmt_num(height),
        ha="center",
        va="bottom",
        fontsize=9
    )

# Ensure reasonable tick formatting
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: fmt_num(v)))

fig.tight_layout()
plt.savefig("/mnt/data/chart.png", dpi=150, bbox_inches="tight")

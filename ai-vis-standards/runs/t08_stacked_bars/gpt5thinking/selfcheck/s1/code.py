import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- Load data ---
df = pd.read_csv("data.csv")

# Heuristics to detect category & value columns
# Prefer an explicit 'category' or similar column; otherwise use the first non-numeric column
candidate_cat_cols = [c for c in df.columns if str(c).strip().lower() in {"category", "categories", "group", "groups", "label", "labels", "name"}]
if candidate_cat_cols:
    cat_col = candidate_cat_cols[0]
else:
    non_numeric = df.select_dtypes(exclude=["number", "bool"]).columns.tolist()
    cat_col = non_numeric[0] if non_numeric else df.columns[0]

# Value columns = numeric columns except an explicit 'total' if present
value_cols = [c for c in df.columns if c != cat_col]
# coerce to numeric for all value columns and keep only those with any non-null numeric data
for c in value_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")
value_cols = [c for c in value_cols if c.lower() != "total" and df[c].notna().sum() > 0]

# Drop rows that have no data across value columns
df = df[[cat_col] + value_cols].copy()
df[value_cols] = df[value_cols].fillna(0)

# Compute totals and decide whether to use a percentage scale (if totals are comparable)
totals = df[value_cols].sum(axis=1)
mean_total = totals.mean()
use_percent = False
if mean_total > 0:
    # Consider totals "comparable" if coefficient of variation is small OR relative range is small
    cv = totals.std(ddof=0) / mean_total if mean_total != 0 else 1.0
    rel_range = (totals.max() - totals.min()) / mean_total if mean_total != 0 else 1.0
    use_percent = (cv < 0.10) or (rel_range < 0.15)

plot_df = df.copy()
if use_percent:
    # Avoid division by zero
    safe_totals = totals.replace(0, np.nan)
    plot_df[value_cols] = (plot_df[value_cols].div(safe_totals, axis=0) * 100.0).fillna(0)

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

categories = plot_df[cat_col].astype(str).tolist()
x = np.arange(len(categories))

# Choose a consistent, high-contrast, colorblind-friendly palette
# Use tab10 and cycle if needed
tab10 = plt.cm.get_cmap('tab10')
colors = [tab10(i % tab10.N) for i in range(len(value_cols))]

bottom = np.zeros(len(categories))
bar_containers = []
for i, col in enumerate(value_cols):
    values = plot_df[col].to_numpy()
    bars = ax.bar(x, values, bottom=bottom, label=str(col), color=colors[i], edgecolor='black', linewidth=0.3)
    bar_containers.append(bars)
    bottom += values

# Axes & labels
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=0 if max(len(c) for c in categories) <= 10 else 30, ha='right')

if use_percent:
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylabel("Percentage of total (%)", color='black')
    title = "Stacked Bar Chart — Parts of a Whole (Percent of Total)"
else:
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Value", color='black')
    title = "Stacked Bar Chart — Parts of a Whole"

ax.set_title(title, color='black')
ax.set_xlabel(str(cat_col).strip().title(), color='black')

# Grid for readability (light, unobtrusive)
ax.yaxis.grid(True, linestyle='-', linewidth=0.5, alpha=0.3)
ax.set_axisbelow(True)

# Legend
legend = ax.legend(title="Components", frameon=True)
legend.get_frame().set_alpha(0.9)

# Tight layout and save
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

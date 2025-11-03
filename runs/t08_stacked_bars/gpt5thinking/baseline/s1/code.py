import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Read data
df = pd.read_csv("data.csv")

# Assume first column is the category axis; remaining columns are parts of the whole
category_col = df.columns[0]
part_cols = df.columns[1:]

# Coerce part columns to numeric, treating non-numeric as NaN -> 0
parts = df[part_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
categories = df[category_col].astype(str)

# Compute totals and decide whether to use percentage scale (if totals are comparable)
totals = parts.sum(axis=1)
mean_total = totals.replace(0, np.nan).mean()
std_total = totals.replace(0, np.nan).std()
use_percentage = False
if pd.notna(mean_total) and mean_total > 0:
    cv = (std_total / mean_total) if mean_total != 0 else np.inf
    use_percentage = cv <= 0.1  # "Comparable totals" heuristic

# Prepare data for plotting
if use_percentage:
    plot_data = parts.div(totals.replace(0, np.nan), axis=0).fillna(0) * 100.0
    y_label = "Percentage (%)"
    title = "Parts of a Whole Across Categories (Percentage Stacked Bar)"
else:
    plot_data = parts.copy()
    y_label = "Value"
    title = "Parts of a Whole Across Categories (Stacked Bar)"

# Figure sizing based on number of categories
n_categories = len(categories)
fig_width = max(8, min(20, 0.6 * n_categories + 2))
fig_height = 6
fig, ax = plt.subplots(figsize=(fig_width, fig_height))

# Consistent colors (up to many parts)
cmap = plt.get_cmap("tab20")
colors = [cmap(i % cmap.N) for i in range(len(part_cols))]

# Plot stacked bars
x = np.arange(n_categories)
bottom = np.zeros(n_categories)
bar_containers = []
for idx, col in enumerate(part_cols):
    values = plot_data[col].to_numpy()
    bars = ax.bar(
        x,
        values,
        bottom=bottom,
        label=str(col),
        color=colors[idx],
        edgecolor="black",
        linewidth=0.5
    )
    bar_containers.append(bars)
    bottom += values

# Axes labels and ticks
ax.set_title(title)
ax.set_xlabel(category_col)
ax.set_ylabel(y_label)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha="right")

# Y-axis scaling and formatting
ax.set_ylim(0, 100 if use_percentage else max(0, np.nanmax(bottom) * 1.1 if len(bottom) else 1))
if use_percentage:
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))

# Zero baseline for bars
ax.set_axisbelow(True)
ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6)

# Legend
legend = ax.legend(title="Components", ncol=min(4, len(part_cols)), frameon=True)
legend._legend_box.align = "left"  # type: ignore[attr-defined]

# Save figure
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

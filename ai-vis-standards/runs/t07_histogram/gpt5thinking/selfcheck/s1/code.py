import re
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data.csv")

# Helper to pick a numeric column (prefer a column literally named 'value' if present)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if 'value' in df.columns and pd.api.types.is_numeric_dtype(df['value']):
    col = 'value'
elif numeric_cols:
    col = numeric_cols[0]
else:
    raise ValueError("No numeric columns found in data.csv to plot a histogram.")

# Clean data
x = pd.to_numeric(df[col], errors='coerce').dropna().to_numpy()
if x.size == 0:
    raise ValueError(f"Column '{col}' has no numeric data after cleaning.")

# Parse variable name and unit from the column header, e.g., "Temperature (°C)" or "Speed [km/h]"
def parse_name_and_unit(header: str):
    # Patterns: (...) or [...]
    m = re.search(r"\(([^)]+)\)|\[(.+?)\]", header)
    unit = None
    if m:
        unit = (m.group(1) or m.group(2)).strip()
        base = re.sub(r"\s*(\([^)]+\)|\[[^\]]+\])\s*$", "", header).strip()
    else:
        base = header.strip()
    return base, unit

basename, unit = parse_name_and_unit(col)

# Choose reasonable binning using Freedman–Diaconis rule (robust to outliers)
def freedman_diaconis_bins(data: np.ndarray) -> int:
    data = np.asarray(data)
    if data.size < 2:
        return 10
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25
    if iqr == 0:
        # Fall back to Sturges if no spread
        k = math.ceil(math.log2(data.size) + 1)
        return int(np.clip(k, 5, 60))
    bin_width = 2 * iqr * (data.size ** (-1/3))
    if bin_width <= 0:
        return 10
    bins = int(np.ceil((data.max() - data.min()) / bin_width))
    return int(np.clip(bins, 10, 60))

bins = freedman_diaconis_bins(x)

# Plot
plt.rcParams.update({
    "figure.dpi": 150,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

fig, ax = plt.subplots(figsize=(6.5, 4.0))
counts, bins_edges, patches = ax.hist(x, bins=bins, edgecolor='black')

# Titles and labels
xlabel = f"{basename} ({unit})" if unit else basename
ax.set_xlabel(xlabel)
ax.set_ylabel("Count")
ax.set_title(f"Distribution of {basename}")

# Ensure readable contrast and clarity
ax.grid(True, axis='y', linestyle=':', linewidth=0.8, alpha=0.6)
for spine in ax.spines.values():
    spine.set_linewidth(0.8)

# Bars start at zero by default for histograms; make it explicit for robustness
ymin, ymax = ax.get_ylim()
ax.set_ylim(bottom=0, top=ymax)

fig.tight_layout()
fig.savefig("chart.png", dpi=150, bbox_inches='tight')

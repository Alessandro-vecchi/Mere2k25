import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from math import ceil

# Read data
df = pd.read_csv("data.csv")

# Select a numeric series
num_df = df.select_dtypes(include=[np.number])
if num_df.shape[1] >= 1:
    s = num_df.iloc[:, 0]
    col_name = num_df.columns[0]
else:
    # Try to coerce the first column to numeric if no numeric dtype detected
    col_name = df.columns[0]
    s = pd.to_numeric(df.iloc[:, 0], errors="coerce")

# Drop NaNs
x = s.dropna().values
n = len(x)

# Extract variable and unit from column name if present (e.g., "Temperature (°C)" or "NO2 [µg/m³]")
def parse_var_unit(name: str):
    m = re.match(r"^\s*(.*?)\s*[\(\[]\s*([^\)\]]+)\s*[\)\]]\s*$", str(name))
    if m:
        var = m.group(1).strip() or str(name).strip()
        unit = m.group(2).strip()
    else:
        var, unit = str(name).strip(), ""
    return var, unit

var, unit = parse_var_unit(col_name)
xlabel = f"{var} ({unit})" if unit else var

# Choose reasonable binning: Freedman–Diaconis, fallback to Sturges
bins = 10
if n > 1:
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    if iqr > 0:
        h = 2 * iqr * (n ** (-1 / 3))
        if h > 0:
            bins = int(ceil((x.max() - x.min()) / h)) if x.max() > x.min() else 1
    if bins <= 1 or not np.isfinite(bins):
        bins = int(ceil(np.log2(n) + 1))
    bins = int(np.clip(bins, 5, 60))

# Plot histogram as density
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(x, bins=bins, density=True, edgecolor="black", linewidth=0.5)
ax.set_xlabel(xlabel)
ax.set_ylabel("density")
ax.set_title(f"Distribution of {xlabel}")
ax.grid(alpha=0.3)
fig.tight_layout()

# Save figure
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

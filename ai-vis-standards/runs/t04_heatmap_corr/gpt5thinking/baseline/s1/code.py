import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read CSV, try to infer if the first column is an index of labels
df_raw = pd.read_csv("data.csv")
if df_raw.select_dtypes(include="number").shape[1] == df_raw.shape[1]:
    df = df_raw.copy()
else:
    df = pd.read_csv("data.csv", index_col=0)

# Coerce to numeric for heatmap values
data_df = df.apply(pd.to_numeric, errors="coerce")

# Prepare masked array to handle missing values gracefully
data = data_df.to_numpy()
masked_data = np.ma.masked_invalid(data)

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(masked_data, aspect="auto", interpolation="nearest")

# Ticks and labels
ax.set_xticks(np.arange(data_df.shape[1]))
ax.set_yticks(np.arange(data_df.shape[0]))
ax.set_xticklabels(list(map(str, data_df.columns)))
ax.set_yticklabels(list(map(str, data_df.index)))

# Rotate x tick labels for readability
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

# Labels and colorbar
ax.set_xlabel("Columns")
ax.set_ylabel("Rows")
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Value")

# Save figure
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

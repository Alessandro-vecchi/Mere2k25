import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import re

# --- Load data ---
df = pd.read_csv("data.csv")

# Parse a datetime column
def find_datetime_column(columns):
    candidates = [c for c in columns if any(k in c.lower() for k in ["date", "time", "timestamp"])]
    return candidates[0] if candidates else columns[0]

time_col = find_datetime_column(df.columns)
df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
df = df.sort_values(time_col).reset_index(drop=True)

# Identify numeric series columns (exclude datetime)
num_cols = [c for c in df.select_dtypes(include=[np.number]).columns]
# If numeric columns missing due to numbers stored as strings, try converting
if len(num_cols) < 2:
    for c in df.columns:
        if c == time_col:
            continue
        if c not in num_cols:
            try:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            except Exception:
                pass
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns]

# Ensure we have at least two numeric series
if len(num_cols) < 2:
    # Fallback: try all non-time columns after coercion
    others = [c for c in df.columns if c != time_col]
    for c in others:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns][:2]

series_a, series_b = num_cols[:2]

# Extract units from column names (e.g., "Temp (°C)" -> "°C")
def extract_unit(name):
    m = re.search(r"\((.*?)\)", name)
    return m.group(1) if m else None

unit_a = extract_unit(series_a)
unit_b = extract_unit(series_b)

ylabel_a = f"{series_a}" if unit_a is None else f"{series_a.split('(')[0].strip()} ({unit_a})"
ylabel_b = f"{series_b}" if unit_b is None else f"{series_b.split('(')[0].strip()} ({unit_b})"

# --- Plot: two aligned panels (preferred over dual y-axes) ---
plt.rcParams.update({
    "figure.figsize": (10, 6.5),
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={"hspace": 0.15})

# Line styles with good visibility
linewidth = 2.0
marker = None

# Panel 1
ax1.plot(df[time_col], df[series_a], linewidth=linewidth, marker=marker, label=series_a)
ax1.set_ylabel(ylabel_a)
ax1.grid(True, linestyle="--", linewidth=0.6, alpha=0.5)
ax1.legend(frameon=False)

# Panel 2
ax2.plot(df[time_col], df[series_b], linewidth=linewidth, marker=marker, label=series_b)
ax2.set_ylabel(ylabel_b)
ax2.grid(True, linestyle="--", linewidth=0.6, alpha=0.5)
ax2.legend(frameon=False)

# X-axis formatting
locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
formatter = mdates.ConciseDateFormatter(locator)
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(formatter)
ax2.set_xlabel("Time")

# Overall title and subtitle note
title_main = "Two Time Series with Different Units (Aligned Panels)"
subtitle = "Panels avoid dual y-axes, improving interpretability across distinct units."
fig.suptitle(f"{title_main}\n{subtitle}", y=0.98)

# Tight layout and save
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("chart.png", dpi=150, bbox_inches="tight")

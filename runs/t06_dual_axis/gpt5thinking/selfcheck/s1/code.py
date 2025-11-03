import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ---- Load data ----
df = pd.read_csv("data.csv")

# Infer time column
time_candidates = [c for c in df.columns if c.lower() in {"date","time","timestamp","datetime","period"}]
if not time_candidates:
    # Fallback: try to detect a column that can be parsed as datetime
    for c in df.columns:
        try:
            pd.to_datetime(df[c])
            time_candidates.append(c)
            break
        except Exception:
            continue
if not time_candidates:
    raise ValueError("No time-like column found. Include a 'date'/'time' column or a parseable datetime column.")

tcol = time_candidates[0]
df[tcol] = pd.to_datetime(df[tcol], infer_datetime_format=True, errors="coerce")
df = df.dropna(subset=[tcol]).sort_values(tcol)

# Pick two numeric series columns (excluding time)
num_cols = [c for c in df.select_dtypes(include="number").columns if c != tcol]
if len(num_cols) < 2:
    # Try to coerce non-numeric columns (excluding time) to numeric
    candidates = [c for c in df.columns if c != tcol]
    coerced = []
    for c in candidates:
        ser = pd.to_numeric(df[c], errors="coerce")
        if ser.notna().sum() > 0:
            df[c] = ser
            coerced.append(c)
    num_cols = [c for c in df.select_dtypes(include="number").columns if c != tcol]

if len(num_cols) < 2:
    raise ValueError("Need at least two numeric series columns to plot.")

s1, s2 = num_cols[:2]

# Extract units from column names if present, e.g., "Temperature (°C)"
def extract_unit(col_name):
    m = re.search(r"\((.*?)\)", col_name)
    return m.group(1) if m else None

u1 = extract_unit(s1) or ""
u2 = extract_unit(s2) or ""

y1_label = f"{s1}" if not u1 else f"{s1} [{u1}]"
y2_label = f"{s2}" if not u2 else f"{s2} [{u2}]"

# ---- Plot: prefer two aligned panels over dual y-axes ----
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "text.color": "black",
    "xtick.color": "black",
    "ytick.color": "black",
})

fig, axes = plt.subplots(
    2, 1, sharex=True, figsize=(10, 6), constrained_layout=True
)

# Top panel
axes[0].plot(df[tcol], df[s1], label=s1, linewidth=2)
axes[0].set_ylabel(y1_label)
axes[0].grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
axes[0].legend(loc="best", frameon=False)

# Bottom panel
axes[1].plot(df[tcol], df[s2], label=s2, linewidth=2)
axes[1].set_ylabel(y2_label)
axes[1].set_xlabel(f"{tcol}")
axes[1].grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
axes[1].legend(loc="best", frameon=False)

# Date formatting for readability
locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
formatter = mdates.ConciseDateFormatter(locator)
axes[1].xaxis.set_major_locator(locator)
axes[1].xaxis.set_major_formatter(formatter)

# Title and justification (explicitly avoiding dual y-axes)
fig.suptitle(
    "Two Series Over Time in Aligned Panels\n"
    "Dual y-axes avoided to prevent misinterpretation of magnitudes and trends.",
    fontsize=12
)

# Save figure
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

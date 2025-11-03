import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# --- Load data ---
csv_path = Path("data.csv")
df_raw = pd.read_csv(csv_path)

# --- Identify time column ---
def find_datetime_column(df):
    # Priority 1: first column if it parses to many datetimes
    first_col = df.columns[0]
    dt_try = pd.to_datetime(df[first_col], errors="coerce", infer_datetime_format=True)
    if dt_try.notna().sum() >= max(3, int(0.5 * len(df))):
        return first_col

    # Priority 2: any column with 'date' or 'time' in the name
    for col in df.columns:
        if re.search(r"(date|time)", col, flags=re.I):
            dt_try = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            if dt_try.notna().sum() >= max(3, int(0.5 * len(df))):
                return col

    # Priority 3: any column that mostly parses as datetime
    for col in df.columns:
        dt_try = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
        if dt_try.notna().sum() >= max(3, int(0.5 * len(df))):
            return col

    raise ValueError("No suitable datetime column found.")

time_col = find_datetime_column(df_raw)
df = df_raw.copy()
df[time_col] = pd.to_datetime(df[time_col], errors="coerce", infer_datetime_format=True)
df = df.sort_values(time_col)

# --- Identify two numeric series columns ---
def coerce_numeric(s):
    return pd.to_numeric(s, errors="coerce")

candidate_cols = [c for c in df.columns if c != time_col]
numeric_scores = []
for c in candidate_cols:
    s = coerce_numeric(df[c])
    numeric_scores.append((c, s.notna().sum()))
numeric_cols_sorted = [c for c, score in sorted(numeric_scores, key=lambda x: -x[1]) if score > 0]

if len(numeric_cols_sorted) < 2:
    # Try to coerce all and fill with numeric where possible
    raise ValueError("Fewer than two numeric series detected for plotting.")

y1_col, y2_col = numeric_cols_sorted[:2]
y1 = pd.to_numeric(df[y1_col], errors="coerce")
y2 = pd.to_numeric(df[y2_col], errors="coerce")

# --- Helper to extract (name, unit) from column label like "Temperature (°C)" ---
def split_name_unit(col_name):
    m = re.match(r"^(.*?)(?:\s*\((.*?)\))\s*$", str(col_name))
    if m:
        base = m.group(1).strip()
        unit = m.group(2).strip()
    else:
        base, unit = str(col_name).strip(), None
    return base, unit

y1_name, y1_unit = split_name_unit(y1_col)
y2_name, y2_unit = split_name_unit(y2_col)

def format_ylabel(name, unit):
    return f"{name} ({unit})" if unit else name

# --- Plot: two aligned panels instead of dual y-axes ---
fig, axes = plt.subplots(
    2, 1, sharex=True, figsize=(10, 6), constrained_layout=True
)

# Date formatter for readable ticks
locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)

# Top panel
axes[0].plot(df[time_col], y1, label=y1_name, linewidth=1.8, marker="o", markersize=3)
axes[0].set_ylabel(format_ylabel(y1_name, y1_unit))
axes[0].legend(frameon=False)
axes[0].grid(True, linewidth=0.6, alpha=0.4)

# Bottom panel
axes[1].plot(df[time_col], y2, label=y2_name, linewidth=1.8, marker="o", markersize=3)
axes[1].set_ylabel(format_ylabel(y2_name, y2_unit))
axes[1].legend(frameon=False)
axes[1].grid(True, linewidth=0.6, alpha=0.4)

# Shared x-axis formatting
axes[1].xaxis.set_major_locator(locator)
axes[1].xaxis.set_major_formatter(formatter)
axes[1].set_xlabel(str(time_col))

# Title with explicit justification for using two panels
fig.suptitle(
    "Two Series Over Time — Two-Panel Layout (avoids dual y-axes; each panel shows its own units)"
)

# Tight layout and save
plt.savefig("chart.png", dpi=150, bbox_inches="tight")
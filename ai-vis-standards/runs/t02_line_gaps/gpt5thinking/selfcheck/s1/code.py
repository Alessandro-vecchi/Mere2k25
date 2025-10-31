import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Load data ---
csv_path = Path("data.csv")
df = pd.read_csv(csv_path)

# --- Identify date column ---
date_col_candidates = [c for c in df.columns if str(c).strip().lower() in {"date", "month", "period"}]
date_col = None

def try_parse_date(series):
    dt = pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
    return dt if dt.notna().mean() >= 0.7 else None

for c in ([date_col_candidates[0]] if date_col_candidates else []) + list(df.columns):
    if date_col is not None:
        break
    parsed = try_parse_date(df[c])
    if parsed is not None:
        date_col = c
        df["_dt"] = parsed.dt.to_period("M").dt.to_timestamp()
        break

if date_col is None:
    raise ValueError("No parseable date/month column found in data.csv.")

# --- Identify category and value columns ---
lower_cols = {str(c).strip().lower(): c for c in df.columns}
category_col = next((lower_cols[k] for k in ["category", "cat", "group", "series", "name"] if k in lower_cols), None)

# Numeric columns excluding helpers/date/category
numeric_cols = [c for c in df.select_dtypes(include="number").columns if c not in {"_dt"}]
value_col = lower_cols["value"] if "value" in lower_cols else (numeric_cols[0] if len(numeric_cols) == 1 else None)

# --- Prepare monthly dataframe with gaps (NaNs) for missing months ---
if category_col and value_col:
    # Wide format: one line per category
    wide = (
        df[[ "_dt", category_col, value_col ]]
        .groupby(["_dt", category_col], as_index=False)[value_col].mean()
        .pivot(index="_dt", columns=category_col, values=value_col)
        .sort_index()
    )
    # Reindex to full monthly range to show gaps
    full_idx = pd.period_range(wide.index.min(), wide.index.max(), freq="M").to_timestamp()
    plot_df = wide.reindex(full_idx)
    y_label_source = value_col
    legend_labels = list(plot_df.columns.astype(str))
else:
    # Single/multiple numeric series without explicit category
    if value_col:
        series = df[["_dt", value_col]].groupby("_dt", as_index=True)[value_col].mean().sort_index()
        full_idx = pd.period_range(series.index.min(), series.index.max(), freq="M").to_timestamp()
        plot_df = series.reindex(full_idx).to_frame(name=value_col)
        legend_labels = None  # single line -> no legend
        y_label_source = value_col
    else:
        # Plot all numeric columns as separate lines
        data = df[["_dt"] + numeric_cols].groupby("_dt", as_index=True).mean().sort_index()
        full_idx = pd.period_range(data.index.min(), data.index.max(), freq="M").to_timestamp()
        plot_df = data.reindex(full_idx)
        legend_labels = list(plot_df.columns.astype(str))
        y_label_source = " / ".join(legend_labels)

# --- Extract unit from column name if present, e.g., "Value (mg/L)" -> "mg/L" ---
def extract_unit(name: str) -> str:
    m = re.search(r"\(([^)]+)\)", str(name))
    return m.group(1).strip() if m else ""

unit = extract_unit(y_label_source)
y_label = f"Value ({unit})" if unit else "Value"

# --- Plot ---
plt.figure(figsize=(10, 6))
ax = plt.gca()

# Plot each column
if plot_df.shape[1] == 1:
    ax.plot(plot_df.index, plot_df.iloc[:, 0], marker="o", linewidth=2)
else:
    for col in plot_df.columns:
        ax.plot(plot_df.index, plot_df[col], marker="o", linewidth=2, label=str(col))

# Formatting: quarterly ticks, readable labels
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

ax.set_xlabel("Month")
ax.set_ylabel(y_label)
ax.set_title("Monthly Trend")

# Grid for readability
ax.grid(True, which="major", linestyle="--", linewidth=0.6, alpha=0.7)

# Legend only if multiple series
if plot_df.shape[1] > 1:
    ax.legend(title="Series", frameon=False)

plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")
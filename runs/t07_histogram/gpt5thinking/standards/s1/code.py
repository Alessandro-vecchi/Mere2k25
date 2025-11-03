import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

# --- Load data robustly ---
path = Path("data.csv")
if not path.exists():
    raise FileNotFoundError("data.csv not found in current directory.")
# Try common encodings
for enc in ("utf-8-sig", "utf-8", "latin-1"):
    try:
        df = pd.read_csv(path, encoding=enc)
        break
    except Exception:
        df = None
if df is None:
    raise ValueError("Unable to read data.csv with common encodings.")

# --- Helper: find numeric column to plot ---
def find_numeric_series(frame: pd.DataFrame) -> pd.Series:
    # Prefer a column literally named 'value' (case-insensitive)
    for col in frame.columns:
        if str(col).strip().lower() == "value":
            s = pd.to_numeric(frame[col], errors="coerce")
            if s.notna().any():
                return s.rename(col)
    # Otherwise, pick the first column that becomes numeric with coercion and has >0 non-NaNs
    for col in frame.columns:
        s = pd.to_numeric(frame[col], errors="coerce")
        if s.notna().sum() > 0:
            return s.rename(col)
    # As a fallback, try selecting any numeric dtype columns directly
    num_cols = frame.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        return frame[num_cols[0]]
    raise ValueError("No numeric columns found to plot.")

s = find_numeric_series(df).astype(float)

# --- Extract unit and clean variable name for labels ---
def extract_unit_and_name(col_name: str, frame: pd.DataFrame) -> tuple[str, str]:
    unit = ""
    name = str(col_name).strip()

    # If there's a 'unit' column with a single unique non-null value, prefer it
    if "unit" in frame.columns:
        unique_units = pd.Series(frame["unit"]).dropna().unique()
        if len(unique_units) == 1:
            unit = str(unique_units[0]).strip()

    # Try to parse unit from column name patterns if not found
    if not unit:
        # Pattern like "Temperature (°C)"
        m = re.search(r"\(([^)]+)\)", name)
        if m:
            unit = m.group(1).strip()
            name = re.sub(r"\s*\([^)]+\)\s*", "", name).strip()

    if not unit:
        # Pattern like "value_mg/L" or "Concentration_mg_per_L"
        m = re.search(r"_(.+)$", name)
        if m and "/" in m.group(1) or "per" in m.group(1).lower() or any(ch.isalpha() for ch in m.group(1)):
            unit = m.group(1).replace("_", " ").strip()
            name = re.sub(r"_(.+)$", "", name).strip()

    # Tidy name casing but preserve acronyms
    tidy = " ".join(word if word.isupper() else word.capitalize() for word in re.split(r"\s+", name))
    return unit, tidy

unit, var_name = extract_unit_and_name(s.name, df)
x_label = f"{var_name} ({unit})" if unit else var_name

# --- Clean data ---
values = s.dropna().values
if values.size == 0:
    raise ValueError("Selected variable has no numeric data to plot.")

# --- Choose reasonable binning: Freedman–Diaconis rule with safeguards ---
def freedman_diaconis_bins(x: np.ndarray) -> int:
    x = np.asarray(x)
    x = x[np.isfinite(x)]
    if x.size < 2:
        return 1
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    if iqr == 0:
        # Fall back to Sturges' rule if no spread
        k = int(np.ceil(np.log2(x.size) + 1))
    else:
        bin_width = 2 * iqr * (x.size ** (-1/3))
        if bin_width <= 0:
            k = int(np.ceil(np.log2(x.size) + 1))
        else:
            k = int(np.clip(np.ceil((x.max() - x.min()) / bin_width), 5, 60))
    return max(1, k)

bins = freedman_diaconis_bins(values)

# --- Plot ---
plt.rcParams.update({
    "figure.figsize": (8, 5),
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

fig, ax = plt.subplots()

# Histogram with counts; bars naturally start at zero on y-axis
n, bins_edges, patches = ax.hist(values, bins=bins, edgecolor="black", linewidth=0.6)

# Accessibility/readability aids
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.6)
ax.set_axisbelow(True)

# Labels and title
ax.set_title(f"Distribution of {var_name}")
ax.set_xlabel(x_label)
ax.set_ylabel("count")

# Tight layout and save
fig.tight_layout()
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

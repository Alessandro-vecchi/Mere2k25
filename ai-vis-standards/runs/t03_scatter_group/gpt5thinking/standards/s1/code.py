import re
import pandas as pd
import matplotlib.pyplot as plt

# --- Helpers ---
def extract_label_and_unit(col_name: str):
    """
    Extracts base label and unit from column name patterns like:
    'x (m)', 'y [kg]', 'Speed_km/h', 'Temp-°C'.
    Returns (label, unit or None).
    """
    s = col_name.strip()
    # Common bracketed units: (), [], {}
    m = re.match(r"^(.*?)[\s_]*[\(\[\{]\s*([^\]\)\}]+?)\s*[\)\]\}]\s*$", s)
    if m:
        label = m.group(1).strip()
        unit = m.group(2).strip()
        return (label if label else s, unit)
    # Suffix patterns like 'Speed_km/h' or 'Temp-°C'
    m2 = re.match(r"^(.*?)[\s_\-]+([A-Za-z°/%]+(?:/[A-Za-z°%]+)?)$", s)
    if m2 and len(m2.group(2)) >= 2:
        return (m2.group(1).strip() or s, m2.group(2).strip())
    return (s, None)

def find_xy_group_columns(df: pd.DataFrame):
    cols = list(df.columns)

    # Normalize name map
    lower_map = {c: c.lower() for c in cols}

    # Prefer explicit 'x'/'y'
    x_candidates = [c for c in cols if lower_map[c] in ("x", "x_value")]
    y_candidates = [c for c in cols if lower_map[c] in ("y", "y_value")]

    # Broaden search: startswith
    if not x_candidates:
        x_candidates = [c for c in cols if lower_map[c].startswith("x ")] or \
                       [c for c in cols if lower_map[c].startswith("x")]
    if not y_candidates:
        y_candidates = [c for c in cols if lower_map[c].startswith("y ")] or \
                       [c for c in cols if lower_map[c].startswith("y")]

    # Fallback: first two numeric columns as x,y
    if not x_candidates or not y_candidates:
        numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
        if len(numeric_cols) >= 2:
            if not x_candidates:
                x_candidates = [numeric_cols[0]]
            if not y_candidates:
                # ensure different from x
                y_candidates = [nc for nc in numeric_cols if nc != x_candidates[0]][:1]

    x_col = x_candidates[0] if x_candidates else None
    y_col = y_candidates[0] if y_candidates else None

    # Group column: explicit 'group' or last non-numeric/categorical-like
    group_col = None
    for c in cols:
        if lower_map[c] in ("group", "grp", "category", "cat", "class", "label"):
            group_col = c
            break
    if group_col is None:
        # pick a non-numeric column with low cardinality (reasonable groups)
        non_numeric = [c for c in cols if not pd.api.types.is_numeric_dtype(df[c])]
        if non_numeric:
            # choose the one with smallest reasonable unique count > 1
            candidates = sorted(
                (c for c in non_numeric if 1 < df[c].nunique(dropna=True) <= max(20, int(len(df)*0.2))),
                key=lambda c: df[c].nunique(dropna=True)
            )
            group_col = candidates[0] if candidates else non_numeric[0]

    return x_col, y_col, group_col

# --- Load data ---
df = pd.read_csv("data.csv", encoding="utf-8-sig")

x_col, y_col, group_col = find_xy_group_columns(df)
if x_col is None or y_col is None:
    raise ValueError("Could not infer x/y columns. Ensure your CSV contains 'x' and 'y' (case-insensitive) or two numeric columns.")

# Prepare labels with units (if present)
x_label_base, x_unit = extract_label_and_unit(str(x_col))
y_label_base, y_unit = extract_label_and_unit(str(y_col))
x_label = f"{x_label_base} ({x_unit})" if x_unit else x_label_base
y_label = f"{y_label_base} ({y_unit})" if y_unit else y_label_base

# Coerce x/y to numeric in case they are strings with numeric content
x = pd.to_numeric(df[x_col], errors="coerce")
y = pd.to_numeric(df[y_col], errors="coerce")
plot_df = pd.DataFrame({x_label: x, y_label: y})
if group_col is not None:
    plot_df["__group__"] = df[group_col].astype("string")
else:
    plot_df["__group__"] = "All"

# Drop rows with missing x or y
plot_df = plot_df.dropna(subset=[x_label, y_label])

# --- Plot ---
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "text.color": "black",
    "xtick.color": "black",
    "ytick.color": "black",
})

fig, ax = plt.subplots(figsize=(7, 5))

# Mitigate overplotting: small markers, partial transparency, thin edge
for g, sub in plot_df.groupby("__group__"):
    ax.scatter(
        sub[x_label], sub[y_label],
        s=24, alpha=0.6, linewidths=0.3, edgecolors="black", label=str(g)
    )

ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
ax.set_title("Scatterplot of Y vs X by Group")

# Legend (only if multiple groups)
handles, labels = ax.get_legend_handles_labels()
if len(labels) > 1 or (labels and labels[0] != "All"):
    leg = ax.legend(title="Group", frameon=True, framealpha=1.0)
    # Improve legend text contrast implicitly via default colors on white
else:
    # Remove legend if it's just a single "All"
    if ax.get_legend() is not None:
        ax.get_legend().remove()

ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)

# Tight layout and save
fig.tight_layout()
fig.savefig("chart.png", dpi=150, bbox_inches="tight")

import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data.csv")
df = df.dropna(subset=["Concentration (milligrams per liter)"])
df["Concentration (milligrams per liter)"] = df["Concentration (milligrams per liter)"].astype(float)

# Sort descending by value
df_sorted = df.sort_values("Concentration (milligrams per liter)", ascending=False)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    df_sorted["Site"],
    df_sorted["Concentration (milligrams per liter)"],
    color="#3366cc"
)
ax.set_title("River Concentrations Ranked by Value", fontsize=14, pad=12)
ax.set_xlabel("River Site", fontsize=12)
ax.set_ylabel("Concentration (mg/L)", fontsize=12)
ax.set_ylim(0, df_sorted["Concentration (milligrams per liter)"].max() * 1.1)
plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=9)

# Improve contrast for y-tick labels and axes
ax.tick_params(axis='y', labelsize=10, colors='#222222')
ax.spines['bottom'].set_color('#222222')
ax.spines['left'].set_color('#222222')
ax.yaxis.label.set_color('#222222')
ax.xaxis.label.set_color('#222222')
ax.title.set_color('#222222')

# Add legend
ax.legend(['Concentration (mg/L)'], loc='upper right', facecolor='white', edgecolor='gray', fontsize=10)

plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

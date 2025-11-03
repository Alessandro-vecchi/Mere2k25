import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data.csv", delim_whitespace=True, names=['Site', 'Concentration', 'Unit'], header=None, skiprows=1)
df['Value'] = pd.to_numeric(df['Concentration'], errors='coerce')
df = df.dropna(subset=['Value'])

# Sort descending by value
df_sorted = df.sort_values('Value', ascending=False)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(df_sorted['Site'], df_sorted['Value'], color='#2861ce', edgecolor='black')

# Titles and labels
ax.set_title('River Sites Ranked by Concentration', fontsize=14)
ax.set_xlabel('Site', fontsize=12)
ax.set_ylabel('Concentration (milligrams per liter)', fontsize=12)
ax.set_ylim(0, df_sorted['Value'].max() * 1.08)

# Y-axis grid for readability
ax.yaxis.grid(True, linestyle='--', alpha=0.7)

# Rotate x ticks for readability
plt.xticks(rotation=35, ha='right')

# Improve layout
plt.tight_layout()

# Save figure
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data
df = pd.read_csv('data.csv')

# Parse month-year to datetime
df['date'] = pd.to_datetime(df['month'], format='%B %Y', errors='coerce')
df = df.dropna(subset=['date']).sort_values('date')

# Get unique regions
regions = df['region'].unique()
n_regions = len(regions)

# Create figure with subplots
fig, axes = plt.subplots(n_regions, 1, figsize=(10, 2 * n_regions), sharex=True, sharey=True)
if n_regions == 1:
    axes = [axes]

# Colors for lines (consistent across regions)
colors = plt.cm.tab10(np.linspace(0, 1, len(regions)))

# Plot each region
for ax, region, color in zip(axes, regions, colors):
    data = df[df['region'] == region]
    ax.plot(data['date'], data['value'], color=color, linewidth=2, label=region)
    ax.set_title(region, fontsize=12, pad=10)
    ax.grid(True, linestyle='--', alpha=0.5)

# Shared y-label
fig.text(0.04, 0.5, 'Value', va='center', ha='center', rotation='vertical', fontsize=12)

# Shared x-label
fig.text(0.5, 0.04, 'Month', va='center', ha='center', fontsize=12)

# Format x-axis
for ax in axes:
    ax.tick_params(axis='x', rotation=45)

# Shared legend below the plots
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=len(regions), fontsize=10)

# Layout
plt.subplots_adjust(hspace=0.4, bottom=0.15, top=0.95, left=0.1, right=0.95)

# Save
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
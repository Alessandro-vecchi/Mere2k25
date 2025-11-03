import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df['date'] = pd.to_datetime(df['month'], format='%B %Y')
df = df.sort_values(['region', 'date'])

regions = df['region'].unique()
n_regions = len(regions)
cols = 3
rows = (n_regions + cols - 1) // cols

fig, axes = plt.subplots(rows, cols, figsize=(12, 2.5 * rows), sharey=True, sharex=True)
axes = axes.flatten() if n_regions > 1 else [axes]

for ax, region in zip(axes, regions):
    region_df = df[df['region'] == region]
    ax.plot(region_df['date'], region_df['value'], label=region, marker='o', markersize=3)
    ax.set_title(region)
    ax.grid(True, linestyle='--', alpha=0.5)

for ax in axes[n_regions:]:
    ax.set_visible(False)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=4, frameon=False)

fig.autofmty_xdate()
plt.tight_layout(rect=[0, 0.05, 1, 0.98])
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
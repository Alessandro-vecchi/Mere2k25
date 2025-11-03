import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime

# Read data
df = pd.read_csv('data.csv')

# Parse dates
df['date'] = pd.to_datetime(df['month'])
df['year'] = df['date'].dt.year
df['month_num'] = df['date'].dt.month

# Create figure with grid
n_regions = df['region'].nunique()
fig = plt.figure(figsize=(16, 10))
gs = GridSpec(n_regions, 1, hspace=0.3, figure=fig)

# Get unique regions
regions = sorted(df['region'].unique())

# Colors for regions
colors = sns.color_palette("husl", n_regions)

# Create subplots
axes = []
for i, region in enumerate(regions):
    ax = fig.add_subplot(gs[i, 0])
    axes.append(ax)
    
    # Filter data for region
    region_df = df[df['region'] == region].sort_values('date')
    
    # Plot line
    ax.plot(range(len(region_df)), region_df['value'], 
            color=colors[i], linewidth=2, marker='o', markersize=4)
    
    # Formatting
    ax.set_title(f'{region}', fontsize=12, fontweight='bold', pad=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.set_xlabel('Month', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Set y-limits to match global range
    global_min = df['value'].min()
    global_max = df['value'].max()
    y_margin = (global_max - global_min) * 0.05
    ax.set_ylim(global_min - y_margin, global_max + y_margin)
    
    # Format x-ticks with month names
    month_labels = [str(m.month_name()[:3]) for m in region_df['date']]
    ax.set_xticks(range(0, len(region_df), 3))  # Every 3 months
    ax.set_xticklabels([month_labels[i] for i in range(0, len(region_df), 3)], 
                       rotation=45, ha='right')

# Create shared legend
fig.legend(handles=[plt.Line2D([0], [0], color=colors[i], lw=2, 
                              label=regions[i]) for i in range(n_regions)], 
          loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=n_regions, 
          fontsize=10)

# Main title
fig.suptitle('Monthly Values by Region (2023-2024)', fontsize=16, fontweight='bold', y=0.98)

# Adjust layout and save
plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
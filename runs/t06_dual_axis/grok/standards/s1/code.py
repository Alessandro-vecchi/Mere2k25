import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np

# Read data
df = pd.read_csv('data.csv')
df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y')
df = df.set_index('date')

# Create figure with two subplots sharing x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'hspace': 0.15})

# Plot Precipitation on top panel
color1 = '#1f77b4'  # blue
ax1.bar(df.index, df['Precipitation (mm)'], width=0.8, color=color1, alpha=0.8, label='Precipitation')
ax1.set_ylabel('Precipitation (mm)', fontsize=12, color=color1)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_title('Daily Precipitation and Discharge (January - April 2024)', fontsize=14, pad=15)
ax1.legend(loc='upper left')
ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
ax1.set_ylim(0, df['Precipitation (mm)'].max() * 1.1)

# Plot Discharge on bottom panel
color2 = '#ff7f0e'  # orange
ax2.plot(df.index, df['Discharge (cubic meters per second)'], color=color2, linewidth=2, label='Discharge')
ax2.set_ylabel('Discharge (m³/s)', fontsize=12, color=color2)
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_xlabel('Date', fontsize=12)
ax2.legend(loc='upper left')
ax2.grid(True, linestyle='--', alpha=0.7)

# Format x-axis
ax2.xaxis.set_major_formatter(DateFormatter('%b %d'))
plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')

# Adjust layout and save
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.close()
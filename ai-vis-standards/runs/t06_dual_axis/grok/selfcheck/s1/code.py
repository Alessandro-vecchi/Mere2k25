import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

# Read data
df = pd.read_csv('data.csv', parse_dates=['date'])
df = df.set_index('date')

# Create figure with two subplots sharing x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [1, 2]})

# Plot precipitation on top panel (bar)
ax1.bar(df.index, df['Precipitation (mm)'], color='tab:blue', width=1.0, edgecolor='none', alpha=0.8)
ax1.set_ylabel('Precipitation (mm)', fontsize=12)
ax1.set_title('Daily Precipitation and River Discharge', fontsize=14, pad=15)
ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
ax1.set_ylim(0, df['Precipitation (mm)'].max() * 1.1)

# Plot discharge on bottom panel (line)
ax2.plot(df.index, df['Discharge (cubic meters per second)'], color='tab:green', linewidth=2, label='Discharge')
ax2.set_ylabel('Discharge (m³/s)', fontsize=12)
ax2.set_xlabel('Date', fontsize=12)
ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
ax2.legend(loc='upper left')

# Format x-axis
ax2.xaxis.set_major_locator(mdates.MonthLocator())
ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
ax2.xaxis.set_major_formatter(DateFormatter('%b %Y'))
plt.setp(ax2.get_xticklabels(), rotation=0, ha='center')

# Adjust layout
plt.tight_layout()

# Save figure
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
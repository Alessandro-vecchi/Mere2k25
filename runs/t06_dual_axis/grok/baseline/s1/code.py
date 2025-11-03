import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

df = pd.read_csv('data.csv', parse_dates=['date'])
df.set_index('date', inplace=True)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [1, 1]})

ax1.bar(df.index, df['Precipitation (mm)'], color='tab:blue', width=1.0, label='Precipitation')
ax1.set_ylabel('Precipitation (mm)', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.set_title('Daily Precipitation and Discharge (January - April 2024)')
ax1.grid(True, axis='y', linestyle='--', alpha=0.7)

ax2.plot(df.index, df['Discharge (cubic meters per second)'], color='tab:green', linewidth=2, label='Discharge')
ax2.set_ylabel('Discharge (m³/s)', color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')
ax2.set_xlabel('Date')
ax2.grid(True, axis='y', linestyle='--', alpha=0.7)

date_form = DateFormatter("%b %d")
ax2.xaxis.set_major_formatter(date_form)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

fig.align_ylabels([ax1, ax2])
plt.subplots_adjust(hspace=0.15)
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
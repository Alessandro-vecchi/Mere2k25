import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

df = pd.read_csv('data.csv')
df['date'] = pd.to_datetime(df['date'], format='%B %Y')
df = df.sort_values('date')

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['date'], df['Temperature (°C)'], marker='o', linestyle='-', color='tab:blue')

ax.set_title('Monthly Temperature Trend')
ax.set_xlabel('Date')
ax.set_ylabel('Temperature (°C)')

ax.grid(True, linestyle='--', alpha=0.7)

ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=12))
ax.tick_params(axis='x', rotation=45)

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.close(fig)
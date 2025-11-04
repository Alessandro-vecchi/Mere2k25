import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

df = pd.read_csv('data.csv')
df['date'] = pd.to_datetime(df['date'], format='%B %Y')
df = df.sort_values('date')

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
ax.plot(df['date'], df['Temperature (°C)'], marker='o', linewidth=2, color='#1f77b4')

ax.set_title('Monthly Temperature Trend', fontsize=14, pad=15)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Temperature (°C)', fontsize=12)

ax.grid(True, which='major', axis='y', linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=8))
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.close()
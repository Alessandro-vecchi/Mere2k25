import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

df = pd.read_csv('data.csv', parse_dates=['date'], dayfirst=False)
df = df.set_index('date').sort_index()

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df.index, df['Temperature (°C)'], marker='o', linestyle='-')

ax.set_ylabel('Temperature (°C)')
ax.set_title('Monthly Temperature Trend')

ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=12))
ax.grid(True, which='major', axis='y', linestyle='--', alpha=0.5)

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.close(fig)
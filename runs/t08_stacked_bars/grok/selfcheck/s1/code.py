import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')
df.set_index('country', inplace=True)
totals = df.sum(axis=1)
df_pct = df.div(totals, axis=0) * 100

colors = {'Coal': '#4b4b4b', 'Gas': '#ff7f0e', 'Nuclear': '#d62728', 'Renewables': '#2ca02c'}

fig, ax = plt.subplots(figsize=(10, 6))
df_pct.plot(kind='bar', stacked=True, ax=ax, color=[colors[col] for col in df.columns])

ax.set_title('Energy Mix by Country (% of Total)', fontsize=14, pad=15)
ax.set_ylabel('Percentage (%)', fontsize=12)
ax.set_xlabel('Country', fontsize=12)
ax.set_ylim(0, 100)
ax.legend(title='Energy Source', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, title_fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.3)

plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
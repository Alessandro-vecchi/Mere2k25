import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')
df.set_index('country', inplace=True)
totals = df.sum(axis=1)
df_pct = df.div(totals, axis=0) * 100

ax = df_pct.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
ax.set_ylabel('Percentage (%)')
ax.set_title('Energy Sources by Country (Percentage)')
ax.legend(title='Energy Source', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
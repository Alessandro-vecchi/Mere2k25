import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df.set_index('country', inplace=True)
totals = df.sum(axis=1)
df_pct = df.div(totals, axis=0) * 100

colors = {'Coal': '#2E2E2E', 'Gas': '#808080', 'Nuclear': '#D4A017', 'Renewables': '#4CAF50'}

ax = df_pct.plot(kind='bar', stacked=True, color=[colors[col] for col in df_pct.columns],
                 figsize=(10, 6), width=0.8)

ax.set_title('Energy Mix by Country (Percentage of Total Production)', fontsize=14, pad=15)
ax.set_xlabel('Country', fontsize=12)
ax.set_ylabel('Percentage (%)', fontsize=12)
ax.set_ylim(0, 100)
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], title='Energy Source', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
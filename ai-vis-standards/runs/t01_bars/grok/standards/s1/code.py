import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df = df.dropna().sort_values(by='Concentration (milligrams per liter)', ascending=False)

plt.figure(figsize=(10, 6))
bars = plt.bar(df['Site'], df['Concentration (milligrams per liter)'], color='#1f77b4')
plt.xlabel('Site')
plt.ylabel('Concentration (mg/L)')
plt.title('River Sediment Concentration Ranking')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height}', ha='center', va='bottom', fontsize=9)
plt.ylim(0, max(df['Concentration (milligrams per liter)']) * 1.15)
plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
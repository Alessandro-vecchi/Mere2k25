import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df = df.dropna(subset=['Concentration (milligrams per liter)'])
df['Concentration (milligrams per liter)'] = pd.to_numeric(df['Concentration (milligrams per liter)'], errors='coerce')
df = df.sort_values(by='Concentration (milligrams per liter)', ascending=False)

plt.figure(figsize=(10, 6), dpi=150)
bars = plt.bar(df['Site'], df['Concentration (milligrams per liter)'], color='#1f77b4')
plt.xlabel('Site')
plt.ylabel('Concentration (mg/L)')
plt.title('River Sediment Concentration by Site')
plt.xticks(rotation=45, ha='right')
plt.ylim(0, df['Concentration (milligrams per liter)'].max() * 1.1)

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
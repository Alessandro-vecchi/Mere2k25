import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df = df.dropna().sort_values(by='Concentration (milligrams per liter)', ascending=False)

fig, ax = plt.subplots()
ax.bar(df['Site'], df['Concentration (milligrams per liter)'])
ax.set_ylabel('Concentration (mg/L)')
ax.set_title('Concentration by Site')
plt.xticks(rotation=45, ha='right')
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
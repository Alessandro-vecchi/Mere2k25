import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')

plt.figure(figsize=(10, 6))
groups = df['Group'].unique()
colors = {'Male': 'blue', 'Female': 'red', 'Other': 'green'}

for group in groups:
    subset = df[df['Group'] == group]
    plt.scatter(subset['Age (years)'], subset['Total Cholesterol (mg/dL)'],
                label=group, color=colors[group], alpha=0.6, s=20)

plt.xlabel('Age (years)')
plt.ylabel('Total Cholesterol (mg/dL)')
plt.legend(title='Group')
plt.grid(True, alpha=0.3)

plt.savefig('chart.png', dpi=150, bbox_inches='tight')

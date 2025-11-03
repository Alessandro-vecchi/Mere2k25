import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')
data = df['Particle Size (mm)']

fig, ax = plt.subplots(figsize=(8, 6))
counts, bins, patches = ax.hist(data, bins=50, edgecolor='black', color='skyblue', alpha=0.7)

ax.set_xlabel('Particle Size (mm)')
ax.set_ylabel('Count')
ax.set_title('Histogram of Particle Size Distribution')

ax.grid(True, alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('data.csv')
values = data.iloc[1:, 0].astype(float)

fig, ax = plt.subplots()
ax.hist(values, bins=50, density=False, edgecolor='black')
ax.set_xlabel('Particle Size (mm)')
ax.set_ylabel('Count')
ax.set_title('Histogram of Particle Size Distribution')

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
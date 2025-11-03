import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')
data = df['Particle Size (mm)']

plt.figure(figsize=(10, 6))
counts, bins, _ = plt.hist(data, bins=50, density=False, color='skyblue', edgecolor='black')
plt.title('Histogram of Particle Size Distribution')
plt.xlabel('Particle Size (mm)')
plt.ylabel('Count')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Read the CSV file
df = pd.read_csv('data.csv', index_col=0)

# Create the heatmap
plt.figure(figsize=(12, 10))
sns.set(font_scale=1.1)

# Mask upper triangle for better readability (optional, but clean)
mask = np.triu(np.ones_like(df, dtype=bool))

# Heatmap
ax = sns.heatmap(df, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                 square=True, linewidths=.5, cbar_kws={"shrink": .8}, mask=mask)

# Colorbar label
cbar = ax.collections[0].colorbar
cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)

# Labels and title
plt.title('Correlation Matrix of Environmental and Economic Indicators', pad=20)
plt.xlabel('')
plt.ylabel('')

# Rotate labels
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

# Adjust layout
plt.tight_layout()

# Save figure
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
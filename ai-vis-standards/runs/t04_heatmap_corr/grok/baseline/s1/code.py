import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

df = pd.read_csv('data.csv', index_col=0)
corr = df.corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, 
            square=True, linewidths=.5, cbar_kws={"shrink": .8},
            fmt='.2f', annot_kws={"size": 8})

plt.title('Correlation Heatmap')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
cbar = plt.gca().collections[0].colorbar
cbar.set_label('Correlation Coefficient')

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
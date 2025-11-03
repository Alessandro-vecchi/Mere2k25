import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("data.csv")

# Create the scatter plot
plt.figure(figsize=(10, 6))
groups = df['Group'].unique()
colors = {'Male': 'blue', 'Female': 'red', 'Other': 'green'}

for group in groups:
    subset = df[df['Group'] == group]
    plt.scatter(subset['Age (years)'], subset['Total Cholesterol (mg/dL)'],
                c=colors[group], label=group, alpha=0.6, s=30, edgecolors='none')

# Labels and title
plt.xlabel('Age (years)')
plt.ylabel('Total Cholesterol (mg/dL)')
plt.title('Total Cholesterol vs Age by Group')

# Legend
plt.legend(title='Group')

# Grid for better readability
plt.grid(True, alpha=0.3)

# Save the figure
plt.savefig("chart.png", dpi=150, bbox_inches='tight')
plt.close()

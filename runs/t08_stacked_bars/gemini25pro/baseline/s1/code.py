import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Read the data
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: data.csv not found. Make sure the file is in the correct directory.")
    exit()

# Set 'country' as the index for easier plotting
df = df.set_index('country')

# Calculate the percentage for each energy source within each country
df_pct = df.div(df.sum(axis=1), axis=0) * 100

# Define colors for consistency (optional, but good practice)
colors = ['#4A4A4A', '#FF8C00', '#50C878', '#4682B4'] 

# Create the stacked bar chart
ax = df_pct.plot(
    kind='bar', 
    stacked=True, 
    figsize=(12, 7),
    color=colors,
    width=0.8
)

# Set title and labels
plt.title('Share of Energy Production by Source per Country', fontsize=16)
plt.xlabel('Country', fontsize=12)
plt.ylabel('Percentage', fontsize=12)

# Format the y-axis to show percentage symbols
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100.0))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Add a legend
# Place legend outside the plot area
plt.legend(title='Energy Source', bbox_to_anchor=(1.02, 1), loc='upper left')

# Ensure the plot layout is tight
# (bbox_inches='tight' in savefig also helps)
plt.tight_layout() 

# Save the figure
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

# Close the plot to free memory (good practice, especially in scripts)
plt.close()
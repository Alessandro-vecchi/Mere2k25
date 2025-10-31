import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
try:
    data = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: 'data.csv' not found.")
    exit()

# Rename column for easier handling
data.rename(columns={'Concentration (milligrams per liter)': 'Concentration (mg/L)'}, inplace=True)

# Drop rows with missing values (like Mississippi River)
data.dropna(subset=['Concentration (mg/L)'], inplace=True)

# Ensure concentration is numeric
data['Concentration (mg/L)'] = pd.to_numeric(data['Concentration (mg/L)'], errors='coerce')
data.dropna(subset=['Concentration (mg/L)'], inplace=True) # Drop again if coercion failed

# Sort data descending by concentration
data_sorted = data.sort_values(by='Concentration (mg/L)', ascending=False)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Define colors (using a default color, but ensuring contrast)
# Using a medium blue for bars, black for text
bar_color = '#0072B2' # A colorblind-friendly blue
text_color = '#000000'
grid_color = '#A9A9A9' # Dark gray grid

# Create bars
ax.bar(data_sorted['Site'], data_sorted['Concentration (mg/L)'], color=bar_color)

# Set titles and labels
ax.set_title("River Concentration Levels (Ranked)", color=text_color, fontsize=16, weight='bold')
ax.set_xlabel("Site", color=text_color, fontsize=12)
ax.set_ylabel("Concentration (mg/L)", color=text_color, fontsize=12)

# Set bar base to zero (default for bar charts)
ax.set_ylim(bottom=0)

# Rotate x-axis labels for readability
plt.xticks(rotation=45, ha='right', color=text_color)

# Set y-axis tick colors
plt.yticks(color=text_color)

# Add a y-axis grid for easier reading
ax.grid(axis='y', linestyle='--', color=grid_color, alpha=0.7)

# Ensure good contrast by setting facecolor
ax.set_facecolor('#FFFFFF') # White background
fig.set_facecolor('#FFFFFF')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the figure as specified
try:
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving chart: {e}")

# Do not call plt.show()
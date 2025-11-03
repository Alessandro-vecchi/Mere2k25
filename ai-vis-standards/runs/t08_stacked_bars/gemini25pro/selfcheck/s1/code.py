import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Read the data from the CSV file
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: data.csv not found.")
    exit()

# Set 'country' as the index for easier plotting
df.set_index('country', inplace=True)

# Define the columns to be stacked
energy_columns = ['Coal', 'Gas', 'Nuclear', 'Renewables']

# Calculate the percentage of each energy source for each country
# This is better for comparing the "parts of a whole" across categories with different totals
df_percent = df[energy_columns].div(df[energy_columns].sum(axis=1), axis=0) * 100

# Define colors for contrast and consistency
# Using a perceptually uniform colormap like 'viridis' or 'cividis' is good.
# Or define manually: colors = ['#5A5A5A', '#B0B0B0', '#D46A6A', '#6AB0D4']
# Using pandas default colormap functionality is simplest.
ax = df_percent.plot(
    kind='bar',
    stacked=True,
    figsize=(11, 7),
    colormap='tab20c' # Using a colormap with good differentiation
)

# --- Set Titles and Labels (Checklist Item) ---
ax.set_title('Proportional Energy Mix by Country', fontsize=16, pad=20)
ax.set_xlabel('Country', fontsize=12, labelpad=10)
ax.set_ylabel('Percentage of Total Production (%)', fontsize=12, labelpad=10)

# --- Format Y-axis (Checklist Item) ---
# Bars must start at zero (default for bar plots)
ax.set_ylim(0, 100)
# Format y-axis as percentage
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

# --- Add Legend (Checklist Item) ---
# Place legend outside the plot area to avoid obscuring data
ax.legend(
    title='Energy Source',
    bbox_to_anchor=(1.02, 1),
    loc='upper left',
    borderaxespad=0.
)

# --- Ensure Readability (Checklist Item) ---
# Rotate x-axis labels for readability
plt.xticks(rotation=45, ha='right')

# Add a light grid for easier reading of values
ax.grid(axis='y', linestyle='--', alpha=0.7, which='major')
ax.set_axisbelow(True) # Ensure grid is behind bars

# Adjust layout to prevent labels from being cut off
# This is handled by bbox_inches='tight' in savefig, but good practice.
# plt.tight_layout() # This can conflict with bbox_to_anchor

# --- Save the figure ---
# dpi=150, bbox_inches='tight' as requested
try:
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving figure: {e}")

# Close the plot to free memory (as plt.show() is forbidden)
plt.close()
import pandas as pd
import matplotlib.pyplot as plt
import re

# Read the CSV file
df = pd.read_csv("data.csv")

# Clean data: Drop rows where the concentration value is missing
# Assumes the concentration column is the second one, based on the snippet.
# A more robust way is to find the column with "Concentration" in it.
concentration_col = None
for col in df.columns:
    if 'concentration' in col.lower():
        concentration_col = col
        break

if concentration_col is None:
    # Fallback if no column name matches
    concentration_col = df.columns[1]

# Ensure the concentration column is numeric, coercing errors (like empty strings) to NaN
df[concentration_col] = pd.to_numeric(df[concentration_col], errors='coerce')

# Drop rows with NaN values in the concentration column
df_clean = df.dropna(subset=[concentration_col])

# Sort the DataFrame by concentration in descending order
df_sorted = df_clean.sort_values(by=concentration_col, ascending=False)

# Extract unit from the column name for the y-axis label
unit_match = re.search(r'\((.*?)\)', concentration_col)
y_label = concentration_col
if unit_match:
    # If unit is found, use it as requested
    y_label = f"Concentration ({unit_match.group(1)})"

# Set the site column (assuming it's the first column)
site_col = df.columns[0]

# Create the bar chart
plt.figure(figsize=(12, 7))
plt.bar(df_sorted[site_col], df_sorted[concentration_col], color='#4C72B0')

# Set titles and labels
plt.title('River Sites Ranked by Concentration', fontsize=16)
plt.xlabel(site_col, fontsize=12)
plt.ylabel(y_label, fontsize=12)

# Rotate x-axis labels for readability
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)

# Add a grid for easier reading
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Ensure the y-axis starts at zero
plt.ylim(bottom=0)

# Save the figure
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

# Close the plot to free memory
plt.close()
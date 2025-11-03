import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
try:
    data = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: data.csv not found.")
    exit()
except Exception as e:
    print(f"Error reading data.csv: {e}")
    exit()

# Check if the expected column is present
if "Particle Size (mm)" not in data.columns:
    print("Error: 'Particle Size (mm)' column not found in data.csv.")
    # As a fallback, try to use the first column if only one exists
    if len(data.columns) == 1:
        column_name = data.columns[0]
        print(f"Warning: Using first column '{column_name}' as a fallback.")
    else:
        print("Please check the CSV file.")
        exit()
else:
    column_name = "Particle Size (mm)"

# Create the histogram
plt.figure(figsize=(10, 6))
# Using 'auto' for reasonable binning based on data distribution
plt.hist(data[column_name], bins='auto', edgecolor='black', alpha=0.7)

# Set labels and title
plt.xlabel(column_name)
plt.ylabel("Count")
plt.title(f"Histogram of {column_name}")

# Ensure layout is clean
plt.tight_layout()

# Save the figure
try:
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving chart.png: {e}")
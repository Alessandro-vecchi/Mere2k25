import pandas as pd
import matplotlib.pyplot as plt
import re

try:
    # Read the CSV file
    df = pd.read_csv("data.csv")

    # Rename columns for easier access if needed, or get the exact names
    # Let's find the concentration column, assuming it's the second one
    # or contains "Concentration"
    site_col = df.columns[0]
    conc_col = df.columns[1]

    # Clean the concentration column name to extract units
    # Default unit
    unit = "(mg/L)"
    # Try to extract from column name
    match = re.search(r'\((.*?)\)', conc_col)
    if match:
        unit_label = match.group(0) # e.g., (milligrams per liter)
        # Standardize unit for label if possible
        if "milligrams per liter" in unit_label.lower():
            unit = "(mg/L)"
        else:
            unit = unit_label # Use as found
    
    y_axis_label = f"Concentration {unit}"


    # Convert concentration column to numeric, handling potential errors
    df[conc_col] = pd.to_numeric(df[conc_col], errors='coerce')

    # Drop rows where concentration is missing (NaN)
    df_cleaned = df.dropna(subset=[conc_col])

    # Sort the DataFrame by the concentration column in descending order
    df_sorted = df_cleaned.sort_values(by=conc_col, ascending=False)

    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Generate the bar chart
    plt.bar(df_sorted[site_col], df_sorted[conc_col])

    # Set labels and title
    plt.xlabel("Site")
    plt.ylabel(y_axis_label)
    plt.title("Concentration by Site (Ranked)")

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Ensure layout is tight
    plt.tight_layout()

    # Save the figure
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

    # Close the plot to free memory
    plt.close()

except FileNotFoundError:
    print("Error: data.csv not found.")
except Exception as e:
    print(f"An error occurred: {e}")
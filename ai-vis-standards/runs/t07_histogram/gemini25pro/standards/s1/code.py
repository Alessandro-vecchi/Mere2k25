import pandas as pd
import matplotlib.pyplot as plt

try:
    # Load the dataset
    df = pd.read_csv("data.csv")

    # Define the column name based on the provided snippet
    col_name = "Particle Size (mm)"

    # Check if the column exists
    if col_name not in df.columns:
        # Fallback if the header was misinterpreted (e.g., if file has no header)
        # In a real scenario, we'd raise a clearer error or inspect,
        # but for this request, we'll assume the first column is the target
        # if the named one isn't found AND there's only one column.
        # If the file truly lacks the 'Particle Size (mm)' header,
        # pandas might read the first data row as the header.
        # A more robust approach might be `pd.read_csv("data.csv", header=None)`
        # if we suspect no header, but we follow the snippet.
        
        # If the expected column name is not found, raise an error
        # as we cannot be sure which column to plot.
        raise KeyError(f"Column '{col_name}' not found in data.csv. "
                       f"Available columns: {list(df.columns)}")

    # Extract the data
    data = df[col_name]

    # Create a new figure
    plt.figure(figsize=(10, 6))
    
    # Plot the histogram
    # 'auto' bins provides a reasonable guess for bin width/number
    plt.hist(data, bins='auto', color='#1f77b4', edgecolor='black', alpha=0.75)

    # Set title and labels
    plt.title('Distribution of Particle Size', fontsize=16)
    plt.xlabel(col_name, fontsize=12) # Use the column name for x-label
    plt.ylabel('Count', fontsize=12)  # Y-axis represents frequency count

    # Add a grid for easier reading of the y-axis values
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Ensure the y-axis (count) starts at 0
    plt.ylim(bottom=0)

    # Save the figure as specified
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

    # Close the plot figure to free up memory
    plt.close()

except FileNotFoundError:
    # Handle case where file isn't found
    print("Error: File 'data.csv' not found in the current directory.")
except KeyError as e:
    # Handle case where the expected column isn't in the file
    print(f"Error: {e}")
except Exception as e:
    # Handle other potential errors (e.g., empty file, permissions)
    print(f"An unexpected error occurred: {e}")
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# Set a colorblind-friendly style for better contrast and accessibility
matplotlib.style.use('seaborn-v0_8-colorblind')

try:
    # Read the data from the CSV file
    df = pd.read_csv("data.csv")

    # Check if the expected column is present
    if "Particle Size (mm)" not in df.columns:
        print("Error: 'Particle Size (mm)' column not found in data.csv")
    else:
        # Extract the data
        particle_size = df["Particle Size (mm)"]

        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Plot the histogram
        # Using 'auto' for binning to let matplotlib choose a reasonable number of bins
        plt.hist(particle_size, bins='auto', edgecolor='black', alpha=0.8)

        # Set title and labels
        plt.title("Distribution of Particle Size", fontsize=16)
        plt.xlabel("Particle Size (mm)", fontsize=12)
        plt.ylabel("Count", fontsize=12)

        # Add a grid for better readability
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # Ensure y-axis starts at 0
        plt.ylim(bottom=0)

        # Save the figure
        plt.savefig("chart.png", dpi=150, bbox_inches='tight')

except FileNotFoundError:
    print(f"Error: The file 'data.csv' was not found.")
except pd.errors.EmptyDataError:
    print("Error: The file 'data.csv' is empty.")
except Exception as e:
    print(f"An error occurred: {e}")
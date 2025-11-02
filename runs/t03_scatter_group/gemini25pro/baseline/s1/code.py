import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
try:
    df = pd.read_csv("data.csv")

    # Create a figure and axes
    fig, ax = plt.subplots()

    # Get unique groups
    groups = df['Group'].unique()

    # Define colors for groups (optional, matplotlib handles it automatically,
    # but explicit definition can be clearer if needed)
    # colors = plt.cm.get_cmap('tab10', len(groups))
    # color_map = dict(zip(groups, colors.colors))

    # Plot each group
    for group in groups:
        subset = df[df['Group'] == group]
        ax.scatter(
            subset['Age (years)'], 
            subset['Total Cholesterol (mg/dL)'], 
            label=group, 
            alpha=0.7,  # Mitigate overplotting
            s=10        # Use small markers
        )

    # Set labels with units
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Total Cholesterol (mg/dL)")

    # Add a legend
    ax.legend(title="Group")
    
    # Set title
    ax.set_title("Total Cholesterol vs. Age by Group")
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.6)

    # Save the figure
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

    # Close the plot figure to free up memory
    plt.close(fig)

except FileNotFoundError:
    print("Error: data.csv not found.")
except Exception as e:
    print(f"An error occurred: {e}")
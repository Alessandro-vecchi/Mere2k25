import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_small_multiples():
    # Read the data
    # Using "A.csv" as it's the provided file name, overriding "data.csv" from prompt
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        print("Error: 'A.csv' not found. Please ensure the file is in the correct directory.")
        return

    # Convert month column to datetime objects
    try:
        df['month'] = pd.to_datetime(df['month'], format='%B %Y')
    except ValueError:
        print("Error: Could not parse 'month' column. Ensure it's in 'Month Year' format (e.g., 'January 2023').")
        return

    # Get sorted unique regions
    unique_regions = sorted(df['region'].unique())
    n_regions = len(unique_regions)

    if n_regions == 0:
        print("Error: No regions found in data.")
        return

    # Get a color map
    colors = plt.get_cmap('tab10').colors

    # Create subplots (facets), one for each region
    # Share x and y axes
    fig, axes = plt.subplots(
        n_regions, 1, 
        figsize=(10, 2.5 * n_regions), 
        sharex=True, 
        sharey=True
    )

    # Ensure 'axes' is always an array for consistent indexing
    if n_regions == 1:
        axes = [axes]

    handles = []
    labels = []

    # Iterate through each region and plot on its own subplot
    for i, region in enumerate(unique_regions):
        ax = axes[i]
        
        # Filter data for the region and sort by month
        region_data = df[df['region'] == region].sort_values('month')
        
        if not region_data.empty:
            # Plot the data
            color = colors[i % len(colors)]
            line, = ax.plot(
                region_data['month'], 
                region_data['value'], 
                color=color, 
                label=region
            )
            
            # Append line and label for the shared legend
            handles.append(line)
            labels.append(region)
        
        # Set the title for the subplot
        ax.set_title(region)
        ax.grid(True, linestyle='--', alpha=0.6)

    # --- Configure Shared Elements ---

    # Add a single, shared legend at the top of the figure
    fig.legend(
        handles, 
        labels, 
        loc='upper center', 
        bbox_to_anchor=(0.5, 1.02),  # Position above the top subplot
        ncol=min(4, n_regions)      # Adjust columns based on number of regions
    )

    # Set shared y-axis label
    fig.supylabel('Value', fontsize=12)

    # Configure x-axis (only for the bottom plot)
    ax_bottom = axes[-1]
    ax_bottom.set_xlabel('Month', fontsize=12)

    # Improve date formatting
    locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
    formatter = mdates.ConciseDateFormatter(locator)
    ax_bottom.xaxis.set_major_locator(locator)
    ax_bottom.xaxis.set_major_formatter(formatter)

    # Adjust layout to prevent overlap and make room for legend
    # rect leaves space at the top [left, bottom, right, top]
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the figure
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
    
    # Close the figure to free memory
    plt.close(fig)

if __name__ == "__main__":
    plot_small_multiples()
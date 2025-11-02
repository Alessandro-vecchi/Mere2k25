import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def main():
    # Read the CSV file
    try:
        data = pd.read_csv("data.csv")
    except FileNotFoundError:
        print("Error: data.csv not found. Make sure the file is in the correct directory.")
        return
    except Exception as e:
        print(f"Error reading data.csv: {e}")
        return

    # Check for required columns
    required_cols = ['Age (years)', 'Total Cholesterol (mg/dL)', 'Group']
    if not all(col in data.columns for col in required_cols):
        print(f"Error: Missing one or more required columns: {required_cols}")
        print(f"Available columns: {data.columns.tolist()}")
        return

    # Get unique groups
    groups = data['Group'].unique()
    
    # Create a color map for the groups
    # Using 'tab10' colormap for good visual distinction and contrast
    colors = plt.cm.tab10(range(len(groups)))
    color_map = dict(zip(groups, colors))

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data for each group
    for group in groups:
        group_data = data[data['Group'] == group]
        ax.scatter(
            group_data['Age (years)'],
            group_data['Total Cholesterol (mg/dL)'],
            label=group,
            color=color_map[group],
            alpha=0.6,  # Mitigate overplotting
            s=15        # Use small markers
        )

    # Set titles and labels
    ax.set_title("Total Cholesterol vs. Age by Group", fontsize=16, pad=15)
    ax.set_xlabel("Age (years)", fontsize=12)
    ax.set_ylabel("Total Cholesterol (mg/dL)", fontsize=12)

    # Add legend
    ax.legend(title="Group", title_fontsize='11', fontsize='10', frameon=False, bbox_to_anchor=(1.04, 1), loc='upper left')

    # Add grid for readability
    ax.grid(True, linestyle='--', alpha=0.6)

    # Improve layout
    fig.tight_layout()

    # Save the figure
    try:
        fig.savefig("chart.png", dpi=150, bbox_inches='tight')
    except Exception as e:
        print(f"Error saving figure: {e}")
    finally:
        # Close the plot to free memory
        plt.close(fig)

if __name__ == "__main__":
    main()
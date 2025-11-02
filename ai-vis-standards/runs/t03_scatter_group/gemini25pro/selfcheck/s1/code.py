import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def main():
    # Read the CSV file
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        print("Error: data.csv not found.")
        return
    except Exception as e:
        print(f"Error reading data.csv: {e}")
        return

    # Check if required columns exist
    required_cols = ['Age (years)', 'Total Cholesterol (mg/dL)', 'Group']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Missing one or more required columns: {required_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return

    # Get unique groups
    groups = df['Group'].unique()
    
    # Create a color map for the groups
    # Using 'tab10' colormap which provides good distinct colors
    colors = plt.cm.tab10(range(len(groups)))
    color_map = dict(zip(groups, colors))

    # Create the plot
    fig, ax = plt.subplots()

    # Plot data for each group
    for group in groups:
        group_df = df[df['Group'] == group]
        ax.scatter(
            group_df['Age (years)'], 
            group_df['Total Cholesterol (mg/dL)'], 
            alpha=0.6,  # Mitigate overplotting
            s=20,       # Use slightly smaller markers
            color=color_map[group], 
            label=group,
            edgecolors='w', # Add a slight white edge for better separation
            linewidths=0.5
        )

    # Set labels and title
    ax.set_xlabel('Age (years)')
    ax.set_ylabel('Total Cholesterol (mg/dL)')
    ax.set_title('Total Cholesterol vs. Age by Group')

    # Add legend
    # Place legend outside the plot area to avoid obscuring data
    ax.legend(title='Group', bbox_to_anchor=(1.04, 1), loc='upper left')

    # Ensure layout is clean before saving
    # Note: bbox_inches='tight' in savefig often handles this, 
    # but explicit tight_layout() is good practice.
    try:
        fig.tight_layout()
    except Exception:
        # Fallback in case tight_layout fails
        pass

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
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

try:
    # Read the CSV file, assuming the first column is the index
    # Using "A.csv" as that is the file provided by the user.
    df = pd.read_csv("data.csv", index_col=0)

    # Get data, column labels, and index labels
    data = df.values
    col_labels = df.columns
    row_labels = df.index

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot the heatmap using imshow
    im = ax.imshow(data, cmap='coolwarm')

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel("Correlation Value", rotation=-90, va="bottom")

    # Set ticks and labels
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)
    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_title("Heatmap Matrix")

    # Save the figure
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

    # Close the plot to prevent display
    plt.close(fig)

except FileNotFoundError:
    print("Error: The file 'A.csv' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
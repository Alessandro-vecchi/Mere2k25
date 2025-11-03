import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

try:
    # Read the CSV file. Assuming the first column is the index.
    # Using "A.csv" as it's the file provided in context, despite the prompt mentioning "data.csv".
    df = pd.read_csv("A.csv", index_col=0)

    # Ensure data is numeric, coercing errors just in case
    # (though a correlation matrix should already be numeric)
    df = df.apply(pd.to_numeric, errors='coerce')

    # Create the figure and axes
    # Increase figure size to accommodate labels
    fig, ax = plt.subplots(figsize=(12, 10))

    # Define a diverging colormap (Red-White-Blue)
    # 'vmin' and 'vmax' are set to -1 and 1, standard for correlation
    cmap = 'RdBu_r'
    im = ax.imshow(df.values, cmap=cmap, vmin=-1, vmax=1)

    # Create the colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Correlation Coefficient", rotation=-90, va="bottom", labelpad=15)

    # Set ticks to match the DataFrame's index and columns
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns)
    ax.set_yticklabels(df.index)

    # Move x-axis labels to the top
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Rotate the x-tick (top) labels for readability
    plt.setp(ax.get_xticklabels(), rotation=-45, ha="left", rotation_mode="anchor")

    # Add text annotations for each cell
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            value = df.iloc[i, j]
            if pd.notna(value):
                # Use white text for dark colors (abs(corr) > 0.6)
                # Use black text for light colors (abs(corr) <= 0.6)
                text_color = "white" if abs(value) > 0.6 else "black"
                ax.text(j, i, f"{value:.2f}",
                        ha="center", va="center", color=text_color, fontsize=8)

    # Set the title
    ax.set_title("Correlation Heatmap Matrix", pad=20, fontsize=16)

    # Save the figure
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

    # Close the figure to free up memory
    plt.close(fig)

except FileNotFoundError:
    print("Error: 'A.csv' not found. Please ensure the file is in the correct directory.")
except Exception as e:
    print(f"An error occurred: {e}")
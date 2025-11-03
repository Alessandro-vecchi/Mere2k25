import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

def get_text_color(bg_color):
    """
    Determines whether black or white text has better contrast against a 
    given background color.
    
    Args:
    bg_color (tuple): RGB(A) color tuple (values 0-1).
    
    Returns:
    str: 'black' or 'white'.
    """
    # Calculate relative luminance (using WCAG formula)
    # L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    # Note: Assumes sRGB colorspace.
    r, g, b = bg_color[:3]
    
    # Gamma correction (approx.)
    r_c = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g_c = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b_c = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    
    luminance = 0.2126 * r_c + 0.7152 * g_c + 0.0722 * b_c
    
    # WCAG contrast ratio calculation
    # Contrast (Black) = (L_black + 0.05) / (L_bg + 0.05) 
    #   (L_black is approx 0) -> 0.05 / (luminance + 0.05) - this is wrong
    # Contrast (White) = (L_white + 0.05) / (L_bg + 0.05) = 1.05 / (luminance + 0.05)
    # Contrast (Black) = (L_bg + 0.05) / (L_black + 0.05) = (luminance + 0.05) / 0.05
    
    # Simpler threshold:
    # If luminance > 0.179 (per WCAG 1.4.3 on APCA), use black.
    # A common simpler heuristic is 0.5 for perceptual brightness.
    # Let's use the luminance directly:
    if luminance > 0.4: # This threshold is often good for perceptal balance
        return 'black'
    else:
        return 'white'

try:
    # Read the data, specifying the first column as the index
    # The user prompt mentioned "data.csv", but the uploaded file is "A.csv"
    df = pd.read_csv("data.csv", index_col=0)
    
    # Get data matrix and column/index labels
    data = df.values
    labels = df.columns
    
    # Create the figure and axes
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Determine value range and normalization
    val_min = np.min(data)
    val_max = np.max(data)
    
    # Use a diverging colormap if data spans 0 (typical for correlation)
    if val_min < 0 and val_max > 0:
        norm = mcolors.DivergingNorm(vcenter=0)
        cmap_name = 'coolwarm'
    else:
        norm = mcolors.Normalize(vmin=val_min, vmax=val_max)
        cmap_name = 'viridis'
        
    cmap = plt.get_cmap(cmap_name)

    # Create the heatmap
    im = ax.imshow(data, cmap=cmap, norm=norm, aspect='auto')
    
    # Create the colorbar and set its label
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation Coefficient') # Label based on file content
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    
    # Rotate the x-axis tick labels for readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
             
    # Add text annotations for the values
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = data[i, j]
            # Get the cell color from the colormap
            bg_color = cmap(norm(val))
            # Determine the best text color for contrast
            text_color = get_text_color(bg_color)
            
            ax.text(j, i, f"{val:.2f}",
                    ha="center", va="center", color=text_color, fontsize=8)

    # Set titles and labels
    ax.set_title('Heatmap Correlation Matrix')
    ax.set_xlabel('Variables')
    ax.set_ylabel('Variables')
    
    # Adjust layout to prevent label overlap (though bbox_inches='tight' helps)
    fig.tight_layout()
    
    # Save the figure as specified
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
    
    # Close the figure to free memory
    plt.close(fig)

except FileNotFoundError:
    # Handle file not found error
    print("Error: 'A.csv' not found.")
    # Create a dummy error plot if file not found, to still save *something*
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "Error: 'A.csv' not found.", 
            ha='center', va='center', color='red')
    ax.set_title("File Not Found Error")
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
except Exception as e:
    # Handle other potential errors
    print(f"An error occurred: {e}")
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f"An error occurred:\n{e}", 
            ha='center', va='center', color='red', wrap=True)
    ax.set_title("Plotting Error")
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
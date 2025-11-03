import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Load the dataset
# The user specified "data.csv" but the uploaded file is "A.csv".
# We will use the uploaded file name "A.csv".
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: 'A.csv' not found. Please ensure the file is in the correct directory.")
    exit()

# Prepare data for plotting
# Convert 'month' column to datetime objects
try:
    df['datetime'] = pd.to_datetime(df['month'], format='%B %Y')
except ValueError as e:
    print(f"Error parsing 'month' column: {e}")
    print("Please ensure 'month' column is in 'Month YYYY' format (e.g., 'January 2023').")
    exit()

# Extract year and month number (for plotting and sorting)
df['year'] = df['datetime'].dt.year
df['month_num'] = df['datetime'].dt.month

# Sort values to ensure lines are drawn correctly
df = df.sort_values(by=['region', 'year', 'month_num'])

# Get unique categories for facets (regions) and lines (years)
unique_regions = df['region'].unique()
unique_years = df['year'].unique()
n_regions = len(unique_regions)

# Create a color map for the years
colors = plt.cm.get_cmap('tab10', len(unique_years))
year_colors = {year: colors(i) for i, year in enumerate(unique_years)}

# Create the small-multiple subplots
# One row per region
fig, axes = plt.subplots(
    nrows=n_regions,
    ncols=1,
    figsize=(10, 2.5 * n_regions),
    sharex=True,  # Shared x-axis
    sharey=True   # Shared y-axis (as requested)
)

# Handle the case of a single region (where 'axes' is not an array)
if n_regions == 1:
    axes = [axes]

# Iterate over each region and plot on its corresponding axis
for ax, region in zip(axes, unique_regions):
    region_df = df[df['region'] == region]
    
    # Plot a separate line for each year
    for year in unique_years:
        year_df = region_df[region_df['year'] == year].sort_values('month_num')
        if not year_df.empty:
            ax.plot(
                year_df['month_num'],
                year_df['value'],
                label=year,
                color=year_colors[year],
                marker='.', # Add markers to distinguish points
                linestyle='-'
            )
    
    # Set the subplot title to the region name
    ax.set_title(region, loc='left', fontsize=12)
    
    # Add gridlines for readability
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Ensure text has good contrast
    ax.title.set_color('black')
    ax.tick_params(colors='black')

# Configure shared axes
# Set x-axis ticks to month abbreviations
month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Use setp to apply to all shared axes
plt.setp(axes, xticks=range(1, 13), xticklabels=month_labels)

# Set shared axis labels
axes[-1].set_xlabel("Month", fontsize=12, color='black') # Only on the bottom plot
# Use fig.supylabel for a single, centered shared y-axis label
fig.supylabel("Value", fontsize=12, color='black')

# Configure overall figure
fig.suptitle("Monthly Value by Region and Year", fontsize=16, fontweight='bold', color='black')
fig.tight_layout(rect=[0.05, 0.05, 0.85, 0.93]) # Adjust layout to make room for title and legend

# Create a single, shared legend
# Get handles and labels from one of the plots
handles, labels = axes[0].get_legend_handles_labels()
# Place legend outside the plot area
fig.legend(
    handles,
    labels,
    title="Year",
    loc='center left',
    bbox_to_anchor=(1, 0.5), # Position to the right of the plots
    fontsize=10,
    title_fontsize=11
)

# Save the figure
plt.savefig("chart.png", dpi=150, bbox_inches='tight')
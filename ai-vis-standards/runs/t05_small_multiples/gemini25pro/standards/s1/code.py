import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

# Load the dataset
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    # Handle file not found error
    print("Error: data.csv not found.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    # Handle other potential loading errors
    print(f"Error loading data: {e}", file=sys.stderr)
    sys.exit(1)

# Convert 'month' to datetime objects
try:
    df['datetime'] = pd.to_datetime(df['month'], format='%B %Y')
except ValueError as e:
    # Handle errors in date parsing
    print(f"Error parsing dates: {e}", file=sys.stderr)
    sys.exit(1)
except KeyError:
    # Handle missing 'month' column
    print("Error: 'month' column not found.", file=sys.stderr)
    sys.exit(1)

# Ensure 'region' column exists
if 'region' not in df.columns:
    print("Error: 'region' column not found.", file=sys.stderr)
    sys.exit(1)

# Ensure 'value' column exists
if 'value' not in df.columns:
    print("Error: 'value' column not found.", file=sys.stderr)
    sys.exit(1)

# Get unique regions and setup colors
regions = df['region'].unique()
regions.sort()  # Sort for consistent order
n_regions = len(regions)

# Get colors from a qualitative map
# Use tab10 and cycle if n_regions > 10
cmap = plt.colormaps['tab10']
colors_list = cmap.colors

# Create subplots
# Arrange in 2 columns, adjust rows as needed
ncols = 2
nrows = (n_regions + ncols - 1) // ncols
# Set a base figure size and scale
base_width = 12
base_height_per_row = 3.5
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, 
                         figsize=(base_width, nrows * base_height_per_row), 
                         sharey=True, squeeze=False)
axes_flat = axes.flatten() # Flatten for easy iteration

# Plot data for each region
for i, region in enumerate(regions):
    ax = axes_flat[i]
    color = colors_list[i % len(colors_list)]
    
    # Filter data for the current region and sort by date
    region_data = df[df['region'] == region].sort_values('datetime')
    
    if not region_data.empty:
        ax.plot(region_data['datetime'], region_data['value'], 
                marker='o', linestyle='-', markersize=4, label=region, color=color)
    
    # Set title for the subplot
    ax.set_title(region, fontsize=12, color='#333333')
    ax.grid(True, linestyle='--', alpha=0.6, color='#AAAAAA')
    
    # Format x-axis locators and formatters
    ax.xaxis.set_major_locator(mdates.YearLocator(1)) # Major tick every year
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10])) # Minor ticks every quarter
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
    
    # Set tick parameters for visibility and contrast
    ax.tick_params(axis='x', which='major', labelsize=10, length=6, color='#555555')
    ax.tick_params(axis='x', which='minor', labelsize=8, labelrotation=90, length=3, color='#777777')
    ax.tick_params(axis='y', labelsize=9, color='#555555') 

    # Set label colors for contrast
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.title.set_color('#111111')
    
    # Set tick label colors
    ax.tick_params(axis='x', colors='#333333')
    ax.tick_params(axis='y', colors='#333333')

    # Set spine colors for better contrast
    for spine in ax.spines.values():
        spine.set_edgecolor('#AAAAAA')

# Remove unused subplots if the number of regions is odd
for j in range(n_regions, len(axes_flat)):
    fig.delaxes(axes_flat[j])

# Set common X and Y labels for the entire figure
fig.supxlabel("Month", fontsize=14, y=0.01, color='#222222')
fig.supylabel("Value", fontsize=14, x=0.03, color='#222222')

# Set an overall title for the figure
fig.suptitle("Value Over Time by Region", fontsize=18, y=1.03, color='#000000', weight='bold')

# --- Add a single shared legend ---
# Create handles (lines) for the legend
handles = [plt.Line2D([0], [0], 
                      color=colors_list[k % len(colors_list)], 
                      lw=2, marker='o', markersize=5) 
           for k in range(n_regions)]
labels = regions

# Place legend centrally above the plots
leg = fig.legend(handles, labels, title="Region", 
           loc='upper center', 
           bbox_to_anchor=(0.5, 0.96), # Position legend below title
           ncol=min(n_regions, 6),     # Max 6 columns for legend
           fontsize=10, 
           title_fontsize=12, 
           frameon=False) # No border

# Set legend text colors for contrast
plt.setp(leg.get_texts(), color='#333333')
plt.setp(leg.get_title(), color='#111111')

# Adjust layout to prevent overlap and make space for title/legend
# rect=[left, bottom, right, top] in figure coordinates
fig.tight_layout(rect=[0.04, 0.05, 1, 0.93])

# Save the figure
try:
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving figure: {e}", file=sys.stderr)
    sys.exit(1)
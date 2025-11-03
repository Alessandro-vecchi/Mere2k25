import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the dataset
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    print("Error: data.csv not found.")
    exit()
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit()

# Data validation and preparation
if 'date' not in df.columns or \
   'Precipitation (mm)' not in df.columns or \
   'Discharge (cubic meters per second)' not in df.columns:
    print("Error: Required columns are missing.")
    print(f"Columns found: {df.columns.tolist()}")
    exit()

# Convert date column to datetime objects
try:
    # Remove any potential surrounding quotes from the date string
    df['date'] = df['date'].str.strip('"')
    df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y')
except ValueError as e:
    print(f"Error parsing dates: {e}")
    print("Please ensure date format is like 'January 01, 2024'.")
    exit()

# Convert numeric columns, handling potential errors
df['Precipitation (mm)'] = pd.to_numeric(
    df['Precipitation (mm)'], errors='coerce'
)
df['Discharge (cubic meters per second)'] = pd.to_numeric(
    df['Discharge (cubic meters per second)'], errors='coerce'
)

# Drop rows where conversion failed
df.dropna(subset=[
    'date', 'Precipitation (mm)', 'Discharge (cubic meters per second)'
], inplace=True)

# Sort by date
df.sort_values('date', inplace=True)

# Create two vertically stacked subplots sharing the x-axis
# This is preferred over a dual y-axis as the units are different
fig, (ax1, ax2) = plt.subplots(
    nrows=2, 
    ncols=1, 
    figsize=(12, 8), 
    sharex=True, 
    dpi=150
)

# Plot Precipitation on the first (top) axis
color1 = 'tab:blue'
ax1.plot(
    df['date'], 
    df['Precipitation (mm)'], 
    color=color1, 
    marker='.', 
    linestyle='-', 
    label='Precipitation'
)
ax1.set_ylabel('Precipitation (mm)', color=color1)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_title('Daily Precipitation')
ax1.grid(True, linestyle='--', alpha=0.6)

# Plot Discharge on the second (bottom) axis
color2 = 'tab:green'
ax2.plot(
    df['date'], 
    df['Discharge (cubic meters per second)'], 
    color=color2, 
    marker='.', 
    linestyle='-', 
    label='Discharge'
)
ax2.set_ylabel('Discharge (cubic meters per second)', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_title('Daily River Discharge')
ax2.grid(True, linestyle='--', alpha=0.6)

# Format the shared x-axis
ax2.set_xlabel('Date')
# Use concise date formatting
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# Rotate date labels for readability
fig.autofmt_xdate(rotation=45)

# Add a main title for the entire figure
fig.suptitle(
    'River Discharge and Precipitation Over Time', 
    fontsize=16, 
    fontweight='bold'
)

# Adjust layout to prevent titles/labels from overlapping
# Add space at the top for the suptitle
fig.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save the figure
try:
    plt.savefig('chart.png', dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving figure: {e}")
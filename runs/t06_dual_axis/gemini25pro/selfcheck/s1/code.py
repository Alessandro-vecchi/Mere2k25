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
    print(f"Error loading data.csv: {e}")
    exit()

# Clean column names (remove potential leading/trailing spaces)
df.columns = df.columns.str.strip()

# Verify required columns exist
required_cols = ['date', 'Precipitation (mm)', 'Discharge (cubic meters per second)']
if not all(col in df.columns for col in required_cols):
    print(f"Error: Missing one or more required columns: {required_cols}")
    print(f"Available columns: {df.columns.tolist()}")
    exit()

# Convert 'date' column to datetime objects
try:
    df['date'] = pd.to_datetime(df['date'], format='"%B %d, %Y"')
except ValueError as e:
    print(f"Error parsing date column: {e}")
    # Attempt alternative common formats if needed, or exit
    try:
        # If the quotes weren't consistent, try without them
        df['date'] = pd.to_datetime(df['date'].str.strip('"'), format='%B %d, %Y')
    except Exception as e2:
        print(f"Could not parse dates. Error: {e2}")
        exit()


# Create two subplots sharing the x-axis
# Using two panels is preferred over dual y-axes for clarity
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Plot Precipitation on the first (top) panel
color1 = '#0072B2' # A clear blue
ax1.plot(df['date'], df['Precipitation (mm)'], color=color1, marker='o', markersize=3, linestyle='-')
ax1.set_ylabel('Precipitation (mm)', color='black', fontsize=12)
ax1.set_title('Daily Precipitation', fontsize=14, pad=10)
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(True, linestyle='--', alpha=0.6)

# Plot Discharge on the second (bottom) panel
color2 = '#D55E00' # A clear orange/brown
ax2.plot(df['date'], df['Discharge (cubic meters per second)'], color=color2, marker='s', markersize=3, linestyle='-')
ax2.set_ylabel('Discharge (m³/s)', color='black', fontsize=12) # Using m³/s for brevity
ax2.set_title('Daily Discharge', fontsize=14, pad=10)
ax2.tick_params(axis='y', labelcolor='black')
ax2.grid(True, linestyle='--', alpha=0.6)

# Format the shared x-axis
ax2.set_xlabel('Date', fontsize=12)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45, ha='right')

# Add a main title for the entire figure
fig.suptitle('Hydrological Data Over Time (Jan-Mar 2024)', fontsize=16, y=1.02)

# Adjust layout to prevent overlap
plt.tight_layout(rect=[0, 0.03, 1, 0.98]) # Adjust rect to make space for suptitle

# Save the figure
try:
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving figure: {e}")
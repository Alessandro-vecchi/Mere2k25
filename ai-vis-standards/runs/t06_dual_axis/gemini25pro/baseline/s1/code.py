import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV data
# The CSV has quoted date strings, which pandas parse_dates can handle.
try:
    df = pd.read_csv('data.csv', parse_dates=['date'])
except FileNotFoundError:
    print("Error: 'data.csv' not found.")
    # Create dummy data if file not found, to allow script to run
    import numpy as np
    from datetime import datetime, timedelta
    base = datetime(2024, 1, 1)
    dates = [base + timedelta(days=i) for i in range(100)]
    precip = np.random.randint(0, 15, size=100)
    discharge = np.abs(np.random.randn(100).cumsum() * 10 + 50 + np.random.rand(100) * 20)
    df = pd.DataFrame({
        'date': dates,
        'Precipitation (mm)': precip,
        'Discharge (cubic meters per second)': discharge
    })
except Exception as e:
    print(f"Error reading 'data.csv': {e}")
    exit()

# Extract data for plotting
dates = df['date']
precip = df['Precipitation (mm)']
discharge = df['Discharge (cubic meters per second)']

# Create a figure with two vertically stacked subplots (panels)
# sharex=True links the x-axes, so zooming/panning one affects the other.
fig, (ax1, ax2) = plt.subplots(
    nrows=2,
    ncols=1,
    sharex=True,
    figsize=(10, 8),
    gridspec_kw={'height_ratios': [1, 2]} # Give more space to discharge plot
)

# --- Top Panel: Precipitation ---
ax1.bar(dates, precip, color='tab:blue', alpha=0.7, width=1, label='Precipitation')
ax1.set_ylabel('Precipitation (mm)', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.grid(axis='y', linestyle='--', alpha=0.7)
# Invert y-axis for precipitation (common in hydrology to show it "falling")
ax1.invert_yaxis()
ax1.set_title('Hydrological Data Over Time (Two Panel Approach)', pad=20)


# --- Bottom Panel: Discharge ---
ax2.plot(dates, discharge, color='tab:green', marker='o', markersize=2, linestyle='-', label='Discharge')
ax2.set_ylabel('Discharge (cubic m/s)', color='tab:green')
ax2.tick_params(axis='y', labelcolor='tab:green')
ax2.grid(True, linestyle='--', alpha=0.7)

# --- X-Axis Formatting (Shared) ---
ax2.set_xlabel('Date')
# Format the date display
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# Rotate date labels for better readability
fig.autofmt_xdate(rotation=45)

# Adjust layout to prevent labels from overlapping
fig.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust rect to make space for suptitle

# Save the figure as specified
try:
    plt.savefig('chart.png', dpi=150, bbox_inches='tight')
except Exception as e:
    print(f"Error saving figure: {e}")

# Close the plot figure to free memory (as plt.show() is not called)
plt.close(fig)
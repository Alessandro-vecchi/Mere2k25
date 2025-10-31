import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV file
df = pd.read_csv("data.csv")

# Convert 'date' column to datetime objects
# This correctly parses "Month YYYY" format
df['date'] = pd.to_datetime(df['date'], format='%B %Y')

# Sort by date to ensure the line plot connects points in order
df = df.sort_values('date')

# Create a figure and axes for the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the temperature data as a line with markers
# This inherently handles gaps, as it only plots existing points
ax.plot(df['date'], df['Temperature (°C)'], marker='o', linestyle='-')

# Set the title and axis labels
ax.set_title("Monthly Temperature Trend")
ax.set_xlabel("Date")
ax.set_ylabel("Temperature (°C)")

# --- Configure x-axis ticks for readability ---
# Set major ticks to appear quarterly (every 3 months)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

# Set minor ticks to appear monthly
ax.xaxis.set_minor_locator(mdates.MonthLocator())

# Format the major tick labels as 'YYYY-MM'
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Add a grid for easier reading
ax.grid(True, linestyle='--', alpha=0.6)

# Rotate date labels to prevent overlap
fig.autofmt_xdate()

# Save the figure to "chart.png"
plt.savefig("chart.png", dpi=150, bbox_inches='tight')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

# Set a non-GUI backend to prevent errors in environments without display
import matplotlib
matplotlib.use('Agg')

try:
    # Load the dataset
    file_path = "data.csv"
    df = pd.read_csv(file_path)

    # Convert 'date' column to datetime objects
    # This is crucial for plotting time series data correctly
    df['date'] = pd.to_datetime(df['date'], format='%B %Y')

    # Sort by date to ensure the line connects points chronologically
    df = df.sort_values(by='date')

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the line chart
    # Using markers clearly indicates the specific months data exists for
    ax.plot(df['date'], df['Temperature (°C)'], marker='o', linestyle='-')

    # --- Set titles and labels ---
    ax.set_title("Monthly Temperature Trend (Gaps Shown)", fontsize=16)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Temperature (°C)", fontsize=12) # Label y with unit

    # --- Configure X-axis ticks for readability (quarterly) ---
    # Set major ticks to appear every 3 months
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    
    # Format the tick labels as 'Jan 2020'
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    # Rotate date labels for better fit
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # --- Apply styling for readability ---
    # Add a light grid for the y-axis to help read values
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Ensure plot elements don't overlap
    # Note: bbox_inches='tight' in savefig also helps, but this is good practice
    fig.tight_layout()

    # --- Save the figure ---
    # Save the chart as "chart.png" with specified DPI and bounding box
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
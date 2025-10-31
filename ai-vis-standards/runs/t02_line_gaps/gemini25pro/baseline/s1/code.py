import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the dataset
try:
    df = pd.read_csv("data.csv")

    # Convert 'date' column to datetime objects
    # This is crucial for correct temporal plotting
    df['date'] = pd.to_datetime(df['date'], format='%B %Y')

    # Set the 'date' as the index
    df = df.set_index('date')
    
    # Sort the index to ensure the line connects points in chronological order
    df = df.sort_index()

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot the data. Pandas plotting with a datetime index
    # will naturally leave gaps for missing months if those rows don't exist.
    df['Temperature (°C)'].plot(ax=ax, marker='o', linestyle='-', markersize=5)

    # Set labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Monthly Temperature Trend (with Gaps for Missing Data)")

    # Customize x-axis ticks for reasonable density (e.g., quarterly)
    # Use MonthLocator to place ticks every 3 months
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    
    # Format the tick labels to show 'Month Year' (e.g., 'Jan 2020')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    # Improve layout and readability
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Save the figure
    fig.savefig("chart.png", dpi=150, bbox_inches='tight')

    # Close the plot figure to free up memory
    plt.close(fig)

except FileNotFoundError:
    print("Error: data.csv not found in the current directory.")
except Exception as e:
    print(f"An error occurred: {e}")
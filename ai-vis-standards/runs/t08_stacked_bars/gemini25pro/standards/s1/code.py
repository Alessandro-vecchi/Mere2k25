import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Read the data from the CSV file
try:
    df = pd.read_csv("data.csv")

    # Set 'country' as the index for plotting categories
    df = df.set_index('country')

    # Calculate the total production for each country
    df_total = df.sum(axis=1)

    # Calculate the percentage for each energy source
    # Divide each column by the total, then multiply by 100
    df_percent = df.div(df_total, axis=0) * 100

    # Create the stacked bar chart
    ax = df_percent.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Set title and labels
    ax.set_title('Energy Production Mix by Country')
    ax.set_xlabel('Country')
    ax.set_ylabel('Percentage (%)')

    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    # Add a legend and place it outside the plot
    ax.legend(title='Energy Source', bbox_to_anchor=(1.02, 1), loc='upper left')

    # Ensure bars start at zero (default for bar plots)
    ax.set_ylim(bottom=0, top=100) # Percentages sum to 100

    # Add horizontal grid lines for readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Save the figure
    plt.savefig("chart.png", dpi=150, bbox_inches='tight')

except FileNotFoundError:
    print("Error: data.csv not found.")
except Exception as e:
    print(f"An error occurred: {e}")
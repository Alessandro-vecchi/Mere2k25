import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the data
df = pd.read_csv("data.csv")
df["date"] = pd.to_datetime(df["date"], format="%B %Y")

# Set plotting style for contrast
plt.style.use('seaborn-v0_8-colorblind')

fig, ax = plt.subplots(figsize=(10, 5))

# Plot line with visible gaps for missing months
ax.plot(df["date"], df["Temperature (°C)"], marker='o', linestyle='-', color='#0072B2', label="Temperature")

# Format x-axis: show quarterly ticks, rotate labels
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

# Titles and labels with units
ax.set_title("Monthly Temperature Trend (2020-2022)")
ax.set_xlabel("Month")
ax.set_ylabel("Temperature (°C)")

# Grid for readability
ax.grid(True, which='major', axis='y', linestyle='--', alpha=0.7)

# Add legend
ax.legend()

# Tight layout and save figure
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

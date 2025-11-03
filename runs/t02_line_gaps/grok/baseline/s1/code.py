import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV assuming columns are 'Month' and 'Value' (adjust column names as needed)
data = pd.read_csv('data.csv')

# Detect which column is for months/date
date_col = None
for col in data.columns:
    if data[col].dtype == object and (
        "month" in col.lower() or "date" in col.lower()
    ):
        date_col = col
        break

if not date_col:
    date_col = data.columns[0]

data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
data = data.sort_values(date_col)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(data[date_col], data['Value'], marker='o', linestyle='-')

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
fig.autofmt_xdate()

ax.set_xlabel('Month')
ax.set_ylabel('Value (unit)')
ax.set_title('Monthly Trend')

plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.close()

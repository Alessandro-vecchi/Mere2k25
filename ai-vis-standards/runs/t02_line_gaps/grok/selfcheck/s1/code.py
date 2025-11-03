import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read data
df = pd.read_csv('data.csv', parse_dates=[0])

# Try to infer labels
possible_date_cols = [col for col in df.columns if 'date' in col.lower() or 'month' in col.lower()]
possible_y_cols = [col for col in df.columns if col not in possible_date_cols]
date_col = possible_date_cols[0]
y_col = possible_y_cols[0]

# Set up plot
fig, ax = plt.subplots(figsize=(8, 4))

# Line plot (show gaps for missing months)
df = df.sort_values(date_col)
ax.plot(df[date_col], df[y_col], marker='o', color='#1765ab', label=y_col)

# x-ticks: quarterly density
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=30, ha='right')

# Labels and title
ax.set_title('Monthly Trend', fontsize=13)
ax.set_xlabel('Month')
unit = ''
if '(' in y_col and ')' in y_col:
    # Extract unit from column name
    import re
    m = re.search(r'\((.*?)\)', y_col)
    if m:
        unit = m.group(1)
ax.set_ylabel(f'{y_col}' + (f' [{unit}]' if unit else ''))

# Legend
ax.legend()

# Improve readability
ax.grid(True, which='major', linestyle='--', alpha=0.5)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Tighten, save
plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.close()

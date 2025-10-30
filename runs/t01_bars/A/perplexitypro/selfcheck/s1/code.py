import pandas as pd
import matplotlib.pyplot as plt

# Read the data
df = pd.read_csv("data.csv", sep=r"\s{2,}|\t|,", engine="python")
df.columns = [col.strip() for col in df.columns]

# Rename columns for clarity if necessary
if "SiteConcentration" in df.columns:
    # split the combined column if present (as in unstructured CSV content above)
    df[['Site', 'Concentration']] = df['SiteConcentration'].str.extract(r'([A-Za-z\s]+)([\d.]+)')
    df['Site'] = df['Site'].str.strip()
    df['Concentration'] = df['Concentration'].astype(float)
    df = df[['Site', 'Concentration']]

# Sort descending
df = df.sort_values(by='Concentration', ascending=False)

# Prepare bar chart
plt.figure(figsize=(10, 6))
bars = plt.bar(df['Site'], df['Concentration'], color='#3E6FB0', edgecolor='black')

plt.title('River Sites Ranked by Concentration', fontsize=14)
plt.xlabel('Site', fontsize=12)
plt.ylabel('Concentration (mg/L)', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
plt.ylim(bottom=0)

plt.tight_layout()
plt.savefig('chart.png', dpi=150, bbox_inches='tight')

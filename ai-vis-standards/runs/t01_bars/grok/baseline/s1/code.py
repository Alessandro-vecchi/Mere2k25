import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data.csv")
df = df.dropna(subset=["Concentration (milligrams per liter)"])
df["Concentration (milligrams per liter)"] = df["Concentration (milligrams per liter)"].astype(float)
df_sorted = df.sort_values("Concentration (milligrams per liter)", ascending=False)

plt.figure(figsize=(8, 5))
bars = plt.bar(df_sorted["Site"], df_sorted["Concentration (milligrams per liter)"])
plt.xticks(rotation=45, ha="right")
plt.ylabel("Concentration (mg/L)")
plt.title("River Sites Ranked by Concentration (mg/L)")
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches='tight')

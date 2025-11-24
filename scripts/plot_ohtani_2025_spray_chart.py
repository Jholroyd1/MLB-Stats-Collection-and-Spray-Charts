import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('../data/ohtani_2025_spray_chart.csv')

plt.figure(figsize=(10, 10))
plt.scatter(df['coord_x'], df['coord_y'], alpha=0.7, edgecolors='k')
plt.title("Shohei Ohtani 2025 Batted Ball Spray Chart")
plt.xlabel("X Coordinate (ft)")
plt.ylabel("Y Coordinate (ft)")
plt.xlim(0, 250)
plt.ylim(0, 250)
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('../data/ohtani_2025_spray_chart.png', dpi=300)
plt.show()

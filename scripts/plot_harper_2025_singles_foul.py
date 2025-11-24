import matplotlib.pyplot as plt

# Bryce Harper 2025 singles: (coord_x, coord_y, distance)
points = [
    (126.0, 204.5, 99.0),
    (46.73, 130.94, 241.0),
    (156.96, 170.28, 110.0),
]

fig, ax = plt.subplots(figsize=(6, 6))

for x, y, dist in points:
    ax.scatter(x, y, s=80, label=f"Distance: {dist}")

ax.set_xlabel("coord_x")
ax.set_ylabel("coord_y")
ax.set_title("Bryce Harper 2025 Singles (Foul Territory Events)")
ax.legend()
ax.set_aspect('equal')
plt.tight_layout()
plt.show()

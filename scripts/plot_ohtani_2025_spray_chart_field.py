import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patheffects import withStroke
import numpy as np

# Load the data

# Load the data

# Load and shift data so home plate is (0,0)
df = pd.read_csv('../data/ohtani_2025_spray_chart.csv')
if df['coord_x'].min() > 50:  # If not already shifted
	df['coord_x'] = df['coord_x'] - 125

# Field geometry
home_plate = np.array([0, 0])
first_base = np.array([90, 0])
second_base = np.array([90, 90])
third_base = np.array([0, 90])
mound = np.array([60.5, 0])

# Outfield fence: 400ft to center, 330ft to corners
fence_points = []
for angle in np.linspace(45, 135, 200):
	rad = np.deg2rad(angle)
	# Linear interpolation between 330 (corners) and 400 (center)
	dist = 330 + (400-330)*np.cos(np.deg2rad(angle-90))
	x = dist * np.cos(rad)
	y = dist * np.sin(rad)
	fence_points.append([x, y])
fence_points = np.array(fence_points)


# Plot
fig, ax = plt.subplots(figsize=(7, 7))


# Draw outfield grass fill
outfield_poly = plt.Polygon(fence_points, closed=True, color='#cbe7ea', zorder=1)
ax.add_patch(outfield_poly)

# Draw infield dirt (arc)
infield_arc = patches.Arc(home_plate, 180, 180, theta1=0, theta2=90, color='white', lw=2, zorder=3)
ax.add_patch(infield_arc)
infield_arc2 = patches.Arc(home_plate, 180, 180, theta1=90, theta2=180, color='white', lw=2, zorder=3)
ax.add_patch(infield_arc2)

# Draw basepaths (white lines)
ax.plot([home_plate[0], first_base[0]], [home_plate[1], first_base[1]], color='white', lw=2, zorder=4)
ax.plot([first_base[0], second_base[0]], [first_base[1], second_base[1]], color='white', lw=2, zorder=4)
ax.plot([second_base[0], third_base[0]], [second_base[1], third_base[1]], color='white', lw=2, zorder=4)
ax.plot([third_base[0], home_plate[0]], [third_base[1], home_plate[1]], color='white', lw=2, zorder=4)

# Draw bases (white squares)
base_size = 5
for base in [home_plate, first_base, second_base, third_base]:
	ax.add_patch(patches.Rectangle(base - base_size/2, base_size, base_size, color='white', ec='black', zorder=10))


# Draw mound
mound_radius = 9
ax.add_patch(patches.Circle(mound, mound_radius, edgecolor='gray', facecolor='#e6d3b3', lw=1, alpha=0.7, zorder=5))

# Draw basepaths
ax.plot([home_plate[0], first_base[0], second_base[0], third_base[0], home_plate[0]],
		[home_plate[1], first_base[1], second_base[1], third_base[1], home_plate[1]], color='gray', lw=2)


# Draw outfield fence
ax.plot(fence_points[:,0], fence_points[:,1], color='#b2c7c7', lw=2, zorder=6)


# Draw foul lines
ax.plot([home_plate[0], fence_points[0,0]], [home_plate[1], fence_points[0,1]], color='#b2c7c7', lw=2, zorder=7)
ax.plot([home_plate[0], fence_points[-1,0]], [home_plate[1], fence_points[-1,1]], color='#b2c7c7', lw=2, zorder=7)


# Plot batted balls (colored dots with white outline)
ax.scatter(df['coord_x'], df['coord_y'], alpha=0.85, c='#e6550d', edgecolors='white', linewidths=1.5, s=60, zorder=20)


# Fence distance labels
ax.text(fence_points[0,0], fence_points[0,1]-15, '330', color='#b2c7c7', fontsize=16, ha='center', va='center', fontweight='bold')
ax.text(fence_points[-1,0], fence_points[-1,1]-15, '330', color='#b2c7c7', fontsize=16, ha='center', va='center', fontweight='bold')
ax.text(0, 410, '410', color='#b2c7c7', fontsize=16, ha='center', va='center', fontweight='bold')
ax.text(fence_points[40,0], fence_points[40,1]+15, '387', color='#b2c7c7', fontsize=16, ha='center', va='center', fontweight='bold')
ax.text(fence_points[-40,0], fence_points[-40,1]+15, '387', color='#b2c7c7', fontsize=16, ha='center', va='center', fontweight='bold')

# Remove axes and grid for a clean look
ax.set_xlim(-50, 450-125)
ax.set_ylim(-50, 450)
ax.set_aspect('equal', adjustable='box')
ax.axis('off')
plt.tight_layout()
plt.savefig('../data/ohtani_2025_spray_chart_real_field.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.show()

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

def rotate_point(x, y, angle_deg):
    angle_rad = np.deg2rad(angle_deg)
    xr = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    yr = x * np.sin(angle_rad) + y * np.cos(angle_rad)
    return xr, yr

home_plate = rotate_point(0, 0, 45)
first_base = rotate_point(127.28, 0, 45)
second_base = rotate_point(127.28, 127.28, 45)
third_base = rotate_point(0, 127.28, 45)
mound = rotate_point(60.5, 60.5, 45)

fence_points = []
for angle in np.linspace(-45, 45, 200):
    rad = np.deg2rad(angle)
    dist = 330 + (400-330)*np.cos(np.deg2rad(angle))
    x = dist * np.sin(rad)
    y = dist * np.cos(rad)
    fence_points.append([x, y])
fence_points = np.array(fence_points)

fig, ax = plt.subplots(figsize=(7, 7))

# Outfield fill (white)
outfield_poly = plt.Polygon(fence_points, closed=True, color='white', zorder=1)
ax.add_patch(outfield_poly)

# Basepaths (black)
ax.plot([home_plate[0], first_base[0]], [home_plate[1], first_base[1]], color='black', lw=2, zorder=4)
ax.plot([first_base[0], second_base[0]], [first_base[1], second_base[1]], color='black', lw=2, zorder=4)
ax.plot([second_base[0], third_base[0]], [second_base[1], third_base[1]], color='black', lw=2, zorder=4)
ax.plot([third_base[0], home_plate[0]], [third_base[1], home_plate[1]], color='black', lw=2, zorder=4)

# Bases (white with black edge)
base_size = 5
for base in [home_plate, first_base, second_base, third_base]:
    ax.add_patch(patches.Rectangle(np.array(base) - base_size/2, base_size, base_size, color='white', ec='black', zorder=10))

# Mound (white with black edge)
mound_radius = 9
ax.add_patch(patches.Circle(mound, mound_radius, edgecolor='black', facecolor='white', lw=1, alpha=0.7, zorder=5))

# Outfield fence (black)
ax.plot(fence_points[:,0], fence_points[:,1], color='black', lw=2, zorder=6)

# Foul lines (black)
ax.plot([home_plate[0], fence_points[0,0]], [home_plate[1], fence_points[0,1]], color='black', lw=2, zorder=7)
ax.plot([home_plate[0], fence_points[-1,0]], [home_plate[1], fence_points[-1,1]], color='black', lw=2, zorder=7)

# --- Load Ohtani batted ball data ---
columns = [
    'id','game_id','play_id','inning','half_inning','at_bat_index','play_time','event_type','event_description',
    'result_type','batter_id','pitcher_id','runner_on_first_id','runner_on_second_id','runner_on_third_id',
    'outs','balls','strikes','count','pitch_type','pitch_speed','runs_scored','rbi','created_at',
    'launch_speed','launch_angle','total_distance','trajectory','hardness','location','coord_x','coord_y'
]
data = pd.read_csv('../data/ohtani_2025_batted_balls.csv', sep='|', header=None, names=columns)

# Rotate batted ball coordinates by 45 deg CCW
rotated = data.apply(lambda row: rotate_point(row['coord_x'], row['coord_y'], 45), axis=1)
rotated = np.array(list(rotated))
plot_x = rotated[:,0]
plot_y = rotated[:,1]

ax.scatter(plot_x, plot_y, color='red', edgecolors='black', s=60, zorder=20, alpha=0.7)

ax.set_xlim(-350, 350)
ax.set_ylim(-50, 450)
ax.set_aspect('equal', adjustable='box')
ax.axis('off')
plt.tight_layout()
plt.savefig('../data/ohtani_2025_spray_chart_on_field_rotated.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.show()

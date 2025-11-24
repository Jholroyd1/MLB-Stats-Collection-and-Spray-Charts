import matplotlib.pyplot as plt
import os
import matplotlib.patches as patches
import numpy as np
import pandas as pd

def rotate_point(x, y, angle_deg):
    angle_rad = np.deg2rad(angle_deg)
    xr = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    yr = x * np.sin(angle_rad) + y * np.cos(angle_rad)
    return xr, yr

# Field geometry (diamond, 45 deg CCW)
home_plate = rotate_point(0, 0, 45)
first_base = rotate_point(127.28, 0, 45)
second_base = rotate_point(127.28, 127.28, 45)
third_base = rotate_point(0, 127.28, 45)
mound = rotate_point(60.5, 60.5, 45)


# Only run the main logic if this script is executed directly
if __name__ == "__main__":
    # Field fence points (for possible future use)
    fence_points = []
    for angle in np.linspace(-45, 45, 200):
        rad = np.deg2rad(angle)
        dist = 330 + (400-330)*np.cos(np.deg2rad(angle))
        fence_points.append((dist * np.cos(rad), dist * np.sin(rad)))

    # Load batted ball data
    columns = [
        'play_id','game_id','inning_side','inning','batting_order','half_inning','start_time','event','description',
        'play_type','batter_id','pitcher_id','runner_on_1b','runner_on_2b','runner_on_3b','outs','balls','strikes','pitch_count','count','rbi','runs','timestamp',
        'launch_speed','launch_angle','total_distance','trajectory','hardness','location','coord_x','coord_y'
    ]
    data = pd.read_csv('/Users/jackholroyd/MLB_Stats/data/ohtani_2025_batted_balls_cleaned.csv', delimiter='|', header=None, names=columns)

    # Flip and swap axes so home plate is at bottom center, center field at top center
    data['field_x'] = data['coord_y']
    data['field_y'] = -data['coord_x']

    # Diagnostics: print coordinate ranges
    print(f"Batted ball field_x (should be left-right): min {data['field_x'].min()}, max {data['field_x'].max()}")
    print(f"Batted ball field_y (should be home plate to CF): min {data['field_y'].min()}, max {data['field_y'].max()}")

    # Fix home run filter: match event string as it appears in the data
    print(f"Unique event values: {data['event'].unique()}")

    # Print all event values that are detected as home runs
    hr_mask = data['event'].str.contains('home_run|home run|homers|homer', case=False, na=False)
    print("Detected as home run events:")
    print(data.loc[hr_mask, 'event'])
    print("Full rows for detected home runs:")
    print(data.loc[hr_mask])
    hr = data[hr_mask]
    print(f"Home run field_y: min {hr['field_y'].min()}, max {hr['field_y'].max()}")

    # Scale and shift batted ball coordinates so farthest hit reaches the fence (400 ft)
    data['distance'] = np.sqrt(data['field_x']**2 + data['field_y']**2)
    max_dist = data['distance'].max()
    scale = 400.0 / max_dist if max_dist > 0 else 1.0
    print(f"Scaling factor: {scale}")
    data['field_x_scaled'] = data['field_x'] * scale
    data['field_y_scaled'] = data['field_y'] * scale
    hr['field_x_scaled'] = hr['field_x'] * scale
    hr['field_y_scaled'] = hr['field_y'] * scale

    # Draw field (with same transformation)
    def draw_field(ax):
        # Bases (90 ft apart)
        bases = np.array([[0,0], [90,0], [90,90], [0,90], [0,0]])
        # Apply same transform: swap and flip y
        bases_tf = np.stack([bases[:,1], -bases[:,0]], axis=1)
        ax.plot(bases_tf[:,0], bases_tf[:,1], 'k-')
        # Outfield arc (400 ft)
        theta = np.linspace(0, np.pi/2, 100)
        r = 400
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        arc = np.stack([y, -x], axis=1)
        ax.plot(arc[:,0], arc[:,1], 'k-')
        # Foul lines
        foul1 = np.stack([[0,0], [r,0]], axis=1)
        foul1_tf = np.stack([foul1[:,1], -foul1[:,0]], axis=1)
        foul2 = np.stack([[0,0], [0,r]], axis=1)
        foul2_tf = np.stack([foul2[:,1], -foul2[:,0]], axis=1)
        ax.plot(foul1_tf[:,0], foul1_tf[:,1], 'k-')
        ax.plot(foul2_tf[:,0], foul2_tf[:,1], 'k-')
        # Home plate
        ax.scatter([bases_tf[0,0]], [bases_tf[0,1]], color='k', s=30)
        # Diagnostics: print fence y range
        print(f"Fence field_y: min {arc[:,1].min()}, max {arc[:,1].max()}")

    fig, ax = plt.subplots(figsize=(10,7))
    draw_field(ax)
    # Plot all batted balls (scaled)
    ax.scatter(data['field_x_scaled'], data['field_y_scaled'], color='red', alpha=0.6, label='All batted balls')
    # Highlight home runs (scaled)
    ax.scatter(hr['field_x_scaled'], hr['field_y_scaled'], color='gold', edgecolor='black', label='Home runs')
    ax.set_aspect('equal')
    ax.legend()
    plt.tight_layout()
    # Save to absolute path in the data directory
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'ohtani_2025_spraychart_corrected.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
    print(f"Saved spray chart to {output_path}")
    plt.show()

import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys
import plotly.graph_objects as go
from datetime import datetime

DB_PATH = 'data/mlb_data.db'

# --- Field geometry (simple MLB field) ---
def draw_field(ax):
    home_plate = np.array([0, 0])
    first_base = np.array([90, 0])
    second_base = np.array([90, 90])
    third_base = np.array([0, 90])
    mound = np.array([60.5, 0])
    # Outfield fence: 400ft to center, 330ft to corners
    fence_points = []
    for angle in np.linspace(45, 135, 200):
        rad = np.deg2rad(angle)
        dist = 330 + (400-330)*np.cos(np.deg2rad(angle-90))
        x = dist * np.cos(rad)
        y = dist * np.sin(rad)
        fence_points.append([x, y])
    fence_points = np.array(fence_points)
    # Outfield grass
    outfield_poly = plt.Polygon(fence_points, closed=True, color='#cbe7ea', zorder=1)
    ax.add_patch(outfield_poly)
    # Basepaths
    ax.plot([home_plate[0], first_base[0], second_base[0], third_base[0], home_plate[0]],
            [home_plate[1], first_base[1], second_base[1], third_base[1], home_plate[1]], color='gray', lw=2)
    # Bases
    base_size = 5
    for base in [home_plate, first_base, second_base, third_base]:
        ax.add_patch(patches.Rectangle(base - base_size/2, base_size, base_size, color='white', ec='black', zorder=10))
    # Mound
    mound_radius = 9
    ax.add_patch(patches.Circle(mound, mound_radius, edgecolor='gray', facecolor='#e6d3b3', lw=1, alpha=0.7, zorder=5))
    # Outfield fence
    ax.plot(fence_points[:,0], fence_points[:,1], color='#b2c7c7', lw=2, zorder=6)
    # Foul lines
    ax.plot([home_plate[0], fence_points[0,0]], [home_plate[1], fence_points[0,1]], color='#b2c7c7', lw=2, zorder=7)
    ax.plot([home_plate[0], fence_points[-1,0]], [home_plate[1], fence_points[-1,1]], color='#b2c7c7', lw=2, zorder=7)
    # Fence distance labels
    ax.text(fence_points[0,0], fence_points[0,1]-15, '330', color='#b2c7c7', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(fence_points[-1,0], fence_points[-1,1]-15, '330', color='#b2c7c7', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(0, 410, '410', color='#b2c7c7', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.set_xlim(-50, 450-125)
    ax.set_ylim(-50, 450)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

def get_player_id(conn, player_name):
    # Try exact match, then fallback to LIKE
    cur = conn.cursor()
    cur.execute("SELECT player_id, full_name FROM players WHERE full_name = ? COLLATE NOCASE", (player_name,))
    row = cur.fetchone()
    if row:
        return row[0], row[1]
    cur.execute("SELECT player_id, full_name FROM players WHERE full_name LIKE ? COLLATE NOCASE", (f"%{player_name}%",))
    row = cur.fetchone()
    if row:
        return row[0], row[1]
    print(f"Player '{player_name}' not found in database.")
    sys.exit(1)

def query_batted_balls(conn, player_id, start_date, end_date):
    sql = '''
    SELECT pbp.coord_x, pbp.coord_y, pbp.event_type, g.game_date
    FROM play_by_play pbp
    JOIN games g ON pbp.game_id = g.game_id
    WHERE pbp.batter_id = ?
      AND pbp.coord_x IS NOT NULL AND pbp.coord_y IS NOT NULL
      AND g.game_date BETWEEN ? AND ?
    '''
    df = pd.read_sql_query(sql, conn, params=(player_id, start_date, end_date))
    return df

def main():
    parser = argparse.ArgumentParser(description="Create a spray chart for any player and date range.")
    parser.add_argument('--player', required=True, help='Player full name (case-insensitive)')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', default=None, help='Output PNG or HTML file (optional)')
    parser.add_argument('--html', action='store_true', help='If set, output an interactive HTML spray chart (Plotly)')
    args = parser.parse_args()

    # Validate dates
    try:
        datetime.strptime(args.start, '%Y-%m-%d')
        datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        print('Invalid date format. Use YYYY-MM-DD.')
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    player_id, player_name = get_player_id(conn, args.player)
    df = query_batted_balls(conn, player_id, args.start, args.end)
    conn.close()

    if df.empty:
        print(f"No batted ball data found for {player_name} between {args.start} and {args.end}.")
        sys.exit(0)

    # Statcast transformation (same as interactive script)
    def statcast_transform(hc_x, hc_y):
        x = 2.5 * (hc_x - 125.42)
        y = 2.5 * (198.27 - hc_y)
        return x, y

    statcast_x = []
    statcast_y = []
    event_types = []
    colors = []
    color_map = {
        'home_run': 'red',
        'single': 'green',
        'double': 'blue',
        'triple': 'purple',
    }
    for _, row in df.iterrows():
        hc_x = row['coord_x']
        hc_y = row['coord_y']
        event_type = row['event_type']
        x, y = statcast_transform(hc_x, hc_y)
        statcast_x.append(x)
        statcast_y.append(y)
        event_types.append(event_type)
        if event_type in color_map:
            colors.append(color_map[event_type])
        elif 'out' in event_type:
            colors.append('gray')
        else:
            colors.append('black')

    if args.html:
        # --- Plotly interactive chart ---
        fence_angles = np.linspace(-45, 45, 200)
        fence_x = []
        fence_y = []
        for angle in fence_angles:
            rad = np.deg2rad(angle)
            radius = 330 + (400 - 330) * np.cos(np.deg2rad(angle))
            fence_x.append(radius * np.sin(rad))
            fence_y.append(radius * np.cos(rad))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, 63, 0, -63, 0], y=[0, 63, 126, 63, 0], mode='lines', line=dict(color='black', width=2), showlegend=False))
        fig.add_trace(go.Scatter(x=fence_x, y=fence_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
        fig.add_trace(go.Scatter(x=[-63, fence_x[0]], y=[63, fence_y[0]], mode='lines', line=dict(color='black', width=2), showlegend=False))
        fig.add_trace(go.Scatter(x=[63, fence_x[-1]], y=[63, fence_y[-1]], mode='lines', line=dict(color='black', width=2), showlegend=False))
        hover_text = [f"Event: {etype}<br>x: {x:.1f} ft<br>y: {y:.1f} ft" for etype, x, y in zip(event_types, statcast_x, statcast_y)]
        fig.add_trace(go.Scatter(
            x=statcast_x, y=statcast_y, mode='markers',
            marker=dict(color='orange', size=8, line=dict(width=1, color='black')),
            text=hover_text, hoverinfo='text', name='Batted Balls'))
        margin_x = (max(statcast_x) - min(statcast_x)) * 0.1 if statcast_x else 50
        margin_y = (max(statcast_y) - min(statcast_y)) * 0.1 if statcast_y else 50
        xmin = min(-350, min(statcast_x) - margin_x)
        xmax = max(350, max(statcast_x) + margin_x)
        ymin = min(-20, min(statcast_y) - margin_y)
        ymax = max(450, max(statcast_y) + margin_y)
        fig.update_layout(
            title=f'Baseball Field with Standard MLB Outfield and Statcast Batted Balls: {player_name} ({args.start} to {args.end})',
            xaxis=dict(title='Feet (x)', range=[xmin, xmax], scaleanchor='y', scaleratio=1),
            yaxis=dict(title='Feet (y)', range=[ymin, ymax]),
            width=900, height=900,
            showlegend=False
        )
        if args.output:
            fig.write_html(args.output)
            print(f"Interactive spray chart saved to {args.output}")
        else:
            fig.show()
    else:
        fig, ax = plt.subplots(figsize=(9, 9))
        # Draw field geometry to match interactive
        home = (0, 0)
        first = (63, 63)
        second = (0, 126)
        third = (-63, 63)
        diamond_x = [home[0], first[0], second[0], third[0], home[0]]
        diamond_y = [home[1], first[1], second[1], third[1], home[1]]
        ax.plot(diamond_x, diamond_y, color='black', lw=2, zorder=10)
        fence_angles = np.linspace(-45, 45, 200)
        fence_x = []
        fence_y = []
        for angle in fence_angles:
            rad = np.deg2rad(angle)
            radius = 330 + (400 - 330) * np.cos(np.deg2rad(angle))
            fence_x.append(radius * np.sin(rad))
            fence_y.append(radius * np.cos(rad))
        ax.plot(fence_x, fence_y, color='black', lw=2, zorder=10)
        ax.plot([third[0], fence_x[0]], [third[1], fence_y[0]], color='black', lw=2, zorder=10)
        ax.plot([first[0], fence_x[-1]], [first[1], fence_y[-1]], color='black', lw=2, zorder=10)
        # Add scatter points with labels for legend
        from matplotlib.lines import Line2D
        event_label_map = {
            'home_run': 'Home Run',
            'single': 'Single',
            'double': 'Double',
            'triple': 'Triple',
            'out': 'Out/Other',
            'other': 'Other'
        }
        # Plot each event type separately for legend
        plotted = set()
        for i, (x, y, etype, color) in enumerate(zip(statcast_x, statcast_y, event_types, colors)):
            label = None
            if etype in color_map and color_map[etype] not in plotted:
                label = event_label_map[etype]
                plotted.add(color_map[etype])
            elif 'out' in etype and 'gray' not in plotted:
                label = event_label_map['out']
                plotted.add('gray')
            elif color == 'black' and 'black' not in plotted:
                label = event_label_map['other']
                plotted.add('black')
            ax.scatter(x, y, alpha=0.85, c=color, edgecolors='white', linewidths=1.5, s=60, zorder=20, label=label)
        # Custom legend handles
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Home Run', markerfacecolor='red', markersize=10, markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', label='Single', markerfacecolor='green', markersize=10, markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', label='Double', markerfacecolor='blue', markersize=10, markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', label='Triple', markerfacecolor='purple', markersize=10, markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', label='Out/Other', markerfacecolor='gray', markersize=10, markeredgecolor='black'),
            Line2D([0], [0], marker='o', color='w', label='Other', markerfacecolor='black', markersize=10, markeredgecolor='black'),
        ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11, frameon=True, title='Event Type')
    ax.set_title(f"Spray Chart: {player_name}\n{args.start} to {args.end}", fontsize=14)
    margin_x = (max(statcast_x) - min(statcast_x)) * 0.1 if statcast_x else 50
    margin_y = (max(statcast_y) - min(statcast_y)) * 0.1 if statcast_y else 50
    xmin = min(-350, min(statcast_x) - margin_x)
    xmax = max(350, max(statcast_x) + margin_x)
    ymin = min(-20, min(statcast_y) - margin_y)
    ymax = max(450, max(statcast_y) + margin_y)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    plt.tight_layout()
    if args.output:
        plt.savefig(args.output, dpi=300, bbox_inches='tight', pad_inches=0.05)
        print(f"Spray chart saved to {args.output}")
    else:
        plt.show()

if __name__ == '__main__':
    main()

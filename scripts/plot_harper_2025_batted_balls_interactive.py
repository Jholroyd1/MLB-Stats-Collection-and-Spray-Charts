import numpy as np
import csv
import plotly.graph_objects as go

# --- Draw a baseball field with specified base coordinates using Plotly ---
home = (0, 0)
first = (63, 63)
second = (0, 126)
third = (-63, 63)
y_shift = 0 - home[1]
home = (home[0], home[1] + y_shift)
first = (first[0], first[1] + y_shift)
second = (second[0], second[1] + y_shift)
third = (third[0], third[1] + y_shift)

diamond_x = [home[0], first[0], second[0], third[0], home[0]]
diamond_y = [home[1], first[1], second[1], third[1], home[1]]

fence_angles = np.linspace(-45, 45, 200)
fence_x = []
fence_y = []
for angle in fence_angles:
    rad = np.deg2rad(angle)
    radius = 330 + (400 - 330) * np.cos(np.deg2rad(angle))
    fence_x.append(radius * np.sin(rad))
    fence_y.append(radius * np.cos(rad) + y_shift)

foul_left_x = [third[0], fence_x[0]]
foul_left_y = [third[1], fence_y[0]]
foul_right_x = [first[0], fence_x[-1]]
foul_right_y = [first[1], fence_y[-1]]

# --- Statcast coordinate transformation for batted balls ---
statcast_x = []
statcast_y = []
event_types = []
distances = []
with open('data/harper_2025_batted_balls_with_type.csv') as f:
    reader = csv.reader(f, delimiter='|')
    for row in reader:
        if len(row) >= 3:
            try:
                hc_x = float(row[0])
                hc_y = float(row[1])
                event_type = row[2].strip()
                location_x = 2.5 * (hc_x - 125.42)
                location_y = 2.5 * (198.27 - hc_y)
                statcast_x.append(location_x)
                statcast_y.append(location_y)
                event_types.append(event_type)
                distances.append(np.sqrt(location_x**2 + location_y**2))
            except ValueError:
                continue

color_map = {
    'home_run': 'red',
    'single': 'green',
    'double': 'blue',
    'triple': 'purple',
}
colors = []
for etype in event_types:
    if etype in color_map:
        colors.append(color_map[etype])
    elif 'out' in etype:
        colors.append('gray')
    else:
        colors.append('black')

fig = go.Figure()
fig.add_trace(go.Scatter(x=diamond_x, y=diamond_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
fig.add_trace(go.Scatter(x=fence_x, y=fence_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
fig.add_trace(go.Scatter(x=foul_left_x, y=foul_left_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
fig.add_trace(go.Scatter(x=foul_right_x, y=foul_right_y, mode='lines', line=dict(color='black', width=2), showlegend=False))

hover_text = [f"Event: {etype}<br>x: {x:.1f} ft<br>y: {y:.1f} ft<br>Distance: {d:.1f} ft" for etype, x, y, d in zip(event_types, statcast_x, statcast_y, distances)]
fig.add_trace(go.Scatter(
    x=statcast_x, y=statcast_y, mode='markers',
    marker=dict(color=colors, size=8, line=dict(width=1, color='black')),
    text=hover_text, hoverinfo='text', name='Batted Balls'))

margin_x = (max(statcast_x) - min(statcast_x)) * 0.1
margin_y = (max(statcast_y) - min(statcast_y)) * 0.1
xmin = min(-350, min(statcast_x) - margin_x)
xmax = max(350, max(statcast_x) + margin_x)
ymin = min(-20 + y_shift, min(statcast_y) - margin_y)
ymax = max(450 + y_shift, max(statcast_y) + margin_y)
fig.update_layout(
    title='Baseball Field with Standard MLB Outfield and Statcast Batted Balls',
    xaxis=dict(title='Feet (x)', range=[xmin, xmax], scaleanchor='y', scaleratio=1),
    yaxis=dict(title='Feet (y)', range=[ymin, ymax]),
    width=900, height=900,
    showlegend=False
)

fig.write_html('data/baseball_field_with_statcast_balls_interactive.html')
print('Interactive plot saved as data/baseball_field_with_statcast_balls_interactive.html')

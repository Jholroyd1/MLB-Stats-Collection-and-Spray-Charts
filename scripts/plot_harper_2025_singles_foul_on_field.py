import plotly.graph_objects as go

# Field geometry (copied from interactive field script)
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

import numpy as np
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

# Bryce Harper 2025 singles (foul territory): (coord_x, coord_y, distance)
singles = [
    (126.0, 204.5, 99.0),
    (46.73, 130.94, 241.0),
    (156.96, 170.28, 110.0),
]

# Plotly scatter for singles
singles_x = [x for x, y, d in singles]
singles_y = [y for x, y, d in singles]
singles_text = [f"Distance: {d}<br>x: {x}<br>y: {y}" for x, y, d in singles]

fig = go.Figure()
fig.add_trace(go.Scatter(x=diamond_x, y=diamond_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
fig.add_trace(go.Scatter(x=fence_x, y=fence_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
fig.add_trace(go.Scatter(x=foul_left_x, y=foul_left_y, mode='lines', line=dict(color='black', width=2), showlegend=False))
fig.add_trace(go.Scatter(x=foul_right_x, y=foul_right_y, mode='lines', line=dict(color='black', width=2), showlegend=False))

fig.add_trace(go.Scatter(
    x=singles_x, y=singles_y, mode='markers',
    marker=dict(color='green', size=14, line=dict(width=2, color='black')),
    text=singles_text, hoverinfo='text', name='Singles (Foul Territory)'))

margin_x = (max(singles_x) - min(singles_x)) * 0.1
margin_y = (max(singles_y) - min(singles_y)) * 0.1
xmin = min(-350, min(singles_x) - margin_x)
xmax = max(350, max(singles_x) + margin_x)
ymin = min(-20 + y_shift, min(singles_y) - margin_y)
ymax = max(450 + y_shift, max(singles_y) + margin_y)
fig.update_layout(
    title='Bryce Harper 2025 Singles (Foul Territory) on Baseball Field',
    xaxis=dict(title='Feet (x)', range=[xmin, xmax], scaleanchor='y', scaleratio=1),
    yaxis=dict(title='Feet (y)', range=[ymin, ymax]),
    width=900, height=900,
    showlegend=False
)

fig.write_html('data/harper_2025_singles_foul_on_field.html')
print('Interactive plot saved as data/harper_2025_singles_foul_on_field.html')

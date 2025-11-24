
import numpy as np
import csv
from matplotlib.backend_bases import MouseButton
import plotly.graph_objects as go

# Load batted ball data with event type
x = []
y = []
event_types = []
with open('data/harper_2025_batted_balls_with_type.csv') as f:
    reader = csv.reader(f, delimiter='|')
    for row in reader:
        if len(row) == 3:
            try:
                x.append(float(row[0]))
                y.append(float(row[1]))
                event_types.append(row[2])
            except ValueError:
                continue

# Center the coordinates
mean_x = np.mean(x)
mean_y = np.mean(y)
x_centered = [val - mean_x for val in x]
y_centered = [val - mean_y for val in y]

# Color code: home_run = red, single = green, double = blue, triple = purple, out = gray, else = black
colors = []
                    bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def on_pick(event):
    ind = event.ind[0]
    x = statcast_x[ind]
    y = statcast_y[ind]
    distance = np.sqrt(x**2 + y**2)
    annot.xy = (x, y)
    annot.set_text(f"x={x:.1f}\ny={y:.1f}\ndist={distance:.1f} ft")
    annot.set_visible(True)
    fig.canvas.draw_idle()

def on_click(event):
    # Hide annotation if click is not on a point
    if event.button is MouseButton.LEFT and not event.inaxes is None:
        contains, _ = sc.contains(event)
        if not contains:
            annot.set_visible(False)
            fig.canvas.draw_idle()

fig.canvas.mpl_connect("pick_event", on_pick)
fig.canvas.mpl_connect("button_press_event", on_click)

# Custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Home Run', markerfacecolor='red', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Single', markerfacecolor='green', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Double', markerfacecolor='blue', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Triple', markerfacecolor='purple', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Out', markerfacecolor='gray', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Other', markerfacecolor='black', markersize=10, markeredgecolor='k'),
]
ax.legend(handles=legend_elements, loc='upper right')

# Set limits and aspect for full field, expanding to fit all batted balls
margin_x = (max(statcast_x) - min(statcast_x)) * 0.1
margin_y = (max(statcast_y) - min(statcast_y)) * 0.1
xmin = min(-350, min(statcast_x) - margin_x)
xmax = max(350, max(statcast_x) + margin_x)
ymin = min(-20 + y_shift, min(statcast_y) - margin_y)
ymax = max(450 + y_shift, max(statcast_y) + margin_y)
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_aspect('equal', adjustable='box')
ax.set_title('Baseball Field with Standard MLB Outfield and Statcast Batted Balls')
ax.set_xlabel('Feet (x)')
ax.set_ylabel('Feet (y)')

plt.tight_layout()
plt.savefig('data/baseball_field_with_statcast_balls.png', dpi=150)
plt.show()

# Calculate plot limits for the data
margin_x = (max(x_centered) - min(x_centered)) * 0.15
margin_y = (max(y_flipped) - min(y_flipped)) * 0.15
xmin = min(x_centered) - margin_x
xmax = max(x_centered) + margin_x
ymin = min(y_flipped) - margin_y
ymax = max(y_flipped) + margin_y

ax.scatter(x_centered, y_flipped, c=colors, alpha=0.7, edgecolors='k', label='Batted Balls', zorder=10)
ax.set_title("Bryce Harper Batted Balls - 2025 Season\n(Centered, Flipped, With Field)")
ax.set_xlabel("Centered Feet (x)")
ax.set_ylabel("Centered Feet (y, flipped)")
# Add larger margins to ensure all points are visible
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_aspect('equal', adjustable='box')
# Custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Home Run', markerfacecolor='red', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Single', markerfacecolor='green', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Double', markerfacecolor='blue', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Triple', markerfacecolor='purple', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Out', markerfacecolor='gray', markersize=10, markeredgecolor='k'),
    Line2D([0], [0], marker='o', color='w', label='Other', markerfacecolor='black', markersize=10, markeredgecolor='k'),
]
ax.legend(handles=legend_elements, loc='upper right')
plt.tight_layout()
plt.savefig('data/harper_2025_batted_balls_blank_for_drawing.png', dpi=150)
plt.show()

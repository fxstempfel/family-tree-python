import itertools
from dataclasses import dataclass

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patches as mpt
import matplotlib.pyplot as plt


@dataclass()
class Dimension:
    value: float
    occurrences: int


CONFIG = {
    "nb_gen": 9,
    "dimensions": {
        "people": [
            Dimension(.65, 1),
            Dimension(.8, 1),
            Dimension(1, 1),
            Dimension(1.1, 1),
            Dimension(1.4, 1),
            Dimension(1.8, 1),
            Dimension(2, 1),
            Dimension(2.5, 1),
            Dimension(3.5, 3),
        ],
        "marriage": [
            Dimension(.4, 5),
            Dimension(.6, 2),
            Dimension(.9, 1),
            Dimension(1.2, 3),
        ],
        "width": [
            Dimension(.75, 3),
            Dimension(.6, 2),
            Dimension(.4, 2),
            Dimension(.3, 3),
        ],
    }
}


def _make_dimensions(key: str):
    return list(itertools.chain(*[[d.value] * d.occurrences for d in CONFIG["dimensions"][key]]))[:CONFIG["nb_gen"]]


DIMENSIONS_PEOPLE = _make_dimensions("people")
DIMENSIONS_MARRIAGE = _make_dimensions("marriage")
DIMENSIONS_WIDTH = _make_dimensions("width")
print(f"{DIMENSIONS_PEOPLE=}")
print(f"{DIMENSIONS_MARRIAGE=}")

COLORS = mcolors.BASE_COLORS
del COLORS["w"]
COLORS = list(COLORS.values())

WIDTH = 118.9
HEIGHT = 84.1
ANGLE = 170
ANGLE_OFFSET = 90

w_center = WIDTH * .5
h_center = HEIGHT * .5 * .99
CENTER = (w_center, h_center)
RADIUS_CIRCLE = 2 / 84.1 * HEIGHT
ARC_WIDTH = .6

fig, ax = plt.subplots(1, 1, figsize=(WIDTH, HEIGHT))
ax.set_aspect('equal', adjustable='box')
# To make sure patches are plotted
plt.plot(.5, .2, .3, .4)

# axes settings
ax.set_xlim(0, WIDTH)
ax.set_ylim(0, HEIGHT)


def draw_arc(radius, color=None):
    print(f"    Arc {radius}")
    e = 2 * radius
    pac = mpt.Arc(CENTER, e, e, angle=90, theta1=-ANGLE, theta2=ANGLE, color=color, linewidth=ARC_WIDTH)
    ax.add_patch(pac)


def draw_line_radial(x, y, d, theta, offset=0.0, line_width=None):
    theta = theta + ANGLE_OFFSET
    theta_rad = theta / 180 * np.pi
    cos = np.cos(theta_rad)
    sin = np.sin(theta_rad)

    x2 = x + d * cos
    y2 = y + d * sin

    x += offset * cos
    y += offset * sin
    # print(f"Line ({x:.2f}, {y:.2f}), ({x2:.2f}, {y2:.2f}) // {np.sqrt((x - x2)**2 + (y - y2)**2):.2f}")
    ax.plot((x, x2), (y, y2), color="black", linewidth=line_width)


def draw_generation_rec(n, offset, already_plotted_angles=None):
    if n == CONFIG["nb_gen"]:
        return offset
    radius_diff_people = DIMENSIONS_PEOPLE[n] * RADIUS_CIRCLE
    radius_marriage = DIMENSIONS_MARRIAGE[n] * RADIUS_CIRCLE
    line_width = DIMENSIONS_WIDTH[n]

    radius_first = offset + radius_marriage
    radius_second = radius_first + radius_diff_people

    # fill area for marriages
    x_list, y_list = interpolate_arcs(offset, radius_first)
    """if n == 0:
        FIG = plt.figure()
        AXES = FIG.add_subplot(111)
        arrowplot(AXES, np.array(x_list), np.array(y_list))
    """
    ax.fill(x_list, y_list, "#fff799", zorder=-12)

    # draw arcs
    draw_arc(radius_first)
    draw_arc(radius_second)

    # draw lines (2^n lines to draw)
    if already_plotted_angles is None:
        already_plotted_angles = []
    # we need to split [-angle, angle] into 2^n + 1 intervals

    range_separating_angles = _find_separating_angles(2 ** n - 1)
    plotted_angles_list = []
    # due to numerical operation, angles can be slightly different
    if len(range_separating_angles) >= 2:
        angles_error = abs(range_separating_angles[0] - range_separating_angles[1]) / 10
    else:
        angles_error = ANGLE
    for theta in range_separating_angles:
        # skip already plotted angles
        skip = False
        for theta2 in already_plotted_angles:
            if abs(theta2 - theta) < angles_error:
                skip = True
                break
            if theta2 > theta + angles_error:
                break
        if skip:
            continue

        # draw line if not skipped
        draw_line_radial(w_center, h_center, d=RADIUS_MAX, theta=theta, offset=radius_first, line_width=line_width)
        plotted_angles_list.append(theta)

    draw_generation_rec(n + 1,
                        offset=radius_second,
                        already_plotted_angles=sorted(already_plotted_angles + plotted_angles_list),)


def _find_separating_angles(k):
    # k is the number of angles to find
    size_interval = ANGLE * 2
    size_chunk = size_interval / (k + 1)
    return [size_chunk * (i + 1) - ANGLE for i in range(k)]


def interpolate_arcs(radius_1, radius_2):
    # first, interpolate inner arc left to right
    num = 1000 + int((radius_1 / WIDTH) ** 3 * 5000000)
    num = 100
    print(f"{num=}")
    thetas = np.linspace((180 + ANGLE - ANGLE_OFFSET) / 180 * np.pi, (180 - ANGLE - ANGLE_OFFSET) / 180 * np.pi, num=num)
    print(f"{thetas=}")
    r1 = radius_1
    x = [r1 * np.cos(t) + w_center for t in thetas]
    y = [r1 * np.sin(t) + h_center for t in thetas]

    # second, interpolate outer arc right to left
    x += [radius_2 * np.cos(t) + w_center for t in reversed(thetas)]
    y += [radius_2 * np.sin(t) + h_center for t in reversed(thetas)]

    x.append(x[0])
    y.append(y[0])

    return x, y


# draw circle
ax.add_patch(mpt.Circle(CENTER, RADIUS_CIRCLE, fill=False))

# draw side lines
RADIUS_MAX = (1 + sum(DIMENSIONS_PEOPLE) + sum(DIMENSIONS_MARRIAGE)) * RADIUS_CIRCLE
print(f"{RADIUS_MAX=}")
draw_line_radial(*CENTER, RADIUS_MAX, ANGLE, offset=RADIUS_CIRCLE, line_width=1)
draw_line_radial(*CENTER, RADIUS_MAX, -ANGLE, offset=RADIUS_CIRCLE, line_width=1)

# draw generations
draw_generation_rec(0, RADIUS_CIRCLE)

print(f"{len(ax.patches)} patches")

plt.axis('off')
#plt.show()
plt.savefig("test.pdf", bbox_inches='tight')

import tkinter as tk


canvas = tk.Canvas(options={
    "width": 10,
    "height": 10,
})

NB_GEN = 6

RADIUS_DIFF_MARRIAGE = .5
RADIUS_DIFF_PEOPLE_1 = 1.5
RADIUS_DIFF_PEOPLE_2 = 2.5
RADIUS_DIFF_PEOPLE_3 = 5
# From this generation we switch to next radius diff
THRESHOLD_PEOPLE_2 = 4
THRESHOLD_PEOPLE_3 = 6

WIDTH = 70
HEIGHT = 50
ANGLE = 150
ANGLE_OFFSET = 90

w_center = WIDTH / 2
h_center = HEIGHT * .4
CENTER = (w_center, h_center)
RADIUS_CIRCLE = 1


def draw_arc(c: tk.Canvas, radius, color=None):
    print(f"    Arc {radius}")
    e = 2 * radius
    c.create_arc(CENTER, e, e, angle=90, theta1=-ANGLE, theta2=ANGLE, color=color)
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


def draw_generation_rec(n, offset, already_plotted_angles=None, n_max=8):
    if n > n_max:
        return offset

    if n < THRESHOLD_PEOPLE_2:
        radius_diff_people = RADIUS_DIFF_PEOPLE_1
    elif n < THRESHOLD_PEOPLE_3:
        radius_diff_people = RADIUS_DIFF_PEOPLE_2
    else:
        radius_diff_people = RADIUS_DIFF_PEOPLE_3

    # draw arcs
    radius_first = offset + RADIUS_DIFF_MARRIAGE
    radius_second = radius_first + radius_diff_people
    print(f"#{n}: {offset} {radius_diff_people} {radius_first} {radius_second}")
    draw_arc(radius_first)
    draw_arc(radius_second)

    # fill area for marriages
    x_list, y_1_list, y_2_list = interpolate_arcs(offset, radius_first, 1000)
    fill_between_curves(x_list, y_1_list, y_2_list, "y")

    # draw lines (2^n lines to draw)
    if already_plotted_angles is None:
        already_plotted_angles = []
    # we need to split [-angle, angle] into 2^n + 1 intervals
    if n < THRESHOLD_PEOPLE_2:
        line_width = 1
    elif n < THRESHOLD_PEOPLE_3:
        line_width = .65
    else:
        line_width = .3

    angles_list = _find_separating_angles(2 ** n - 1)
    plotted_angles_list = []
    # due to numerical operation, angles can be slightly different
    if len(angles_list) >= 2:
        angles_error = abs(angles_list[0] - angles_list[1]) / 10
    else:
        angles_error = ANGLE
    for theta in angles_list:
        # skip already plotted angles
        skip = False
        for theta2 in already_plotted_angles:
            if abs(theta2 - theta) < angles_error:
                skip = True
                break
            if theta2 > theta + angles_error:
                break
        if skip:
            print(f"        Skipping {theta:.3f} ({theta2:.3f})")
            continue

        # draw line if not skipped
        draw_line_radial(w_center, h_center, radius_max, theta, radius_first, line_width)
        plotted_angles_list.append(theta)

    draw_generation_rec(n + 1,
                        offset=radius_second,
                        already_plotted_angles=sorted(already_plotted_angles + plotted_angles_list),
                        n_max=n_max)


def _find_separating_angles(k):
    # k is the number of angles to find
    size_interval = ANGLE * 2
    size_chunk = size_interval / (k + 1)
    return [size_chunk * (i + 1) - ANGLE for i in range(k)]


def get_radius_offset(n):
    # todo thresholds in dict + marriage threshold
    radii_people_1 = min(n, THRESHOLD_PEOPLE_2 - 1) * RADIUS_DIFF_PEOPLE_1
    radii_people_2 = max((min(n + 1, THRESHOLD_PEOPLE_3) - THRESHOLD_PEOPLE_2) * RADIUS_DIFF_PEOPLE_2, 0)
    radii_people_3 = max((n - THRESHOLD_PEOPLE_3 + 1) * RADIUS_DIFF_PEOPLE_3, 0)
    return RADIUS_CIRCLE + n * RADIUS_DIFF_MARRIAGE + radii_people_1 + radii_people_2 + radii_people_3


def interpolate_arcs(radius_1, radius_2, nb_points):
    def circle_fct(x, r):
        # todo this is not correct (check signs)
        return np.sqrt(r**2 - (x - w_center)**2) + h_center

    left_bound = radius_2 * np.cos(- ANGLE / 160 * np.pi)
    right_bound = radius_2 * np.cos(ANGLE / 160 * np.pi)
    xs = np.linspace(left_bound, right_bound, nb_points)

    y_1 = []
    y_2 = []
    for x in xs:
        y_1.append(circle_fct(x, radius_1))
        y_2.append(circle_fct(x, radius_2))

    return xs, y_1, y_2


def fill_between_curves(x, y1, y2, color):
    poly_x = np.concatenate((x, x[::-1]))
    poly_y = np.concatenate((y1, y2))
    print(poly_x)
    print(poly_y)
    p = plt.Polygon(np.column_stack((poly_x, poly_y)), facecolor=color, alpha=.5, edgecolor=None)
    print(p)
    ax.add_artist(p)


radius_max = get_radius_offset(NB_GEN)
print(f"Radius max = {radius_max}")

# draw circle
ax.add_patch(mpt.Circle(CENTER, RADIUS_CIRCLE, fill=False))

# draw side lines
draw_line_radial(*CENTER, radius_max, ANGLE, offset=RADIUS_CIRCLE, line_width=1)
draw_line_radial(*CENTER, radius_max, -ANGLE, offset=RADIUS_CIRCLE, line_width=1)

# draw generations
draw_generation_rec(1, RADIUS_CIRCLE, n_max=NB_GEN)

print(f"{len(ax.patches)} patches")

plt.show()

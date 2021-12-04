from dataclasses import dataclass
from scipy.optimize import minimize
from typing import Callable, List

import numpy as np
from wand.color import Color
from wand.compat import nested
from wand.display import display
from wand.drawing import Drawing
from wand.image import Image

from family_tree import ANGLE, CENTER, CONFIG, DIMENSIONS_MARRIAGE, DIMENSIONS_PEOPLE, H_CENTER_FACTOR, RADIUS_CIRCLE, HEIGHT, WIDTH

WAND_ANGLE_OFFSET = 90


def _make_distorted_text(text: str, img_main, angle_start, angle_stop, column_offset, row_offset):
    # TODO resize to fit the cells
    with Image() as img:
        angle_arc = abs(angle_start - angle_stop) * .9
        angle_rot = (angle_start + angle_stop) / 2 - ANGLE
        img.read(filename=f"label: {text} {angle_start=} {angle_stop=} {angle_rot=}",
                 background=Color("None"))

        # first angle is arc span, second angle is rotation clockwise, from noon
        img.distort('arc', (angle_arc, angle_rot))
        # TODO compute and add height and width
        img_main.composite(img, left=int(column_offset * img_main.width), top=int(row_offset * img_main.height))


def _dichotomy(a, b, n):
    # n = number of intervals
    limits = np.linspace(a, b, n + 1)
    return [limits[i:i+2] for i in range(n)]


@dataclass
class Offset:
    row: int
    col: int


def _get_generation_radius_offset(n_gen: int) -> float:
    # todo double check this, there're offsets in row and col offset
    return (1 + sum(DIMENSIONS_PEOPLE[:n_gen-1]) + sum(DIMENSIONS_MARRIAGE[:n_gen]) + DIMENSIONS_PEOPLE[n_gen] / 2) * RADIUS_CIRCLE


def _get_offsets(n_gen: int, angles_chunks) -> List[Offset]:
    # get column and row offsets for a given generation
    radius = _get_generation_radius_offset(n_gen)
    print(f"{radius=}")

    # find offset in original dimensions
    res = []
    for t0, t1 in angles_chunks:
        t0 = (t0 - WAND_ANGLE_OFFSET) / 180 * np.pi
        t1 = (t1 - WAND_ANGLE_OFFSET) / 180 * np.pi

        # top offset is necessarily one of the extremities'
        top = CENTER[1] - radius * max(np.sin(t0), np.sin(t1))

        # left offset can be anywhere in the arc
        min_left = minimize(lambda x: -np.cos(x), (t0 + t1) / 2, bounds=[(t0, t1)]).fun[0]
        print(f"minimize    {t0=} {t1=} {min_left}")
        left = CENTER[0] + radius * min_left

        res.append(Offset(row=top / HEIGHT, col=left / WIDTH))
    return res


if __name__ == '__main__':
    with nested(Image(filename="test.pdf"), Drawing()) as (img, draw):
        center = int(img.width / 2), int(img.height / 2 * H_CENTER_FACTOR)
        print(f"{center=}")
        radius_circle = 2 / HEIGHT * img.height

        # write center circle
        draw.font_size = 16
        draw.text_alignment = "center"
        draw.text(center[0], center[1], "Evelyne BRANCHET\n19/07/1956\nà Saint-Laurent\nde Chamoussey")
        draw(img)

        angle_full_span = ANGLE * 2
        #for i_gen in range(1, int(CONFIG["nb_gen"])):
        for i_gen in range(1, 2):
            angles_chunks = _dichotomy(0, angle_full_span, n=2**i_gen)
            for i, (c, offset) in enumerate(zip(angles_chunks, _get_offsets(n_gen=i_gen, angles_chunks=angles_chunks))):
                print(f"{c=}")
                print(f"{offset=}")
                _make_distorted_text(f"{i_gen=} {i=} {c=}", img, *c, column_offset=offset.col, row_offset=offset.row)

        display(img)

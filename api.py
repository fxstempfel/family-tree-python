import numpy as np


def get_radius_marriage(dimensions_people, dimensions_marriage, radius, n_gen):
    # n_gen: 1 is the parents of the target person (0 is the center circle)
    if n_gen == 0:
        raise ValueError("no marriage cells for generation 0")
    return radius * (1 + sum(dimensions_people[:n_gen-1]) + sum(dimensions_marriage[:n_gen]))


def get_radius_people(dimensions_people, dimensions_marriage, radius, n_gen):
    # n_gen: 1 is the parents of the target person (0 is the center circle)
    return radius * (1 + sum(dimensions_people[:n_gen]) + sum(dimensions_marriage[:n_gen]))


def get_generation_angles(angle_aperture, n_gen, offset=0):
    # angle_aperture is the angle for each of the parents (angle * 2 = angle for generation 1)
    angles = np.linspace(offset - angle_aperture, offset + angle_aperture, 2**n_gen + 1)
    return [(t1, t2) for t1, t2 in zip(angles[:-1], angles[1:])]

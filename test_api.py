import pytest
import api


class TestRadiusPeople:
    def test_base(self):
        got = api.get_radius_people(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5],
            radius=1,
            n_gen=2,
        )
        assert got == 3.6

    def test_0(self):
        got = api.get_radius_people(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5],
            radius=1,
            n_gen=0,
        )
        assert got == 1

    def test_radius2(self):
        got = api.get_radius_people(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5, .7],
            radius=2,
            n_gen=2,
        )
        assert got == 7.2

    def test_1(self):
        got = api.get_radius_people(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5, .7],
            radius=2,
            n_gen=1,
        )
        assert got == 4.2


class TestRadiusMarriage:
    def test_base(self):
        got = api.get_radius_marriage(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5],
            radius=1,
            n_gen=2,
        )
        assert got == 2.6

    def test_0(self):
        with pytest.raises(ValueError):
            api.get_radius_marriage(
                dimensions_people=[1, 1, 2],
                dimensions_marriage=[.1, .5],
                radius=1,
                n_gen=0,
            )

    def test_radius2(self):
        got = api.get_radius_marriage(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5, .7],
            radius=2,
            n_gen=2,
        )
        assert got == 5.2

    def test_1(self):
        got = api.get_radius_marriage(
            dimensions_people=[1, 1, 2],
            dimensions_marriage=[.1, .5, .7],
            radius=2,
            n_gen=1,
        )
        assert got == 2.2


class TestGenerationAngles:
    def test_gen_1(self):
        assert api.get_generation_angles(100, 1) == [(-100, 0), (0, 100)]

    def test_gen_2(self):
        assert api.get_generation_angles(120, 2) == [(-120, -60), (-60, 0), (0, 60), (60, 120)]

    def test_gen_3(self):
        assert api.get_generation_angles(120, 3) == [(-120, -90), (-90, -60), (-60, -30), (-30, 0),
                                                     (0, 30), (30, 60), (60, 90), (90, 120)]

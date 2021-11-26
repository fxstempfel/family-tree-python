from __future__ import annotations

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patches as mpt
import matplotlib.pyplot as plt
from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta


@dataclass()
class Event:
    date: date
    place: str


@dataclass()
class Person:
    # should be able to edit name, birth, death
    id: str
    name: str
    birth: Event
    generation: int
    parents: Couple
    death: Event = None

    def __post_init__(self):
        self.dead_at = None
        if self.death is not None:
            self.dead_at = relativedelta(self.death.date, self.birth.date).years


@dataclass()
class Couple:
    first: Person
    second: Person = None
    marriage: Event = None



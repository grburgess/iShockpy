from dataclasses import dataclass
from typing import List

from .utils.constants import c


@dataclass(frozen=True)
class Collision:
    radiated_energy: float
    gamma: float
    radius: float
    time: float


    @property
    def time_observer(self) -> float:

        return self.time - self.radius/c


class CollisionHistory(object):

    def __init__(self, collisions: List[Collision]) -> None:

        self._collisions = collisions


    @property
    def gamma(self) -> List[float]:

        return [x.gamma for x in self._collisions]

    @property
    def radiated_energy(self) -> List[float]:

        return [x.radiated_energy for x in self._collisions]

    
    @property
    def radius(self) -> List[float]:

        return [x.radius for x in self._collisions]

    
    @property
    def time(self) -> List[float]:

        return [x.time for x in self._collisions]

    @property
    def time_observer(self) -> List[float]:

        return [x.time_observer for x in self._collisions]

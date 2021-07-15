from dataclasses import dataclass

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

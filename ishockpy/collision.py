from dataclasses import dataclass
from typing import List

import h5py
import numpy as np

from .io.logging import setup_logger
from .utils.constants import c

log = setup_logger(__name__)

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


    

    def to_hdf5(self, group) -> None:

        group.create_dataset("radiated_energy", data= np.array(self.radiated_energy), compression="gzip")
        group.create_dataset("gamma", data= np.array(self.gamma), compression="gzip")
        group.create_dataset("radius", data= np.array(self.radius), compression="gzip")
        group.create_dataset("time", data= np.array(self.time), compression="gzip")

    def write_to(self, file_name: str) -> None:

        with h5py.File(file_name, "w") as f:

            self.to_hdf5(f)
        
        
    @classmethod
    def from_hdf5(cls, group):

        radii = group["radius"][()]
        gamma = group["gamma"][()]
        rad_energy = group["radiated_energy"][()]
        time = group["time"][()]

        collisions =  [Collision(a,b,c,d) for a,b,c,d in zip(rad_energy, gamma, radii, time)]

        return cls(collisions)

        
    @classmethod
    def from_file(cls, file_name: str):

        with h5py.File(file_name, "r") as f:

            return cls.from_hdf5(f)

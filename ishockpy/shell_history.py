from dataclasses import dataclass, field
from typing import List

import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class Conditions:
    mass: float
    gamma: float
    status: bool


@dataclass(frozen=True)
class ShellHistory:
        
    gamma: List[float] = field(default_factory=list)
    time: List[float] = field(default_factory=list)
    radius: List[float] = field(default_factory=list)
    mass: List[float] = field(default_factory=list)
    status: List[bool]= field(default_factory=list)

    def add_entry(self, time, gamma, radius, mass, status):

        self.time.append(time)
        self.radius.append(radius)
        self.gamma.append(gamma)
        self.mass.append(mass)
        self.status.append(status)

    def _at_time(self, time) -> int:

        return np.searchsorted(self.time, time)

    def conditions_at_time(self, time) -> Conditions:

        idx = self._at_time(time)

        return Conditions(mass=self.mass[idx], gamma=self.gamma[idx], status=self.status[idx])

    @property
    def n_time_steps(self) -> int:

        return len(self.time)
    
    def to_hdf5(self, group) -> None:

        group.create_dataset("gamma", data=self.gamma, compression="gzip")
        group.create_dataset("time", data=self.time, compression="gzip")
        group.create_dataset("radius", data=self.radius, compression="gzip")
        group.create_dataset("mass", data=self.mass, compression="gzip")
        group.create_dataset("status", data=self.status, compression="gzip")

    @classmethod
    def from_hdf5(cls, group):

        gamma = group["gamma"][()]
        time = group["time"][()]
        radius = group["radius"][()]
        mass = group["mass"][()]
        status = group["status"][()]

        return cls(gamma=gamma, time=time, radius=radius, mass=mass, status=status)

    

class DetailedHistory(object):

    def __init__(self, shell_histories: List[ShellHistory]) -> None:


        self._shell_histories: List[ShellHistory] =  shell_histories

        self._n_shells = len(self._shell_histories)

        self._n_time_steps =  self._shell_histories[0].n_time_steps

        
    @property
    def n_shells(self) -> int:

        return self._n_shells

    @property
    def n_time_steps(self) -> int:

        return self._n_time_steps


    @property
    def histories(self) -> List[ShellHistory]:

        return self._shell_histories
    
    def _compute_values_at_time(self, time):

        status = []
        masses = []
        gammas = []

        for hist in self._shell_histories:

            condition: Conditions = hist.conditions_at_time(time)
            
            status.append(condition.status)
            masses.append(condition.mass)
            gammas.append(condition.gamma)


        status = np.array(status)
        masses = np.array(masses)
        gammas=np.array(gammas)

        return gammas[status], masses[status]

    def plot_gamma_at_time(self, time):

        gamma, mass = self._compute_values_at_time(time)

        total_mass = mass.sum()

        fig, ax = plt.subplots()


        ax.plot(mass[::-1].cumsum()/total_mass,gamma[::-1],'.')

        ax.set_xlim(0,1)

        ax.set_xlabel("M/M total")

        ax.set_ylabel("gamma")


    def to_hdf5(self, group) -> None:


        group.attrs["n_shells"] = self._n_shells
        
        for i, history in enumerate(self._shell_histories):

            shell_group = group.create_group(f"shell_{i}")

            history.to_hdf5(shell_group)
    
    @classmethod
    def from_hdf5(cls, group):

        n_shells = int(group.attrs["n_shells"])

        histories = [ShellHistory.from_hdf5(group[f"shell_{i}"]) for i in range(n_shells)]

        return cls(histories)

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



class DetailedHistory(object):

    def __init__(self, shell_histories: List[ShellHistory]) -> None:


        self._shell_histories: List[ShellHistory] =  shell_histories


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


        ax.plot(mass.cumsum()/total_mass,gamma,'.')

        ax.set_xlim(0,1)

        ax.set_xlabel("M/M total")

        ax.set_ylabel("gamma")



    

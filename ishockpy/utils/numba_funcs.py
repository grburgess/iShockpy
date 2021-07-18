import numba as nb
import numpy as np

from .constants import c



@nb.njit
def beta(gamma):
    return np.sqrt(1.- (1./(gamma * gamma)))

@nb.njit(fastmath=False)
def velocity(gamma):
#    return c * np.sqrt(gamma**2 -1. )/gamma
    return c * beta(gamma)


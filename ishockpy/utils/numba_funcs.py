import numba as nb
import numpy as np

from .constants import c


@nb.njit(fastmath=True)
def velocity(gamma):
    return c * np.sqrt(gamma**2 -1. )/gamma


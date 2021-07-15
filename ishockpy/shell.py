__author__ = "grburgess"


from typing import List, Optional

# import astropy.constants as constants
import numpy as np
from numba import jit, njit

from ishockpy.io.logging import setup_logger

from .shell_history import ShellHistory
from .utils.constants import c as C
from .utils.numba_vector import VectorInt32
from .utils.numba_funcs import velocity
log = setup_logger(__name__)


C2 = C*C

class Shell(object):
    def __init__(self, initial_gamma: float, initial_mass: float, initial_radius: float, jet):
        """
        A 'shell' in the outflow representing a differential
        hyrdo-element with zero width

        :param initial_gamma: the initial Lorentz factor
        :param initial_mass: the initial mass
        :param initial_radius: the intial radius
        :param jet: the jet that is associated to this shell
        :returns: 
        :rtype: 

        """

        # the shells status
        self._active: bool = False

        # set the initial phyical parameters
        self._gamma: float = initial_gamma
        self._mass: float = initial_mass
        self._radius: float = initial_radius

        self._initial_gamma: float = initial_gamma
        self._initial_mass: float = initial_mass
        self._initial_radius: float = initial_radius

        # keep track of the jet
        self._jet = jet

        # set by the shell set
        self._id: Optional[int] = None
        self._initialized: bool = False
        
        self._history = ShellHistory()

        self._has_changed = True

    @property
    def id(self) -> int:

        return self._id
    def set_id(self, id: int) -> None:
        """
        set the shell ID

        :param id: 
        :type id: int
        :returns: 

        """

        if not self._initialized:
        
            self._id = id

        else:

            log.error("shell already initialized")

        self._initialized = True
        
    
    @property
    def radius(self) -> float:
        """
        the comoving radius of the shell in cm
        """

        return self._radius

    @property
    def gamma(self) -> float:

        return self._gamma

    @property
    def mass(self) -> float:

        return self._mass

    @property
    def status(self) -> bool:

        return self._active

    @property
    def is_active(self) -> bool:

        return self._active

    
    @property
    def velocity(self) -> float:
        """
        get the velocity in cm/s
        """

        if self._has_changed:
            self._velocity = velocity(self._gamma)
            self._has_changed = False
        return self._velocity

    @property
    def energy(self) -> float:

        return self._gamma * self._mass * C2

    def move(self, delta_time) -> None:

        self._radius += self.velocity * delta_time

    def collide_shell(self, other_shell):
        """FIXME! briefly describe function

        :param other_shell: 
        :returns: 
        :rtype: 

        """

        if not isinstance(other_shell, Shell):

            log.error("you can only collide with a shell!")

            raise AssertionError()
            
        if not np.isclose(other_shell.radius, self._radius, rtol=1.):


            
            log.error("can only collide with a shell that is front of this shell")
            log.error(f"other: {other_shell.radius} this: {self._radius}")
            log.error(f"other: {other_shell.gamma} this: {self._gamma}")
            log.error(f"other: {other_shell.id} this: {self._id}")

            raise RuntimeError()
            
        # from Daigne 1998

        
        gamma_final = _gamma_final(
            self._gamma, other_shell.gamma, self._mass, other_shell.mass
        )

        # energy calculations

        internal_energy = _internal_energy(
            self._mass, self._gamma, gamma_final, other_shell.mass, other_shell.gamma
        )

        # now modify the physics of this shell after the merge

        self._mass += other_shell.mass
        self._gamma = gamma_final

        self._jet.add_collision(
            radiated_energy=internal_energy, gamma=gamma_final, radius=self._radius
        )

        self._has_changed = True

    def deactivate(self, time: float) -> None:
        """
        turn the shell of and record when the shell when dead
        """

        self._active = False

        self._death_time = time

    def activate(self, time: float) -> None:
        """
        turn the shell on and record the comoving time
        """

        self._active = True

        self._birth_time = time

    def record_history(self, time: float) -> None:

        self._history.add_entry(
            time=time,
            gamma=self.gamma,
            radius=self.radius,
            mass=self._mass,
            status=self.status,
        )

    def __repr__(self):

        out = "radius: %f\ngamma: %f\nmass: %f" % (
            self._radius,
            self._gamma,
            self._mass,
        )
        return out


class ShellSet(object):
    def __init__(self, list_of_shells: List[Shell]):
        """
        A set of shells

        :param list_of_shells: 
        :returns: 
        :rtype: 

        """

        self._shells: List[Shell] = np.array(list_of_shells)

        # set the static shell id
        for i, shell in enumerate(self._shells):

            shell.set_id(i)

        self._currently_active = np.array([shell.status for shell in self._shells])

        # we need to recompute the ordering

        self._has_moved: bool = True

    def __iter__(self):

        for shell in self._shells:
            yield shell

    def __getitem__(self, item) -> Shell:

        return self._shells[item]

    def activate_shells(self, time=0.0, *shell_index) -> None:

        for index in shell_index:

            self._shells[index].activate(time)
            self._currently_active[index] = True

        self._has_moved = True

    def deactivate_shells(self, time=0.0, *shell_index) -> None:

        for index in shell_index:

            self._shells[index].deactivate(time)
            self._currently_active[index] = False

        self._has_moved = True

    @property
    def gamma_distribution(self):

        return np.array([shell.gamma for shell in self.active_shells])

    @property
    def velocity_ordered_shells(self) -> List[Shell]:
        """
        return the active shells that are ordered in velocity
        """

        if self._has_moved:

            # the idea is that only shells with this conditon
            # will collide with each other

            # check if we have moved since the last call

            gamma_dist = self.gamma_distribution

            if len(gamma_dist) > 0:

                idx = _get_ordered_shells(gamma_dist)

                self._velocity_ordered_shells = self.active_shells[idx]

            else:

                self._velocity_ordered_shells = []

            # we haven't moved the shells yet
            self._has_moved = False

        return self._velocity_ordered_shells

    @property
    def radii(self) -> List[float]:

        return np.array([shell.radius for shell in self.velocity_ordered_shells])

    @property
    def velocities(self) -> List[float]:

        return np.array([shell.velocity for shell in self.velocity_ordered_shells])

    @property
    def time_to_collisions(self) -> List[float]:

        if self.n_active_shells > 1:

            v = self.velocities
            r = self.radii

            ttc = _time_to_collision(r_front=r[:-1],
                                     r_back=r[1:],
                                     v_front=v[:-1],
                                     v_back=v[1:])

            return ttc

        else:

            return []

    def move(self, delta_time) -> None:
        """
        Move the active shells

        :param delta_time: 
        :returns: 
        :rtype: 

        """

        for shell in self.active_shells:

            shell.move(delta_time)

        # the shells have move
        self._has_moved = True

    @property
    def active_shells(self) -> List[Shell]:

        return self._shells[self._currently_active]

    @property
    def n_shells(self):

        return self._n_shells
    
    @property
    def n_active_shells(self) -> int:

        return len(self.active_shells)

    def record_history(self, time) -> None:

        for shell in self._shells:
            shell.record_history(time)
    

@njit(fastmath=True)
def _internal_energy(mass, gamma, gamma_final, mass_other, gamma_other):
    return mass * (gamma / gamma_final - 1.0) + mass_other * (gamma_other / gamma_final - 1.0)


@njit(fastmath=True)
def _gamma_final(gamma, gamma_other, mass, mass_other):

    gamma_R = np.sqrt(gamma * gamma_other)

    a = (mass * gamma + mass_other * gamma_other) / (
        mass * np.sqrt(gamma * gamma - 1.0)
        + mass_other * np.sqrt(gamma_other * gamma_other - 1.0)
    )

    a2 = a * a

    gamma_final = np.sqrt(a2 / (a2 - 1.0))

    return gamma_final


@njit(fastmath=True)
def _time_to_collision(r_front, r_back, v_front, v_back):

    # n = len(r_front)
    
    # ttc = np.zeros_like(r_front)

    radius_diff = r_front - r_back
    ttc = radius_diff / (v_back - v_front)
            
    idx = radius_diff == 0.

    ttc[idx] = 0.
            


    
    # for i in range(len(r_front)):

    #     ttc[i] = (r_front[i] - r_back[i])/(v_back[i] - v_front[i] )

    return ttc

@njit(fastmath=True)
def _get_ordered_shells(gamma_dist):

    tmp = VectorInt32(0)
    
    
    
    for i in range(len(gamma_dist) - 1):

        if gamma_dist[i] < gamma_dist[i + 1]:

            tmp.append(i)
            tmp.append(i + 1)

    #return list(set(tmp))
    return tmp.arr

__author__ = "grburgess"

# import astropy.constants as constants
import numpy as np
from .shell_history import ShellHistory


C = 2.99e10  # cm/s
C2 = C * C


class Shell(object):
    def __init__(self, initial_gamma, initial_mass, initial_radius, jet):
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
        self._active = False

        # set the initial phyical parameters
        self._gamma = initial_gamma
        self._mass = initial_mass
        self._radius = initial_radius

        self._initial_gamma = initial_gamma
        self._initial_mass = initial_mass
        self._initial_radius = initial_radius

        # keep track of the jet
        self._jet = jet

        # set by the shell set
        self._shell_id = None

        self._history = ShellHistory()
        

    @property
    def radius(self):
        """
        the comoving radius of the shell in cm
        """

        return self._radius

    @property
    def gamma(self):

        return self._gamma

    @property
    def mass(self):

        return self._mass

    @property
    def status(self):

        return self._active

    @property
    def velocity(self):
        """
        get the velocity in cm/s
        """
        return C * np.sqrt(1 - (1.0 / (self._gamma * self._gamma)))

    @property
    def energy(self):

        return self._gamma * self._mass * C2

    def move(self, delta_time):

        self._radius += self.velocity * delta_time

    def collide_shell(self, other_shell):
        """FIXME! briefly describe function

        :param other_shell: 
        :returns: 
        :rtype: 

        """

        assert isinstance(other_shell, Shell), "you can only collide with a shell!"

        assert (
            other_shell.radius == self._radius
        ), "can only collide with a shell that is front of this shell"

        # from Daigne 1998

        gamma_R = np.sqrt(self._gamma * other_shell.gamma)

        a = (self._mass * self._gamma + other_shell.mass * other_shell.gamma) / (
            self._mass * np.sqrt(self._gamma * self._gamma - 1.0)
            + other_shell.mass * np.sqrt(other_shell.gamma * other_shell.gamma - 1.0)
        )

        a2 = a * a

        gamma_final = np.sqrt(a2 / (a2 - 1.0))

        # energy calculations

        internal_energy = self._mass * (
            self._gamma / gamma_final - 1.0
        ) + other_shell.mass * (other_shell.gamma / gamma_final - 1.0)

        # now modify the physics of this shell after the merge

        self._mass += other_shell.mass
        self._gamma = gamma_final

        self._jet.add_collision(
            radiated_energy=internal_energy, gamma=gamma_final, radius=self._radius
        )

    def deactivate(self, time):
        """
        turn the shell of and record when the shell when dead
        """

        self._active = False

        self._death_time = time

    def activate(self, time):
        """
        turn the shell on and record the comoving time
        """

        self._active = True

        self._birth_time = time

    def record_history(self, time):

        self._shell_history.add_entry(
            time=time,
            gamma=self.gamma,
            radius=self.radius,
            mass=self._mass,
            status=self.status

        )
        
    
    def __repr__(self):

        out = "radius: %f\ngamma: %f\nmass: %f" % (
            self._radius,
            self._gamma,
            self._mass,
        )
        return out


class ShellSet(object):
    def __init__(self, list_of_shells):
        """
        A set of shells

        :param list_of_shells: 
        :returns: 
        :rtype: 

        """

        self._shells = np.array(list_of_shells)

        # set the static shell id
        for i, shell in enumerate(self._shells):

            shell.shell_id = i

        self._currently_active = np.array([shell.status for shell in self._shells])

        # we need to recompute the ordering
        
        self._has_moved = True

    def __iter__(self):

        for shell in self._shells:
            yield shell

    def __getitem__(self, item):

        return self._shells[item]

    def activate_shells(self, time=0.0, *shell_index):

        for index in shell_index:

            self._shells[index].activate(time)
            self._currently_active[index] = True

        self._has_moved = True
            
    def deactivate_shells(self, time=0.0, *shell_index):

        for index in shell_index:

            self._shells[index].deactivate(time)
            self._currently_active[index] = False

        self._has_moved = True
            
    @property
    def gamma_distribution(self):

        return np.array([shell.gamma for shell in self.active_shells])

    @property
    def velocity_ordered_shells(self):
        """
        return the active shells that are ordered in velocity
        """

        if self._has_moved:


            tmp = []

            # the idea is that only shells with this conditon
            # will collide with each other

            # check if we have moved since the last call


            gamma_dist = self.gamma_distribution

            if len(gamma_dist) > 0:

                for i in range(len(gamma_dist) - 1):

                    if gamma_dist[i] < gamma_dist[i + 1]:

                        tmp.append(i)
                        tmp.append(i + 1)


                self._velocity_ordered_shells = self.active_shells[list(set(tmp))]
            
            else:

                self._velocity_ordered_shells = []

            # we haven't moved the shells yet
            self._has_moved = False
            
            
        return self._velocity_ordered_shells

    @property
    def radii(self):

        return np.array([shell.radius for shell in self.velocity_ordered_shells])

    @property
    def velocities(self):

        return np.array([shell.velocity for shell in self.velocity_ordered_shells])

    @property
    def time_to_collisions(self):

        if self.n_active_shells > 1:

            v = self.velocities
            r = self.radii

            ttc = (r[:-1] - r[1:]) / (v[1:] - v[:-1])

            return ttc

        else:

            return []

    def move(self, delta_time):
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
    def active_shells(self):

        return self._shells[self._currently_active]

    @property
    def n_shells(self):

        return self._n_shells

    @property
    def n_active_shells(self):

        return len(self.active_shells)

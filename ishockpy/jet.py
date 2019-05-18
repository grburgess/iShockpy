__author__ = "grburgess"

import numpy as np
import pandas as pd
from ishockpy.shell import Shell, ShellSet

MIN_DELTAT = 1e300


class Jet(object):
    def __init__(
            self, min_radius, variability_time, mass_distribution, gamma_distribution, store=False
    ):
        """FIXME! briefly describe function

        :param min_radius: 
        :param variability_time: 
        :param mass_distribution: 
        :param gamma_distribution: 
        :returns: 
        :rtype: 

        """

        assert len(mass_distribution) == len(gamma_distribution)

        self._n_shells = len(mass_distribution)

        self._shell_emit_iterator = 0

        self._shells = ShellSet(
            [
                Shell(gamma, mass, min_radius, self)
                for gamma, mass in zip(gamma_distribution, mass_distribution)
            ]
        )

        self._collisions = pd.DataFrame(
            columns=["radiated_energy", "gamma", "radius", "time"]
        )
        self._n_collisions = 0

        self._time = 0
        self._variability_time = variability_time

        self._store = store


        if self._store:

            self._shells.record_history(self._time)
        
        # we need to go ahead and emit a shell
        
        
        self._shells.activate_shells(self._time, self._shell_emit_iterator)
        self._shells.move(self._variability_time)
        self._time += self._variability_time
        self._shell_emit_iterator += 1


        if self._store:

            self._shells.record_history(self._time)
        

        
        self._shells.activate_shells(self._time, self._shell_emit_iterator)
        self._shells.move(self._variability_time)
        self._time += self._variability_time
        self._shell_emit_iterator += 1

        self._time_until_next_emission = self._variability_time

        if self._store:

            self._shells.record_history(self._time)
        


        
        self._status = True

        

    def start(self):

        while self._status:

            self._advance_time()

            if self._store:

                self._shells.record_history(self._time)
        


    def add_collision(self, radiated_energy, gamma, radius):

        self._collisions.loc[self._n_collisions] = [
            radiated_energy,
            gamma,
            radius,
            self._time,
        ]
        self._n_collisions += 1

    @property
    def n_collisions(self):
        return self._n_collisions

    def _advance_time(self):

        time_until_next_collision = self._shells.time_to_collisions

        # if there are any collisions

        if len(time_until_next_collision) > 0:

            # find the index of the minimum time differnec

            collision_idx = time_until_next_collision.argmin()

            # get that time difference

            delta_time = time_until_next_collision[collision_idx]

            if (
                delta_time > self._time_until_next_emission
                and self._shell_emit_iterator < self._n_shells
            ):

                # if the next collision will happen AFTER a shell will be
                # emitted, then we will go ahead and emit that shell

                # move the shells forward

                self._shells.move(self._time_until_next_emission)

                # increase the global time

                self._time += self._time_until_next_emission

                # emit the next shell

                self._shells.activate_shells(self._time, self._shell_emit_iterator)

                # reset time until next emission

                self._time_until_next_emission = self._variability_time

                # increase the shell counter

                self._shell_emit_iterator += 1

            else:

                # now we have a collision

                self._shells.move(delta_time)

                # advance the global time

                self._time += delta_time

                # collide the shells

                self._shells.velocity_ordered_shells[collision_idx].collide_shell(
                    self._shells.velocity_ordered_shells[collision_idx + 1]
                )
                # deactivate the forward shell

                self._shells.deactivate_shells(
                    self._time,
                    self._shells.velocity_ordered_shells[collision_idx + 1].shell_id,
                )

                # remove the time we spent colliding this shell
                
                self._time_until_next_emission -= delta_time
        else:

            if self._shell_emit_iterator == self._n_shells:

                self._status = False

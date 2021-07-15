__author__ = "grburgess"

from typing import List, Optional

import numpy as np
import pandas as pd

from ishockpy.shell import Shell, ShellSet

from .collision import Collision, CollisionHistory
from .distribution import InitialConditions
from .io.logging import setup_logger
from .shell_history import DetailedHistory

log = setup_logger(__name__)

MIN_DELTAT = 1e300


class Jet(object):
    def __init__(
            self, initial_conditions: InitialConditions, store=False
    ):

        self._n_shells: int = initial_conditions.n_shells

        self._shell_emit_iterator = 0

        # initialize the shells
        
        self._shells = ShellSet(
            [
                Shell(gamma, mass, initial_conditions.r_min, self)
                for gamma, mass in zip(initial_conditions.gamma_distribution.values,
                                       initial_conditions. mass_distribution.values)
            ]
        )

        self._collisions: List[Collision] = []
        self._n_collisions: int = 0

        self._time: float = 0.
        self._variability_time: float = initial_conditions.variability_time

        self._store: bool = store


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
        

        self._collision_history = CollisionHistory(self._collisions)

        if self._store:

            self._detailed_history: Optional[DetailedHistory]  = DetailedHistory([shell.history for shell in self._shells])

        else:

            self._detailed_history = None
    def add_collision(self, radiated_energy, gamma, radius):

        self._collisions.append( Collision(
            radiated_energy,
            gamma,
            radius,
            self._time,
        ))

        self._n_collisions += 1

    @property
    def shells(self) -> ShellSet:

        return self._shells
        
    @property
    def n_collisions(self):
        return self._n_collisions

    @property
    def collision_history(self) -> CollisionHistory:

        return self._collision_history

    
    def _advance_time(self):

        time_until_next_collision = self._shells.time_to_collisions

        
        #time_until_next_collision = time_until_next_collision[time_until_next_collision > 0]

        # if there are any collisions

        if len(time_until_next_collision) > 0:

            # find the index of the minimum time difference

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
                    self._shells.velocity_ordered_shells[collision_idx + 1].id,
                )

                # remove the time we spent colliding this shell
                
                self._time_until_next_emission -= delta_time
        else:

            if self._shell_emit_iterator == self._n_shells:

                self._status = False

            else:

                self._time += self._time_until_next_emission

                # emit the next shell

                self._shells.activate_shells(self._time, self._shell_emit_iterator)

                self._shell_emit_iterator += 1


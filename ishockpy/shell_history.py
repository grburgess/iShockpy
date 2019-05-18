import numpy as np



class ShellHistory(object):

    def __init__(self):


        
        self._gamma = []
        self._time = []
        self._radius = []
        self._mass=[]
        self._status = []

    def add_entry(self, time, gamma, radius, mass, status):

        self._time.append(time)
        self._radius.append(radius)
        self._gamma.append(radius)
        self._mass.append(mass)
        self._status.append(status)

    @property
    def status(self):

        return np.array(self._status)

    @property
    def time(self):

        return np.array(self._time)

    def radius_at_time(self, time):

        return np.array(self._radius)[idx]

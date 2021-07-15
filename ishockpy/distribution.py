import matplotlib.pyplot as plt
import numpy as np

from .io.logging import setup_logger
from .utils.constants import c
from .utils.numba_funcs import velocity

log = setup_logger(__name__)

class Distribution(object):

    def __init__(self, values: np.ndarray):
        """
        generic distribution

        :param values: 
        :type values: np.ndarray
        :returns: 

        """
        self._values: np.ndarray = values

    @property
    def values(self) -> np.ndarray:

        return self._values


class GammaDistribution(Distribution):
    
    def __init__(self):

        """
        The intial gamma distribution as a function of time

        """
               
        super(GammaDistribution, self).__init__(values = np.empty(0))

    def set_initial_times(self, initial_times: np.ndarray) -> None:
        """
        
        
        :param initial_times: 
        :type initial_times: np.ndarray
        :returns: 

        """
        self._initial_times: np.ndarray = initial_times

        self._values = self._generate_gamma()
        
    def _generate_gamma(self) -> None:

        log.error("You must inherit the gamma distribution to use it")

        
        raise NotImplementedError()

    @property
    def velocity(self) -> np.ndarray:
        """
        the velocity for a given gamma
        

        :returns: 

        """
        return velocity(self._values)

    
class MassDistribution(Distribution):
    
    def __init__(self, gamma_distribution: GammaDistribution, differential_energy: float):

        """
        A mass distribution

        :param gamma_distribution: 
        :type gamma_distribution: GammaDistribution
        :param differential_energy: 
        :type differential_energy: float
        :returns: 

        """

        values = differential_energy / (gamma_distribution.velocity * c**2)
        

        super(MassDistribution, self).__init__(values = values)

class RadialDistribution(Distribution):

    def __init__(self, gamma_distribution: GammaDistribution, r_min: float, times: np.ndarray) -> None:

        """
        Initial radial distribution

        :param gamma_distribution: 
        :type gamma_distribution: GammaDistribution
        :param r_min: 
        :type r_min: float
        :param times: 
        :type times: np.ndarray
        :returns: 

        """
        values = r_min + times * gamma_distribution.velocity[::-1]

        super(RadialDistribution, self).__init__(values = values)

        
        


        
class InitialConditions(object):

    def __init__(self, total_time: float, delta_time: float, total_energy: float,  gamma_distribtuion: GammaDistribution, r_min) -> None:

        """
        Initial conditions 

        :param total_time: 
        :type total_time: float
        :param delta_time: 
        :type delta_time: float
        :param total_energy: 
        :type total_energy: float
        :param gamma_distribtuion: 
        :type gamma_distribtuion: GammaDistribution
        :param r_min: 
        :type r_min: 
        :returns: 

        """

        self._total_time: float = total_time

        self._delta_time: float = delta_time

        self._total_energy: float = total_energy

        self._r_min: float = r_min
        
        self._n_shells: int = total_time // delta_time
        
        self._differential_energy = self._total_energy / self._n_shells

        initial_times = np.arange(0, total_time, delta_time)
        
        self._gamma_distribution: GammaDistribution = gamma_distribtuion

        # initialize the times
        
        self._gamma_distribution.set_initial_times(initial_times)
        
        self._mass_distribution: MassDistribution = MassDistribution(self._gamma_distribution, self._differential_energy)

        self._radial_distribution: RadialDistribution = RadialDistribution(self._gamma_distribution, self._r_min, initial_times)
        
    @property
    def n_shells(self) -> int:
        """
        The number of shells

        :returns: 

        """
        return self._n_shells


    @property
    def gamma_distribution(self) -> GammaDistribution:

        return self._gamma_distribution

    @property
    def mass_distribution(self) -> MassDistribution:

        return self._mass_distribution

    @property
    def radial_distribution(self) -> RadialDistribution:

        return self._radial_distribution

    @property
    def r_min(self) -> float:
        """
        minimum jet launching radius

        :returns: 

        """
        return self._r_min

    @property
    def variability_time(self) -> float:
        return self._delta_time
        


    def plot_gamma(self) -> plt.Figure:

        fig, ax = plt.subplots()


        ax.plot(self._mass_distribution.values / self._mass_distribution.values.sum(), self._gamma_distribution.values)

        ax.set_xlabel(r"M/M$_{\mathrm{total}}$")
        ax.set_ylabel(r"$\Gamma$")
    
        return fig

    def plot_mass(self) -> plt.Figure:

        fig, ax = plt.subplots()


        ax.plot(self._radial_distribution.values, self._mass_distribution.values)

        ax.set_xlabel("radius")
        ax.set_ylabel(r"mass")
    
        return fig


    
class SingleGammaCosine(GammaDistribution):

    def _generate_gamma(self):

        out = np.empty(len(self._initial_times))

        idx = self._initial_times <= 0.4 * self._initial_times.max()

        out[idx] = 250.-150.* np.cos(np.pi * self._initial_times[idx]/(.4 * self._initial_times.max()))

        out[~idx] = 400.

        return out

        
class SingleGammaStep(GammaDistribution):

    def _generate_gamma(self):

        out = np.empty(len(self._initial_times))

        idx = self._initial_times >= self._initial_times.max() * 0.25

        out[idx] = 400

        out[~idx] = 100

        return out
        


    

from pathlib import Path

import numpy as np
import pytest

from ishockpy import InitialConditions, Jet, SingleGammaStep


@pytest.fixture(scope="session", autouse=True)
def finished_jet():

    TOTAL_ENERGY = 2*1.E51/(4* np.pi)



    dT = .05
    t0 = 0.
    Rmin = 1.2E4
    #iTime = linspace(T0+dT,0.,NUM_SHELLS)
    tw=10.


    TOTAL_ENERGY = 2*1.E51/(4* np.pi)


    ic = InitialConditions(total_time=tw,
                       delta_time=dT,
                       total_energy=TOTAL_ENERGY,
                       gamma_distribtuion= SingleGammaStep(),
                       r_min=Rmin
                      
                      
                      )


    jet = Jet(initial_conditions=ic,store=True)

    jet.start()

    yield jet

    # cleanup in files
    
    p = Path(".")


    
    for f in p.glob("*.h5"):

        f.unlink()

    
    

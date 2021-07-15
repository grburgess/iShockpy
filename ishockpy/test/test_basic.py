import numpy as np

from ishockpy import *


def test_basic():
    c=2.99E10
    TOTAL_ENERGY = 2*1.E51/(4* np.pi)



    dT = .005
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

    
    

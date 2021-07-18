---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

<!-- #region -->
# Quick Start


## Jet initial conditions
In order to simulate a gamma-ray burst (GRB) with `ishockpy` we first need to set up the initial conditions of the jet. 

The primary source condition is the radial Lorentz factor distribution of the outflow. `ishockpy` specifies this via a customizable class call `GammaDistribution`. Let's specify on outflow simulat to that of [Daigne and Mochkovich 1999](https://watermark.silverchair.com/296-2-275.pdf?token=AQECAHi208BE49Ooan9kkhW_Ercy7Dm3ZL_9Cf3qfKAc485ysgAAAtEwggLNBgkqhkiG9w0BBwagggK-MIICugIBADCCArMGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQM3vv18XgfCA4D1sNwAgEQgIIChOAd7oQzos_CEcXsNMVIbSPh0uto_GL25Yz8l7puZrMIzbV61JWhMVdzl9DP75JworwxLThB1qHzGSoPoS_j89EunfXMFaGULqhsScVMAu2ehjTxxV6FlAeo4JuDDleZJgmPxAgIPVWTdRziEykQ5kPtlZOk97XWORff0oBY3N_v7bNp6T6QAxBYLjtS5aomjXwM4jGnWb8SJv1Rg7f3HFa-kwWqnzQ-L8imstotblJG3n0EJJ8s2mPk1pCUrEDGZQPR2qpHPmKKrHApBRVro8IW7e8KQOBGA5ueSdYoFS7vnOMD2p-2E46MsDISnVoRcKEG2E_vT3GieCiN0zvUIPtsIYbytDViemTiO7B3TnqayoLG55cb5Foh8ZmPGku31Jt5sdhYJgOhVqsg9n9KkvVn9rSk46Ouv5J9D0fT2pqt9foN9Eq29nGZpdreahx6G47yg7GUCoA-fzFbioIz3nA9X5OtsyB2u3so6NmLZs9MtPXbBjT9B6RmjQhlA8mjDyRwCZetjiKCec2mTYD5TWQU0biyqDhAEKqID1wAPf02KeNDx2geRtsp8ZBdLYFxdqw7P97frFWEi8GVNumSmpboTL4NR-ldUNvEqfLz6TW5RLz-GVA_PM8qGpM1BdUoUx40H-Vgy9jsl-_spVhc11Q1-LYQO4XnDpnHpSrmOeZ39F9FuQ8LM5P66kLXP9FFDpozGVpOPXJ9CeWSGNxjg1k7PxQYB-r1SLzdcznWNLf6jmUDVf2lNGr0DBADc3B0QjxIbgWyRZ5U-H7xcQBX6qaga659ibjU4Vh-zMCIr-6x6D624Ge3LJpKxtj8RYpfrqdWBozFVoFPa_hPkH3EfqIHQH0f).





<!-- #endregion -->

```python
import ishockpy
import numpy as np
import matplotlib.pyplot as plt

%matplotlib inline
```

```python
class DMGamma(ishockpy.GammaDistribution):
    
    def _generate_gamma(self):

        out = np.empty(len(self._initial_times))

        # we must specify the value of gamma
        # as a function of the EMITTED time of
        # the shells
        
        idx = self._initial_times >= self._initial_times.max() * 0.2

        out[idx] = 400 # later times have fast wind

        out[~idx] = 100

        return out
        

```

Now that we have of Lorentz factor distribution set, we can build our initial conditions,

```python

variability_time = .002 # s
total_time = 10. # s
r_min = 1.2E4
total_energy = 1.E52


initial_condistions = ishockpy.InitialConditions(total_time=total_time,
                   delta_time=variability_time,
                   total_energy=total_energy,
                   gamma_distribtuion= DMGamma(),
                   r_min=r_min


                  )
```

```python
initial_condistions.plot_gamma();
```

```python
initial_condistions.plot_mass();
```

## Create the jet

To create the jet, we simply need to pass our initial conditions to the `Jet` constructor. If we activeate the `store` object, then a detailed history of every shell is recorded. Otherwise, we only store information about the internal collisions.


```python
jet = ishockpy.Jet(initial_condistions, store=True)
```

Now we simply start the jet. Shells will be emitted, evolved, and collided until there are no more collisions possible (shells have monotonically increasing gamma with radius or they have all passed the optional maximum radius).

```python
jet.start()
```

## History of the jet

The collisons are store in the `collision_history` member of the jet which stores, the time, radius, $Gamma_r$ and radiated_energy of the jet:

```python
fig, ax = plt.subplots()
ax.plot(jet.collision_history.time_observer,
        jet.collision_history.radiated_energy,'.', markersize=1)

ax.set_xlabel(r't$_{\mathrm{obs}}$')

ax.set_ylabel(r'radiated energy')
```

```python
fig, ax = plt.subplots()
ax.plot(jet.collision_history.time_observer,
        jet.collision_history.gamma,'.', markersize=1)

ax.set_xlabel(r't$_{\mathrm{obs}}$')

ax.set_ylabel(r'$Gamma_r$')
```

If the store option was used, the detailed history of each shell can be accessed:

```python
jet.detailed_history.histories[500].gamma
```

```python

```

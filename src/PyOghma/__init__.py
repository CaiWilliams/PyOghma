"""
PyOghma: A Python API for OghmaNano

PyOghma provides a programmatic interface to configure, execute, and analyze drift-diffusion simulations using OghmaNano. 
It simplifies workflows for researchers and engineers by enabling seamless integration of optical, thermal, epitaxy, 
and simulation configurations. PyOghma also includes tools for analyzing simulation results and calculating key metrics.

Modules:
- OghmaNano: Main class to manage simulations and configurations.
- Results: Class to handle and analyze simulation results.
- Calculate: Classes to compute metrics such as ideality factor, transport resistance, and pseudo JV curves.
"""

from .OghmaNano import OghmaNano
# OghmaNano: Main class to manage simulations and configurations for OghmaNano.

from .OghmaResults import Results
# Results: Class to handle the results of simulations and experiments.

from .Calculate import Ideality_Factor, Transport_Resistance, Psudo_JV
# Ideality_Factor: Class to calculate the ideality factor of a solar cell based on experimental data.
# Transport_Resistance: Class to calculate transport resistance based on experimental data.
# Psudo_JV: Class to calculate the pseudo JV of a diode.

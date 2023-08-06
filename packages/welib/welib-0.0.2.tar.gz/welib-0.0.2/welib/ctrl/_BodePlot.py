
import os
import matplotlib.pyplot as plt   # MATLAB plotting functions
from control import *
from control.freqplot import bode_plot, _bode_defaults
from control.xferfcn import TransferFunction

import numpy as np

# Parameters defining the system
m = 250.0           # system mass
k = 40.0            # spring constant
b = 60.0            # damping constant


# System matrices
A = [[0, 1.], [-k/m, -b/m]]
B = [[0, 0], [0, 1/m]]
print(B)
C = [[1., 0]] # output position
sys = ss(A, B, C, 0)
bode(sys)

C = [[0., 1]] # output speed
sys = ss(A, B, C, 0)
bode(sys)


omega = default_frequency_range(sys, Hz=True, number_of_samples=None)


plt.show()

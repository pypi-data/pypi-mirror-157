"""
Compute and plots the analytical modes of a uniform beam with different boundary conditions
"""
import numpy as np
from welib.beams.theory import *
import matplotlib
from pyFAST.tools.eva import eigA
from pyFAST.input_output.fast_linearization_file import FASTLinearizationFile

L  = 100   
EI = 1037.13E9
m  = 9517.14
freq,x,U,V,K = UniformBeamBendingModes('unloaded-free-free',EI,m,A=1,L=L, nModes=8)
print(freq)


# --- Open lin File
linFile = 'FF.lin.txt'
lin = FASTLinearizationFile(linFile)

# --- Perform eigenvalue analysis
fd, zeta, Q, f0 = eigA(lin['A'])
b=np.logical_and(f0>0.1, f0<180)
f0   = f0[b]
zeta = zeta[b]
print('Nat. freq. [Hz], Damping ratio [%]')
print(np.column_stack((f0,zeta*100)))

print(np.around(freq[0::],1))
print(np.around(f0[0::2]  ,1))

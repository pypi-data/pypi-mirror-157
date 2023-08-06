
import os
import matplotlib.pyplot as plt   # MATLAB plotting functions
from control import *
from control.freqplot import bode_plot, _bode_defaults
from control.xferfcn import TransferFunction
# see xferfcn

import numpy as np





# 
# 
# --------------------------------------------------------------------------------}
# --- Control toolbox vs manual 
# --------------------------------------------------------------------------------{
# omega0=10
# # --- Control toolbox
# sys=TransferFunction([1,0], [1,omega0]) # s + 0  / s+omega0 
# print(sys)
# bode_plot(sys)
# 
# # --- "manual"
# def highpass_H(s,omega0):
#     return s/(s+omega0)
# 
# vH=highpass_H(1j*omega , omega0)
# 
# print(vH-sys(omega*1j))
# 
# phase = np.angle(vH)
# mag   = np.abs(vH)
# 
# 
# 
# fig,axes = plt.subplots(2, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
# fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
# ax=axes[0]
# ax.loglog(omega, mag  , label='')
# ax.set_xlabel('')
# ax.set_ylabel('')
# 
# ax=axes[1]
# ax.semilogx(omega, phase*180/np.pi  , label='')
# ax.set_xlabel('')
# ax.set_ylabel('')
# 
# 
# ax.legend()
# ax.tick_params(direction='in')
# plt.show()



omega=np.logspace(-2,4,200)
db=False

# --- First order high-pass filter
omega0=10
sys=TransferFunction([1,0], [1,omega0]) # s + 0  / s+omega0 
print(sys)
bode_plot(sys,omega,dB=db)

# --- First order low-pass filter
omega0=10
sys=TransferFunction([omega0], [1,omega0]) #omega0  / s+omega0 
print(sys)
bode_plot(sys,omega,dB=db)


# --- Second order band-pass filter
omega0=10
zeta =10
sys=TransferFunction([2*zeta*omega0,0], [1,2*zeta*omega0, omega0**2]) #2*zeta*omega0s  / (s^2 2zom s +om^2)
print(sys)
bode_plot(sys,omega,dB=db)

# --- Second order low-pass filter
omega0=10
zeta =1
sys=TransferFunction([omega0**2], [1,2*zeta*omega0, omega0**2]) #2*zeta*omega0s  / (s^2 2zom s +om^2)
print(sys)
bode_plot(sys,omega,dB=db)






plt.show()

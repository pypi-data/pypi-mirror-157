# secord.py - demonstrate some standard MATLAB commands
# RMM, 25 May 09

import os
import matplotlib.pyplot as plt   # MATLAB plotting functions
from control import *
from control.freqplot import *
#from control.matlab import *  # MATLAB-like functions

import math
def default_frequency_range(syslist, Hz=None, number_of_samples=None,
                            feature_periphery_decades=None):
    """Compute a reasonable default frequency range for frequency
    domain plots.

    Finds a reasonable default frequency range by examining the features
    (poles and zeros) of the systems in syslist.

    Parameters
    ----------
    syslist : list of LTI
        List of linear input/output systems (single system is OK)
    Hz : bool
        If True, the limits (first and last value) of the frequencies
        are set to full decades in Hz so it fits plotting with logarithmic
        scale in Hz otherwise in rad/s. Omega is always returned in rad/sec.
    number_of_samples : int, optional
        Number of samples to generate.  The default value is read from
        ``config.defaults['freqplot.number_of_samples'].  If None, then the
        default from `numpy.logspace` is used.
    feature_periphery_decades : float, optional
        Defines how many decades shall be included in the frequency range on
        both sides of features (poles, zeros).  The default value is read from
        ``config.defaults['freqplot.feature_periphery_decades']``.

    Returns
    -------
    omega : array
        Range of frequencies in rad/sec

    Examples
    --------
    >>> from matlab import ss
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> omega = default_frequency_range(sys)

    """
    # This code looks at the poles and zeros of all of the systems that
    # we are plotting and sets the frequency range to be one decade above
    # and below the min and max feature frequencies, rounded to the nearest
    # integer.  It excludes poles and zeros at the origin.  If no features
    # are found, it turns logspace(-1, 1)

    # Set default values for options
    number_of_samples = config._get_param( 'freqplot', 'number_of_samples', number_of_samples)
    feature_periphery_decades = config._get_param( 'freqplot', 'feature_periphery_decades', feature_periphery_decades, 1)

    # Find the list of all poles and zeros in the systems
    features = np.array(())
    freq_interesting = []

    # detect if single sys passed by checking if it is sequence-like
    if not getattr(syslist, '__iter__', False):
        syslist = (syslist,)

    for sys in syslist:
        try:
            # Add new features to the list
            if sys.isctime():
                features_ = np.concatenate((np.abs(sys.pole()), np.abs(sys.zero())))
                # Get rid of poles and zeros at the origin
                features_ = features_[features_ != 0.0]
                features = np.concatenate((features, features_))
            elif sys.isdtime(strict=True):
                fn = math.pi * 1. / sys.dt
                # TODO: What distance to the Nyquist frequency is appropriate?
                freq_interesting.append(fn * 0.9)

                features_ = np.concatenate((sys.pole(),
                                            sys.zero()))
                # Get rid of poles and zeros
                # * at the origin and real <= 0 & imag==0: log!
                # * at 1.: would result in omega=0. (logaritmic plot!)
                features_ = features_[
                    (features_.imag != 0.0) | (features_.real > 0.)]
                features_ = features_[
                    np.bitwise_not((features_.imag == 0.0) &
                                   (np.abs(features_.real - 1.0) < 1.e-10))]
                # TODO: improve
                features__ = np.abs(np.log(features_) / (1.j * sys.dt))
                features = np.concatenate((features, features__))
            else:
                # TODO
                raise NotImplementedError(
                    "type of system in not implemented now")
        except NotImplementedError:
            pass

    # Make sure there is at least one point in the range
    if features.shape[0] == 0:
        features = np.array([1.])

    if Hz:
        features /= 2. * math.pi
        features = np.log10(features)
        lsp_min = np.floor(np.min(features) - feature_periphery_decades)
        lsp_max = np.ceil(np.max(features) + feature_periphery_decades)
        lsp_min += np.log10(2. * math.pi)
        lsp_max += np.log10(2. * math.pi)
    else:
        features = np.log10(features)
        lsp_min = np.floor(np.min(features) - feature_periphery_decades)
        lsp_max = np.ceil(np.max(features) + feature_periphery_decades)
    if freq_interesting:
        lsp_min = min(lsp_min, np.log10(min(freq_interesting)))
        lsp_max = max(lsp_max, np.log10(max(freq_interesting)))

    # TODO: Add a check in discrete case to make sure we don't get aliasing
    # (Attention: there is a list of system but only one omega vector)

    # Set the range to be an order of magnitude beyond any features
    if number_of_samples:
        omega = np.logspace(
            lsp_min, lsp_max, num=number_of_samples, endpoint=True)
    else:
        omega = np.logspace(lsp_min, lsp_max, endpoint=True)
    return omega



# Parameters defining the system
m = 250.0           # system mass
k = 40.0            # spring constant
b = 60.0            # damping constant


# System matrices
A = [[0, 1.], [-k/m, -b/m]]
B = [[0], [1/m]]
C = [[1., 0]] # output position
sys = ss(A, B, C, 0)
bode(sys)

C = [[0., 1]] # output speed
sys = ss(A, B, C, 0)
bode(sys)


#omega = np.logspace(np.log10(omega[0]), np.log10(omega[-1]), num=len(omega), endpoint=True)
#print(omega)







omega = default_frequency_range(sys, Hz=True, number_of_samples=None)
print(omega)
print(sys)
print(bode.__globals__['__file__'])
print(type(sys))
#         , omega=None,
#               plot=True, omega_limits=None, omega_num=None,
#               margins=None, *args, **kwargs):

# ---





# Step response for the system
# plt.figure(1)
# yout, T = step(sys)
# plt.plot(T.T, yout.T)
# plt.show(block=False)

# Bode plot for the system
#plt.figure(2)
#mag, phase, om = bode(sys, logspace(-2, 2), Plot=True)
#plt.show(block=False)

# Nyquist plot for the system
# plt.figure(3)
# nyquist(sys, logspace(-2, 2))
# plt.show(block=False)

# Root lcous plot for the system
# rlocus(sys)

plt.show()

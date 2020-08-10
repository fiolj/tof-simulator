# coding: utf-8

from tofsim import ToF
import numpy as np
import matplotlib.pyplot as plt

# Create the TOF with all isotopes from Xe, Ar and Kr
T = ToF('Xe,Ar,Kr')
T.Vs = 120                      # Extraction voltaje
T.Vd = 3000                     # Acceleration voltaje
T.signal()                      # Make the spectra

p = T.get_statistics_peaks()    # Get the peaks

t, pos, width = np.array([[T.fragments[k]['M'], v['position'], v['width']] for k, v in p.items()]).T

# Plot the data
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(8, 10))
ax[0].plot(t, pos, '-s', label='Peak position')
ax[1].plot(t, width, '-o', label='Peak width')
ax[1].set_xlabel(r'Mass [AMU]')

ax[0].set_ylabel(r'Time [$\mu s$]')
ax[1].set_ylabel(r'Time [$\mu s$]')
ax[0].legend(loc='best')
ax[1].legend(loc='best')
plt.subplots_adjust(hspace=0)

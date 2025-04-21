# coding: utf-8

from tofsim import ToF
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

# Create the TOF with all isotopes from Li, Ar 
T = ToF('Li, Ar')

T.Vs = 120                      # Extraction voltaje
T.Vd = 3000                     # Acceleration voltaje


T.signal()                      # Make the spectra

p = T.get_statistics_peaks()    # Get the peaks

print(p)                        # Print the peaks

# Alternatively, you can print the data into table form with tabulate
headers = ['Fragment'] + p.headers
print(tabulate(p.tolist(), headers=headers, tablefmt='fancy_grid'))

# # Plot the data
# pa = np.asarray(p.tolist())

# We will plot the position and width of each peak as a function of the mass of the fragment:
x = [T.fragments[k]['M'] for k in p]
ypos = [p[k]['position'] for k in p]
ywidth =  [p[k]['width'] for k in p]

plt.ion()

fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(8, 10))
ax[0].plot(x, ypos, '-s', label='Peak position')
ax[1].plot(x, ywidth, '-o', label='Peak width')
ax[1].set_xlabel(r'Mass [AMU]')

ax[0].set_ylabel(r'Time [$\mu s$]')
ax[1].set_ylabel(r'Time [$\mu s$]')
ax[0].legend(loc='best')
ax[1].legend(loc='best')
plt.subplots_adjust(hspace=0)

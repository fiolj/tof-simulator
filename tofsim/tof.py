# -*- coding: utf-8 -*-
#
# This file is part of tof-simulator.
#
# tof-simulator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tof-simulator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tof-simulator.  If not, see <https://www.gnu.org/licenses/>.
import numpy as np
from math import sqrt
from configparser import ConfigParser
from pathlib import Path
from .nist_elem import Sustancias

_default_conffile = Path(__file__).resolve().parent / 'tof.conf'

_tof_esquema = r"""
Diagram of TOF
--------------

  |<-- 2s --->|<--- d ---->|<--------------D---------------->|
 _____________________________________________________________
  |           |            |                                 |
  |     Vs    |     Vd     |         E=0                     |
  |           v            |                                  \
  |     O  - - - - - - - - - - - - - - - - - - - - - - - - -   >~~~ Detector
  |           ^ r0         |                                  /
  |           |            |                                 |
 _|___________|____________|_________________________________|

"""

_default_param = {
    's': 1.0,                   # Distance from center to first plate in cm
    'd': 2.54,                  # Distance between plates in cm (second stage)
    'D': 105.,                  # Distance of free flight
    'Vs': 200,                  # Potential Es in eV
    'Vd': 3000,                 # Potential Ed in eV
    'ds': 0.1,                  # Radio del spot del laser in cm
    'dt': 0.008,                # Laser-pulse duration (microsegundos)
    't0': 0.,                   # Offset in time of TOF (experimental)
    'r0': 1.e3                  # Radio de abertura después de la extracción
}

_default_conditions = {
    'Temperature': 300,
    'Npoints': 1000000,      # Number of simulation particles
    'timeprec': 0.002,       # Precision de tiempo (microsegundos)
    'posdist': 'normal',     # Disribución en posición de la intensidad del láser
    'tdist': 'normal',       # Distribución en tiempos de la intensidad del láser
    'v_inicial': 0.          # Velocidad de grupo del gas en sqrt(2*eV)
}

localconf = Path().cwd() / 'tof.conf'
_conffile = localconf if localconf.exists() else _default_conffile


def _get_nearest(x, x0):
  """Find index of value on x nearest to x0, for sorted x  """
  # imax = np.abs(x - x0).argmin()
  imax = np.searchsorted(x, x0, side="left")
  if x0 - x[imax] > x[imax + 1] - x0:
    imax += 1
  if imax > len(x):
    imax = len(x)
  return imax


def _get_peak(x, y, N=10):
  """Calculation of the peak position for the array y.
  Fits the proximity of the maximum with a parabole to get its maximum
  """

  j = y.argmax()

  p = np.polyfit(x[j - N:j + N], y[j - N:j + N], 2)

  x0 = np.array([np.sqrt(p[2] / p[0]), -2 * p[2] /
                p[1], -p[1] / (2 * p[0])]).mean()
  y0 = np.polyval(p, x0)
  imax = _get_nearest(x, x0)  # Find the closest index

  return imax, x0, y0


def get_one_peak(x, y, fwidth=1 / np.e):
  """Returns features of a single peak.

  Returns a list with:

  - Position 0: indexes of position of:

    - lower half height
    - center
    - upper half height

  - Position 1: values of x

  - Position 2: values of y

  """
  im, xm, ym = _get_peak(x, y)
  yf = fwidth * ym
  i2p = im + np.abs(y[im:] - yf).argmin()
  i2m = im - np.abs(y[im::-1] - yf).argmin()
  return [(i2m, im, i2p), (x[i2m], xm, x[i2p]), (y[i2m], ym, y[i2p])]


class ToF(object):
  """
  The ToF object defines and handles all aspects of a Time-of-Flight spectrometer

  The following parameters related to the construction and operation are included:
  Distances, voltages, working temperature, particle velocity fields and dispersion,
  time duration and size of the ionizing beam are also included.

  Examples
  --------
  ::

    tof_parameters= {
      's': 0.7,                    # Distance from center to first plate in cm
      'd': 2.54,                   # Distance between plates in cm (second stage)
      'D': 100.,                   # Distance of free flight
      'Vs': 500,                   # Potential Es in eV
      'Vd': 1900,                  # Potential Ed in eV
      'ds': 0.05,                  # Radio del spot del laser in cm
      'dt': 0.008,                 # Laser-pulse duration
      't0': 0.,                    # Offset in time of TOF (experimental)
      'r0': 1.e3,                  # Aperture radius after extraction (in mm?)
      }

    # We can create the object with the parameters desired
    T = ToF(['Ar', 'N2', 'CO2'],**tof_parameters)

    # We can also load parameters from a file
    T.load_conf_file('tof.conf')

    T.signal()     # Calculate the signals

    # Plot the signals
    T.make_plot(fname='tof2.png', negative=True, show_legend=True, show_all=True)

    # Just printing the object gives all the information on construction and
    # condition parameters as well as the substances being simulated
    print(T)

  """

  tof_parameters = ['s', 'd', 'D', 'Vs', 'Vd', 'ds', 'dt', 't0', 'r0']
  adic_parameters = ['Temperature', 'Npoints', 'timeprec', 'posdist',
                     'tdist', 'v_inicial']

  _esquema = _tof_esquema

  def __init__(self, substances=None, **kwds):
    """
    Initialize a ToF object defines and handles all aspects of a Time-of-Flight spectrometer

    Parameters
    ----------
    self: type
      description
    substances: str
      A string of comma-separated substances
    kwds:
      keyword arguments may include any of those defining TOF parameters o conditions. May include:

    - 's': float
          Distance from center to first plate in cm
    - 'd': float
          Distance between plates in cm (second stage)
    - 'D': float
          Distance of free flight
    - 'Vs': float
          Potential Es in eV
    - 'Vd': float
          Potential Ed in eV
    - 'ds': float
          Radio del spot del laser in cm
    - 'dt': float
          Laser-pulse duration (microsegundos)
    - 't0': float
          Offset in time of TOF (experimental)
    - 'r0': 1.e3
          Radio de abertura después de la extracción
    - 'Temperature': float
          Temperature of the gas
    - 'Npoints': intended
          Number of simulation particles
    - 'timeprec': float
          Precision in time: Time step in the spectra (microsegundos)
    - 'posdist': 'normal' or 'uniform'
          Spatial disribution of ionizing beam
    - 'tdist': 'normal' or 'uniform'
          Time distribution of ionizing pulse beam
    - 'v_inicial': float
          Group-velocity of the gas (in units of sqrt(2*eV))

    """
    # First set default values
    self.__dict__.update(_default_param)
    self.__dict__.update(_default_conditions)

    masas = self.load_conf_file(_conffile)
    # Then, process input (overwrite default)
    self.__dict__.update(kwds)
    self.times = None

    if substances is not None:
      self.fragments = Sustancias(substances)
    else:
      self.fragments = Sustancias()
      if masas:
        self.add_substances(masas)

  def add_substances(self, substances, threshold=1.e-3):
    """Add substances to be simulated.

    Parameters
    ----------

    substances: str
       Comma-separated string, or list of strings, each substance may have the form            SF5^{+}, SF5^{++}, SF5^+, S^2+
    threshold: float
       Minimum abundance of a given isotope to be included (default 1.e-3).

    """
    self.fragments.thr = threshold  # Threshold de los isótopos a incluir
    self.fragments.add(substances)

  def remove_substances(self, sustancias):
    """Remove substances from the simulation

    Parameters
    ----------
    self: type
      description
    sustancias: str or list of strings
      substances or fragments to remove
    """
    self.fragments.remove(sustancias)

  def _message(self, message):
    # log to terminal window
    print(message)

  def load_conf_file(self, fname):
    """Load a configuration file, update tof parameters, and also return masses if present."""

    if fname is None:
      return None

    if not Path(fname).exists():
      self._message('Configuration file {0} does not exist'.format(fname))
      return None

    parser = ConfigParser()
    parser.optionxform = str
    parser.read(fname)

    if parser.has_section('tof'):
      for name, value in parser.items('tof'):
        if name in self.tof_parameters:
          self.__dict__[name] = float(value)

    if parser.has_section('condition'):
      for name, value in parser.items('condition'):
        if name in ['Temperature', 'timeprec', 'v_inicial']:
          self.__dict__[name] = float(value)
        elif name == 'Npoints':
          self.__dict__[name] = int(value)
        elif name in ['posdist', 'tdist']:
          self.__dict__[name] = value

    sections = parser.sections()
    sections.remove('tof')
    sections.remove('condition')
    m = {}
    for section_name in sections:
      m[section_name] = {}
      for name, value in parser.items(section_name):
        try:
          m[section_name][name] = float(value)
        except BaseException:
          m[section_name][name] = value
    return m

  def save_conf_file(self, fname, masas={}):
    """Save configuration data for tof and masses to a file
    """
    parser = ConfigParser()
    parser.optionxform = str
    parser.add_section('tof')
    parser.add_section('condition')
    for opt in self.tof_parameters:
      parser.set('tof', opt, str(self.__dict__[opt]))
    for opt in self.adic_parameters:
      parser.set('condition', opt, str(self.__dict__[opt]))

    if not masas:
      masas = self.fragments
    for m, values in list(masas.items()):
      parser.add_section(m)
      for k, v in list(values.items()):
        parser.set(m, k, str(v))
    fo = open(fname, 'w')
    parser.write(fo)
    fo.close()

  def get_tof_parameters(self, explain=False):
    """Returns the parameters of TOF in a dict.

    Parameters
    ----------
    explain: bool
      If `True` add an ascii graphic with the diagram of the TOF

    """
    p = {}
    for k in self.tof_parameters:
      p[k] = self.__dict__[k]
    if explain:
      return p, self._esquema
    return p

  def __str__(self):
    s = """
Time-of-Flight
**************

Construction parameters:
"""
    s += self._esquema
    for k in self.tof_parameters:
      s += "  {} = {}\n".format(k, self.__dict__[k])

    s += "\n\nAditional parameters:\n\n"
    for k in self.adic_parameters:
      s += "  {} = {}\n".format(k, self.__dict__[k])

    s += "\n\nFragments detected:\n"
    s += str(self.fragments)

    return s

  def set_initial_distribution(self):
    """Initial velocity and position distributions"""
    # Energy in eV  (= k_B * T)
    U0 = 0.025 * (1.e-10 + self.Temperature) / 300.
    sigma = np.sqrt(U0)         # Velocity spread (M=1)
    # velocidades iniciales en la dirección de la extracción
    v_0 = np.random.normal(loc=self.v_inicial, scale=sigma, size=self.Npoints)
    # velocidades iniciales en la dirección perpendicular a la extracción
    v_1 = np.random.normal(loc=0, scale=sigma, size=self.Npoints)
    v_2 = np.random.normal(loc=0, scale=sigma, size=self.Npoints)
    v_perp = np.sqrt(v_1**2 + v_2**2)

    if self.posdist.lower() == 'normal':
      # Distribución de posiciones: Gaussiana
      x_0 = np.random.normal(loc=0.0, scale=self.ds / 2., size=self.Npoints)
      x_0 = np.where(np.abs(x_0) <= self.s, x_0,
                     x_0 - (x_0 // self.s) * self.s)
    else:
      # Distribución de posiciones: Uniforme
      x_0 = (2 * np.random.random_sample(self.Npoints) - 1) * self.ds

    # Keep initial velocity and position distributions
    counts, bins_i = np.histogram(v_0, bins=100, density=True)
    self.v_i = np.array([(bins_i[1:] + bins_i[:-1]) / 2., counts])
    counts, bins_i = np.histogram(x_0, bins=100, density=True)
    self.x_i = np.array([(bins_i[1:] + bins_i[:-1]) / 2., counts])
    return x_0, v_0, v_perp

  def _filter_abertura(self, x0, v0, vp):
    "Filter particles that may pass through an aberture of radius self.r0"
    t_ext = self.time_of_extract(x0, v0)
    cond = vp * t_ext <= self.r0
    return x0.compress(cond), v0.compress(cond)

  def signal(self, particles=None):
    """Evaluate the signal that would produce the particles in the ToF

    Parameters
    ----------
    particles : dict each item is a dictionary that should have
        - key: is the label of the mass
        - 'M': Mass (in AMU)
        - 'P': (float in range 0 to 1) Abundance
        - 'L': an (optional, possibly formatted) label, otherwise the key is used

    If particles is None => Usa los fragments

    Returns
    -------
    times : numpy array
      Sets the object variable self.times and also returns its value
    """
    if particles is None:
      particles = self.fragments

    x0, v0, v_p = self.set_initial_distribution()

    # Filtramos las partículas que no pueden pasar la abertura de la extracción
    x_0, v_0 = self._filter_abertura(x0, v0, v_p)

    Time = self.time_of_flight(x_0, v_0)
    self.times = self.calc_signal(particles, Time)
    # Add the theoretical mean value
    self.mean_times()
    return self.times

  def calc_signal(self, particles, Time):
    "Calculo de los histogramas para generar la señal de un grupo de partículas"

    # Incerteza en el tiempo inicial (duracion del laser)
    if self.dt > 1.e-6:
      if self.tdist.lower() == 'normal':
        Dt = np.random.normal(loc=0.0, scale=self.dt / 2., size=len(Time))
      else:
        Dt = 2 * self.dt * np.random.random(len(Time)) - self.dt
    else:
      Dt = 0.

    sm = np.sqrt([p['M'] for p in list(particles.values())])
    tmin, tmax = sm.min() * Time.min() - Dt.max(), sm.max() * Time.max() + Dt.max()
    step = (tmax - tmin) / 20.
    tmin -= step
    tmax += step
    Nbins = min(int((tmax - tmin) / self.timeprec), 1000)

    x = {}
    x['signal'] = None

    for k, p in list(particles.items()):
      hist, bins = np.histogram(sqrt(p["M"]) * Time + Dt,
                                range=(tmin, tmax), bins=Nbins, density=True)
      x[k] = p["P"] * hist
      if x['signal'] is None:
        x['signal'] = x[k].copy()  # Fallaba sin .copy()
      else:
        x['signal'] += x[k]
    x['time'] = np.array((bins[1:] + bins[:-1]) / 2. + self.t0)  # Eje x
    return x

  def mean_times(self, x0=0.):
    """Evaluate the 'main' time of each species, given as if generated in ideal conditions:

      - At time t=0
      - At rest (null initial velocity)
      - At a distance x0 from the center of the extraction plates (s = 0)

    """
    Time = self.time_of_flight(x0, self.v_inicial)
    m = self.fragments
    for k in m.ListItems:
      s = m[k]
      if s['q'] >= 1:
        s['t'] = sqrt(s['M'] / s['q']) * Time + self.t0
      else:
        s['t'] = 0

  def get_statistics_peaks(self, substances='all', fwidth=1 / np.e):
    """Find peaks

    Parameters
    ----------
    substances: 'all' or list
      - if 'all' find the peak for every fragment in the TOF
      - if substance is a list of strings, each element must be a fragment in TOF

    fwidth: float
       fraction of the maximum at which to evaluate the full width.
       For instance, fwidth = 0.5 corresponds to FWHM
    """
    if substances == 'all':
      frags = list(self.fragments.ListItems)
    elif substances in self.fragments.ListItems:
      frags = [substances]
    else:
      frags = []

    peaks = Peaks()
    for m in frags:
      ind, x, y = get_one_peak(
          self.times['time'], self.times[m], fwidth=fwidth)
      peaks[m] = {
          'index': ind,
          'position': x[1],
          'height': y[1],
          'width': x[2] - x[0],
          # 'x': x,
          # 'y': y
          }
      
    return peaks

  def time_of_extract(self, x_0, v_0):
    """Evaluates the time taken to extract a particle of mass M=1 and charge q=1 with
    initial velocity v_0 and position x_0 from the extraction plates."""
    self.Es = self.Vs / (2 * self.s)
    self.Ed = self.Vd / self.d

    coef = 1.02
    s0 = (self.s - x_0)
    a_s = self.Es
    if a_s > 1.e-25:
      Ts = coef / (a_s) * (-v_0 + np.sqrt(np.square(v_0) + 2 * a_s * s0))
    else:
      Ts = coef * s0 / v_0
    return Ts

  def time_of_flight(self, x_0, v_0):
    """Evaluates the time-of-flight of a particle of mass M=1 and charge q=1 with
    initial velocity v_0 and position x_0."""
    self.Es = self.Vs / (2 * self.s)
    self.Ed = self.Vd / self.d

    coef = 1.02
    s0 = (self.s - x_0)
    a_s = self.Es
    if a_s > 1.e-25:
      Ts = coef / (a_s) * (-v_0 + np.sqrt(np.square(v_0) + 2 * a_s * s0))
    else:
      Ts = coef * s0 / v_0

    v_s = v_0 + a_s * Ts
    # pulsado = True
    # if pulsado:
    #     t_p = 50.e-3       # Duración del pulso en microsegundos

    #     v_s = v_0 + a_s * t_p
    #     Ts = coef * (self.s + 0.5 * a_s * t_p**2) / v_s

    a_d = self.Ed
    if a_d > 1.e-25:
      Td = coef / (a_d) * (-v_s + np.sqrt(np.square(v_s) + (2 * a_d * self.d)))
    else:
      Td = coef * self.d / v_s

    v_d = v_s + a_d * Td
    TD = coef * self.D / v_d
    return Ts + Td + TD

  def time_of_flight_bibliog(self, x_0, v_0):
    """Alternative evaluatation of time-of-flight of a particle of mass M=1
    and charge q=1 with initial velocity v_0 and position x_0 (from bibliography)."""
    q = 1.0                                 # WARNING: All have charge q=1.
    coef = 1.02  # *np.sqrt(2)

    U_0 = np.square(v_0) / 2.
    Us = U_0 + q * (self.s + x_0) * self.Es
    u = np.sqrt(Us + q * self.d * self.Ed)
    us = np.sqrt(Us)

    Ts = coef * (us - v_0) / (q * self.Es)
    Td = coef * (u - us) / (q * self.Ed)
    TD = coef * self.D / (2 * u)
    return Ts + Td + TD

  def data_to_array(self, unpack=False):
    """Conversion from signal to "numpy arrays", sorted by time

    Keyword Arguments:
    unpack -- (default False)
    """
    if self.times is not None:
      # especies ordenadas por masa (menores tiempos)
      ks = list(self.times.keys())
      ks.remove('time')
      ks.remove('signal')
      mint = np.argmax([self.times[k] for k in ks], axis=1)
      ks = [x for (y, x) in sorted(zip(mint, ks))]
      ks.insert(0, 'time')
      ks.append('signal')

      y = np.array([self.times[k] for k in ks])

      if unpack:
        return ks, y.T
      else:
        return ks, y
    return None, None

  def save_data(self, fname):
    """Save the signal to a data file"""
    if self.times is not None:
      ks, y = self.data_to_array()
      header = '  ' + '      '.join(ks)
      np.savetxt(fname, y.T, fmt='%.5e', header=header)

  def make_plot(self, especies=None, fname=None, **kvars):
    """Plot the signals in a "standard" form.

    Parameters
    ----------
    especies : dict
      masses to plot. If no present uses simulated fragments
    fname : string or None (default None)
      if not None -> Save the figure to "fname"
    kvars : Optional
      - negative = `True/False`             : if `True` -> Negative signal
      - show_grid = `True/False`             : if `True` -> Negative signal
      - graph_all=`True/False` (or show_all): if `True` -> Plot individual species
      - show_legend=`True/False`            : if `True` -> Show the legend
      - show_title=`True/False`            : if `True` -> Show info in the title

    """
    try:
      from matplotlib.pyplot import figure
    except BaseException:
      print("Plotting not available. Install matplotlib")
      return None

    if especies is None:
      especies = self.fragments
    negative = kvars.get('negative', False)
    show_grid = kvars.get('show_grid', False)
    show_title = kvars.get('show_title', False)
    graph_all = kvars.get('graph_all', kvars.get('show_all', False))
    if 'show_legend' in kvars:
      show_legend = kvars['show_legend']
    else:
      show_legend = not kvars.get('hide_legend', False)

    fig = figure(num='tof', figsize=(11, 7))
    fig.clf()
    ax = fig.add_subplot(111)
    if negative:
      signo = -1.
    else:
      signo = 1.

    Labels = []
    for k, p in sorted(list(especies.items()), key=lambda x: x[1]['M']):
      l = p.get('L', k)
      pico = self.times[k].argmax()

      Labels.append((l, pico))
      if graph_all:
        ax.plot(self.times['time'], signo * self.times[k], lw=4, label=l)

    y = signo * np.array(self.times['signal'])

    if show_legend and not graph_all:
      ax.plot(self.times['time'], y, '-ok', markersize=2)

      xlims = (max(self.times['time'].min(), 0),
               self.times['time'].max())
      Deltax = (xlims[1] - xlims[0]) / 20.
      ylims = ax.get_ylim()
      Deltay = (ylims[1] - ylims[0]) / 30.
      ax.set_ylim(ylims[0] - Deltay, ylims[1] + Deltay)
      ax.set_xlim(xlims[0] - Deltax, xlims[1] + Deltax)
      legbox = dict(facecolor='red', alpha=0.5, linewidth=2)
      dx = 1
      for l, p in Labels:
        xt = self.times['time'][p] + dx * Deltax
        yt = y[p] - Deltay
        ax.text(xt, yt, l,
                horizontalalignment='center', bbox=legbox, fontsize='large')
        dx = -dx
    else:
      ax.plot(self.times['time'], y, '-ok', markersize=2)

    ax.set_xlabel(r" $t(\mu s)$", fontsize="x-large")
    ax.set_ylabel(r"$\rho(t)$", fontsize='x-large')
    ncol = max((len(list(especies.keys())) - 2) // 6 + 1, 1)
    if show_legend:
      ax.legend(loc='best', title='$T={0}^{{\\circ}}K$'.format(
          self.Temperature), framealpha=0.5, ncol=ncol)

    if show_title:
      legtitle = 'TOF parameters\n'
      for k, val in self.get_tof_parameters().items():
        legtitle += r'${0}={1:.2f}$  '.format(k, val)
      ax.set_title(legtitle)

    ax.grid(visible=show_grid)
    if fname is not None:
      fig.savefig(fname, bbox_inches='tight')
    return fig


class Peaks(dict):
  """Simple object describing spectra peaks for the TOF.

  It is essentially a dictionary, with a few added convenience methods

  Each peak is described by a dictionary whose key is the label of the fragment.

  The values are:

    - 'index': tuple
         has the form (im, i0, ip) with the indexes of the peak (i0) and the two positions where the width is obtained.
    - 'position': float
         is value of the coordinate where the peak is located, in microseconds.
    - 'height': float
         is the value of the peak.
    - 'width': float
         is the width of the peak in microseconds.
  """

  def __init__(self):
    self.headers = ['index', 'position', 'height', 'width']

  def tolist(self):
    """Returns a list with the data describing the peaks. The form is:
    ['Substance', 'index', 'position', 'height', 'width']
    """
    peaks = [[k] + [v[h] for h in self.headers] for k, v in self.items()]
    return peaks

  def __str__(self):
    """Nicer printing of peak information
    """
    L = self.tolist()
    headers = ['Substance'] + self.headers
    try:
      from tabulate import tabulate
      return "\n" + tabulate(L, headers=headers, tablefmt='simple')
    except BaseException:
      s = " ".join([h.center(15) for h in headers])
      s += "\n" + " ".join([15 * "-" for h in header]) + "\n"
      for r in L:
        s1 = [str(c).center(15) for c in r[:2]]
        s1 += ["{:11.6f}".format(c).center(15) for c in r[2:]]
        s += " ".join(s1) + "\n"
      return s

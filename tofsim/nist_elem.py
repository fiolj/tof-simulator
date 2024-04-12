
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


import os
import re
import itertools
import collections as col
import numpy as np
from sys import stdout
from configparser import ConfigParser


try:
  datafile = os.path.join(
      os.path.dirname(
          os.path.realpath(__file__)),
      "nist_data.txt")
except BaseException:
  datafile = 'nist_data.txt'

if not os.path.exists(datafile):
  print("data file {} not found. Trying ...".format(datafile))
  datafile = os.path.join(os.getcwd(), "nist_data.txt")
if not os.path.exists(datafile):
  print("data file {} not found".format(datafile))

__NIST_ELEMENTS__ = {}


def _flatten(seq):
  """
  *Copied (and simplified for this use) from matplotlib.cbook*

  Return a generator of flattened nested containers.

  By: Composite of Holger Krekel and Luther Blissett
  From: https://code.activestate.com/recipes/121294/
  and Recipe 1.12 in cookbook
  """
  for item in seq:
    if (isinstance(item, str) or not np.iterable(item)) or item is None:
      yield item
    else:
      yield from _flatten(item)


def read_nist_data(threshold=0):
  """
  Read data from file *datafile* and fills the dictionary
  `__NIST_ELEMENTS__` with all the data

  Parameters
  ----------
  threshold: float
    Add all elements whose abundance is higher than threshold

  """
  global __NIST_ELEMENTS__
  __NIST_ELEMENTS__ = {}

  abbrev = ['Z', 'S', 'A', 'M', 'P', 'W']

  fi = open(datafile)
  end = False
  while not end:
    m = {}
    for f in abbrev:
      line = fi.readline()
      if line == '':
        end = True
        break
      v = line.split('=')[1].strip()
      if v == '':
        v = '0'
      m[f] = v

    if fi.readline().strip() != '':
      print('warning, should be empty')
    if end:
      break

    P = float(m['P'].split('(')[0])
    if P >= threshold:
      __NIST_ELEMENTS__[m['A'] + m['S']] = {
          'M': float(m['M'].split('(')[0]),
          'P': P,
          'S': m['S'],
          'A': int(m['A']),
          'Z': int(m['Z']),
          'L': make_label([(m['A'], m['S'], 0)], fmt='LaTeX'),
          'T': make_label([(m['A'], m['S'], 0)], fmt='LaTeXsimple')
      }
  fi.close()


def mass2conf(masses):
  """Format masses for a configuration file

  Parameters
  ----------
  masses: dict
    Information on substance(s)

  Returns
  -------
  str
    string with the format of a configuration file
  """
  s = ""
  for l, m in masses.items():
    s += f"[{l}]\n"
    for k, v in m.items():
      s += f"{k}={v}\n"
    s += '\n'
  return s


def loadmass(fname):
  """ Load masses from configuration file

  Parameters
  ----------
  fname: str or Path()
    File to read masses from

  Returns
  -------
  dict
    a dictionary with the elements read
  """
  parser = ConfigParser()
  parser.optionxform = str
  parser.read(fname)
  sections = parser.sections()
  m = {}
  for section_name in sections:
    m[section_name] = {}
    for name, value in parser.items(section_name):
      try:
        m[section_name][name] = float(value)
      except BaseException:
        m[section_name][name] = value
  return m


def make_label(ss, fmt='key'):
  """Construct the label for a given substance

  Parameters
  ----------
  ss: str
    Array of tuples [(A1,S1), (A2,S2), ...] for all atoms in the substance
  fmt: str
    Indicates the format of labels::

        'key'         -> "14N2"
        'Latex'       -> "$^{14}N_{2}$"
        'latexsimple' -> "$N_{2}$"
        'latexdoc'    -> r"\\ce{^{14}N_{2}}"
        'mass'        -> "28"

  """
  ss.sort(key=lambda x: x[0])
  items = list(col.Counter(ss).items())
  items.sort(key=lambda x: ss.index(x[0]))
  if fmt.lower() == 'latexdoc':
    label = r'\ce{'
    for k, v in items:
      if v == 1:
        label += r' ^{{{0}}}{1}'.format(k[0], k[1])
      else:
        label += r' ^{{{0}}}{1}{2}'.format(k[0], k[1], v)

    if k[2] == 1:
      label += '^{+}'
    elif k[2] > 1:
      label += '^{{{0}+}}'.format(k[2])
    label += '}'

  elif fmt.lower() == 'latex':
    label = r'$'
    for k, v in items:
      if v == 1:
        label += r'^{{{0}}}\mathrm{{{1}}}'.format(k[0], k[1])
      else:
        label += r'^{{{0}}}\mathrm{{{1}}}_{{{2}}}'.format(k[0], k[1], v)
    if k[2] == 1:
      label += '^{+}'
    elif k[2] > 1:
      label += '^{{{0}+}}'.format(k[2])
    label += '$'

  elif fmt.lower() == 'latexsimple':
    label = r'$'
    for k, v in items:
      if v == 1:
        label += r'\mathrm{{{0}}}'.format(k[1], v)
      else:
        label += r'\mathrm{{{0}}}_{{{1}}}'.format(k[1], v)
    if k[2] == 1:
      label += '^{+}'
    elif k[2] > 1:
      label += '^{{{0}+}}'.format(k[2])
    label += '$'

  elif fmt.lower() == 'mass':
    label = '{}'.format(np.sum([int(x[0]) for x in ss]))

  else:
    ll = []
    for k, v in items:
      if v == 1:
        ll.append('{0}{1}'.format(k[0], k[1]))
      else:
        ll.append('{0}{1}{2}'.format(k[0], k[1], v))

    label = '-'.join(ll)
    if k[2] == 1:
      label += r'^{+}'
    else:
      label += r'^{{{0}+}}'.format(k[2])

  return label


def _splitelement(subst):
  """Analiza una substancia y retorna los componentes y su multiplicidad como una lista de pares

  Parameters
  ----------
  subst: str
    Substance to analyze

  For instance for CHCO2
  gives:  [('C',2), ('H',1),('O',2)]
  """

  comp = list([_f for _f in re.split(r"([A-Z][a-z]*\d*)", subst) if _f])
  componentes = col.OrderedDict()
  for k in comp:
    elemx = list([_f for _f in re.split("([0-9]+)", k) if _f])
    if len(elemx) == 1:
      elem, X = elemx[0], 1
    else:
      elem = elemx[0]
      X = int(elemx[1])
    if elem in componentes:
      componentes[elem] += X
    else:
      componentes[elem] = X
  return list(componentes.items())


def _splitcharge(subst):
  """split element and charge
  """
  if '^' in subst:
    subst, q = subst.split('^')

    q = q.strip('{}')
    if len(q.strip('+')) < 1:
      carga = len(q)
    else:
      carga = int(q.strip('+'))
  else:
    carga = 1

  return subst.strip(), carga


def analyze_substance(subst, threshold=1.e-4, fragments=False, isotopes=True):
  """Devuelve todas las combinaciones con posibles isotopos (y su poblacion)
  de la sustancia con la formula dada.

  Parameters
  ----------
  subst: str
    substance to include (H2O, CO, SF6, N2, ...)
  threshold: float
    Minimum abundance that has to have an isotope in order to be included
  fragments: bool
    If True includes all fragments. For instance from 'CO' -> 'CO', 'C', 'O'
  isotopes: bool
    If True includes all isotope combinations


  Examples::

      analyze_substance('H2O').keys() =  ['1H1-2H1-16O1', '1H2-17O1', '1H2-16O1', '1H2-18O1']
      analyze_substance('CO').keys() =
             ['13C1-17O1', '13C1-18O1', '12C1-16O1', '12C1-18O1', '13C1-16O1', '12C1-17O1']
  """

  subst, carga = _splitcharge(subst)
  componentes = _splitelement(subst)

  elementos = {}
  multiplicidad = {}
  combinaciones = []
  for e, x in componentes:
    elem = _get_element(e)
    if not isotopes:                        # No analizamos composición isotópica
      # Isotopo de mayor población
      mayor = max(elem, key=lambda x: elem[x]['P'])
      elem = {mayor: elem[mayor]}

    m = list(elem.keys())
    elementos.update(elem)

    aa = list(itertools.combinations_with_replacement(m, r=x))
    combinaciones.append(aa)
    for k in aa:
      multiplicidad[k] = len(set(itertools.permutations(k)))

  sustancia = {}
  for k in itertools.product(*combinaciones):
    ll = [(elementos[s]['A'], elementos[s]['S'], carga) for s in _flatten(k)]
    label = make_label(ll)
    P = np.product(np.array([elementos[s]['P'] for s in _flatten(k)]))
    P *= np.product(np.array([multiplicidad[k[j]] for j in range(len(k))]))

    sustancia[label] = {'S': subst,
                        'M': np.sum(np.array([elementos[s]['M'] for s in _flatten(k)])),
                        'L': make_label(ll, fmt='LaTeX'),
                        'T': make_label(ll, fmt='LaTeXSimple'),
                        'P': P,
                        'A': np.sum(np.array([int(elementos[s]['A']) for s in _flatten(k)])),
                        'Z': np.sum(np.array([int(elementos[s]['Z']) for s in _flatten(k)])),
                        'q': carga
                        }
  for k, v in list(sustancia.items())[:]:
    if v['P'] < threshold:
      sustancia.pop(k)
    else:
      v['P'] *= 100.
  return sustancia


def _get_element(*elems):
  """Devuelve uno o varios elementos (con todos sus isotopos)
  en la forma adecuada para el TOF
  Keyword Arguments:
  elems -- Elemento o elementos a devolver: por ejemplo H, Kr, N, Ne, ...
  """
  global __NIST_ELEMENTS__
  if __NIST_ELEMENTS__ == {}:
    read_nist_data()

  sp = {}
  for elem in elems:
    for k, v in list(__NIST_ELEMENTS__.items()):
      if v['S'] == elem:             # IMPORTANTE:
        # sin copy() hace una referencia a __NIST_ELEMENTS[k]
        sp[k] = v.copy()
  return sp


def format_listmass(rows, end='\n', sep=' ', header='', footer=''):
  """Simple formatting of a list of substances. It is intended to use with the
  output of `get_lista()`

  Parameters
  ----------
  rows: list
    List where each row is a list with data on a single element
  end: str
    End of line string
  sep: str
    string used as separator within a line
  header: str
    Header to add before the data
  footer: str
    Footer to add after the data

  """

  s = header + '\n'

  rows.sort(key=lambda x: x[1])
  for r in rows:
    for c in r:
      s += "{}{}".format(c, sep)
    s = s[:-len(sep)] + end
  s += footer
  return s


class Sustancias(dict):
  """Object describing a list of substances.

  Examples:

      >>> elementos = ['N2', 'H2O', 'Ar^{3+}', 'Ar^{+}', 'Ar^2+', 'UF6']
      >>> m = Sustancias(elementos, threshold=1.e-3)
      >>> print(m)
      l                     M          P
      -------------  --------  ---------
      1H2-16O^{+}     18.0106  99.7341
      1H2-18O^{+}     20.0148   0.204953
      14N2^{+}        28.0061  99.2733
      14N-15N^{+}     29.0032   0.72535
      36Ar^{3+}       35.9675   0.3365
      36Ar^{+}        35.9675   0.3365
      36Ar^{2+}       35.9675   0.3365
      40Ar^{3+}       39.9624  99.6003
      40Ar^{+}        39.9624  99.6003
      40Ar^{2+}       39.9624  99.6003
      19F6-235U^{+}  349.034    0.7204
      19F6-238U^{+}  352.041   99.2742

  To get help use:

      >>> m.show_help()
      Create an object Sustancias as:
      #
        Sustancias(<elemento o sustancia>)
      #
      Fields in mass have the meaning:
      #
       Z:  str  Atomic Number
       S:  str  Atomic Symbol
       A:  str  Mass Number
       M:  str  Relative Atomic Mass
       P:  str  Isotopic Composition
       W:  str  Standard Atomic Weight
       q:  str  Charge

  """

  _columns = 'ALMPSZ'

  _fields = [('Z', 'Atomic Number'), ('S', 'Atomic Symbol'),
             ('A', 'Mass Number'),
             ('M', 'Relative Atomic Mass'),
             ('P', 'Isotopic Composition'),
             ('W', 'Standard Atomic Weight'),
             ('q', 'Charge')
             ]

  def __init__(self, elementos='', threshold=1.e-4, isotopes=True):
    """Initialize a `Sustancias` instance

    Parameters
    ----------
    self: type
      description
    elementos: str
      A string defining one or more substances
    threshold: float
      Threshold abundace for adding a given isotope
    isotopes: bool
      If `True` include all isotopes, otherwise only the most abundant.

    """
    self.thr = threshold
    self.iso = isotopes
    self.ListItems = []
    self._sortorder = 'M'
    self.add(elementos)

  def copy(self):
    """Copy the object and returns a new one."""
    p = Sustancias()
    p.thr = self.thr
    p.iso = self.iso
    p.ListItems = self.ListItems
    p._sortorder = self._sortorder
    p.update(self)
    return p

  def show_help(self):
    """Show help on use of Object Sustancias    """
    s = """Create an object Sustancias as:

  Sustancias(<elemento o sustancia>)


  Fields in mass have the meaning:

    """
    # s += (32) * '=' + '\n'
    for k, v in self._fields:
      s += '  {0}:  str  {1}\n'.format(k, v)
    print(s)

  def add(self, sustancias):
    """Returns a dictionary with all the information on the substances added.

    Parameters
    ----------
    sustancias: str
      Comma separated list of substances to be added, por instance:

          m = add('H20,O2,N2,UF5,UF6')

    """
    m = {}
    if isinstance(sustancias, str):
      elems = sustancias.split(',')
    else:
      elems = sustancias

    for e in elems:
      if e != '':
        m.update(
            analyze_substance(
                e.strip(),
                threshold=self.thr,
                isotopes=self.iso))
    self.update(m)
    self.ListItems.extend(list(m.keys()))
    self.sort()

  def remove(self, sustancias, criteria='fragment'):
    """Remove a fragment

    Parameters
    ----------
    sustancias: str or list of strings
      substance or fragment to remove
    criteria: str
      either 'fragment' (the default value) or 'substance':


    For the choices of 'criteria', we use:

    - 'fragment': e.g:  Ar^{2+}, SF6^++,  Removes exactly the fragment given
    - 'substance': e.g:  Ar, SF6, Xe, Remove all fragments with independently of the charge
    """

    if criteria == 'key':
      for_removal = sustancias
    else:
      if isinstance(sustancias, str):
        elems = sustancias.split(',')
      else:
        elems = sustancias
      for e in elems:
        for_removal = []

        if e.strip() != '':
          ee, q = _splitcharge(e)
          for k in self:          # Listamos los que vamos a remover
            if criteria == 'substance':
              remover = (ee == self[k]['S'])
            else:
              remover = (ee == self[k]['S'] and q == self[k]['q'])
            if remover:
              for_removal.append(k)

    for k in for_removal:  # Ahora lo removemos
      self.ListItems.remove(k)
      self.pop(k)

  def list(self, key=None):
    """Return a list of elements, optionally filtered with a criteria given by key

    Parameters
    ----------
    key: None or function
      - if key=None returns all elements
      - otherwise key has to be a function returning `True` or `False`.


    Examples:

         >>> list(key = lambda x:  x['P'] > 0.40)  # returns True if population greater than 40%
         >>> list(key = lambda x:  x['M'] > 50)    # returns True if Mass smaller than than 50 AMU
         >>> list(key = lambda x:  x['q'] > 2)     # returns True if charge greater than 2

    """
    if key is None:
      return self.ListItems
    return [k for k in self.ListItems if key(self[k])]

  def sort(self, order=None, reverse=False):
    """Sort the substances according to the specified order.
    The sort is stable.

    Parameters
    ----------
    self: type
      description
    order: str
      desired order. One of 'ALMPSZq'
    reverse: bool
      If `True` will be reversed

    """
    if order is None:
      order = self._sortorder
    else:
      self._sortorder = order
    if order not in self._columns + 'q':
      print('Sort order must be one of {}'.format(self._columns + 'q'))
      return

    lista = [(k, self[k]) for k in self.ListItems]  # Get in order
    lista.sort(key=lambda x: x[1][order], reverse=reverse)
    self.ListItems = [ll[0] for ll in lista]

  def saveconf(self, fname=None):
    """Save the substances to a file in a format that may be later read

    Parameters
    ----------
    self: type
      description
    fname: None or str or pathlib.Path()
      Name of the file. If `None` prints to screen

    """
    s = mass2conf(self)
    if fname is not None:
      with open(fname, 'w') as fo:
        fo.write(s)
    else:
      stdout.write(s)

  def loadconf(self, fname):
    """Load substances from file

    Parameters
    ----------
    fname: str or Path() object
      File with definition of substances to add


    File should have configuration format as::

        [34S1]
        S=S
        L=$^{34}\\mathrm{S}$
        P=4.25
        M=33.9678669
        A=34
        Z=16

        [32S1]
        S=S
        L=$^{32}\\mathrm{S}$
        P=94.99
        M=31.972071
        A=32
        Z=16

    """
    m = loadmass(fname)
    self.update(m)
    self.ListItems.extend(m.keys())
    self.sort()

  def get_lista(self, cols=None):
    """Return a list with the cols

    Parameters
    ----------
    cols: tuple/list or None
      A list of string selecting the fields to included, chosen from `"A,L,l,M,P,S,Z"`
    """

    lista = []
    if cols is None:
      columnas = self._columns
    else:
      columnas = cols

    for k in self.ListItems:
      a = []
      for x in columnas:
        if x == 'l':
          a.append(k)
        elif x in self[k]:
          a.append(self[k][x])
      lista.append(a)
    return lista

  def __str__(self):
    return self.to_table(cols=['l', 'M', 'P'],
                         tablefmt='simple').replace('\n', '\n  ')

  def to_text(self):
    """Convenience function to format as a simple table
    """
    cols = ['S', 'l', 'M', 'P']
    headers = u'Substance Formula Mass Abundance'.split()
    return self.to_table(cols=cols, headers=headers, tablefmt='fancy_grid')

  def to_table(self, cols=None, headers=(), tablefmt='simple', floatfmt='g',
               numalign='decimal', stralign='left', missingval=''):
    """Format the list of sustances in Table format.

    This is a wrapper around the tabulate function
    from the tabulate package: https://pypi.python.org/pypi/tabulate.
    Available formats are:
    fancy_grid, grid, plain, psql, rst, simple, tsv
    latex, latex_raw, latex_booktabs, mediawiki, orgtbl, pipe,
    html

    Options `tablefmt`, `floatfmt`, `numalign`, `stralign`, `missingval` are passed to package `tabulate`, if available.

    Parameters
    ----------
    cols: list
      A list of strings with the characteristics to include. Must be in ALMPSZ
    headers: str
      String to include before data
    tablefmt: str
      Format of table
    floatfmt: str
      Format used to write numbers
    numalign: str
      Alignment for numbers
    stralign: str
      Alignment for strings
    missingval: str
      Value to write when values are missing

    """
    if headers == ():
      if cols is None:
        headers = self._columns
      else:
        headers = cols
    l = self.get_lista(cols)
    try:
      from tabulate import tabulate
    except BaseException:
      print('Output tables depend on package tabulate.')
      print("Install it from: https://pypi.python.org/pypi/tabulate")
      s = format_listmass(l, header=' '.join(headers))
      return s

    return '\n' + tabulate(l, headers, tablefmt, floatfmt,
                           numalign, stralign, missingval)

  def to_latex(self, cols=None, headers=None, standalone=False):
    """Convert to LaTeX table using tabulate package

    Parameters
    ----------
    cols: list
      Substance characteristics to include.
    headers: str
      String to write before data.
    standalone: bool
      If `True` make a standalone document that may be compiled by LaTeX.

    """
    if standalone:
      if len(self) < 32:
        fontsize = r'\large'
      else:
        fontsize = ''
      head = r"""\documentclass[a4paper,12pt]{article}
\usepackage[version=4]{mhchem}
\usepackage[table]{xcolor}
\usepackage[top=1cm, bottom=1.5cm]{geometry}

\begin{document}
\setlength{\tabcolsep}{10pt}
\renewcommand{\arraystretch}{1.3}
\thispagestyle{empty}

\rowcolors{1}{black!20}{white}
""" + "{}\n".format(fontsize)
      foot = r"""
\end{document}
"""
    else:
      head = ""
      foot = ""

    formato = 'latex_raw'
    if cols is None:
      cols = ['L', 'M', 'P']
    if headers is None:
      headers = cols
    return head + self.to_table(cols=cols,
                                headers=headers, tablefmt=formato) + foot

  def to_pdf(self, cols=None, headers=None,
             latexcommand='pdflatex', output='tmp.pdf'):
    """Convert to pdf format using latex.

    Export to a latex file and compiles it.

    Parameters
    ----------
    self: type
      description
    cols: str
      Substance characteristics to include
    headers: str
      Description to include before data
    latexcommand: str
      command to compile to pdf
    output: str
      Name of the output file

    """
    import subprocess as sub
    tt = os.path.splitext(output)[0] + '.tex'
    with open(tt, mode='w') as texfile:
      # with tempfile.NamedTemporaryFile(mode='w', suffix='.tex') as texfile:
      s = self.to_latex(cols=cols, headers=headers, standalone=True)

      texfile.write(s)
      texfile.close()
      cmd = latexcommand + " " + texfile.name
      ret = sub.call(cmd, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
      ret = sub.call(cmd, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)

      try:                      # Clean-up intermediate files
        sub.call(
            'latexmk -c ' +
            texfile.name,
            shell=True,
            stdout=sub.PIPE,
            stderr=sub.PIPE)
      finally:
        pass
    return ret

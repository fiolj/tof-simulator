#! /usr/bin/ipython
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from get_elements import Sustancias


def sqrtmass(f):
  "sqrt(masas/cargas) para todos los fragmentos en f"
  return np.sqrt([f[k]['M'] / f[k]['q'] for k in f.ListItems])


if __name__ == '__main__':
  plt.ion()

  ######################################################################
  # Ingresar los datos correspondientes
  sust = 'U^+,U^{++},UF^{+},UF2^{+},UF3^{+}'
  datos = {  # fragmentos : tiempos en microsegundos
      '238U^{+}': 19.753,
      '238U^{2+}': 13.966,
      '19F-238U^{+}': 20.528,
      '19F2-238U^{+}': 21.273,
      '19F3-238U^{+}': 21.991,
  }

  # Queremos los tiempos para estas sustancias
  particulas = sust + ',H2O^{+},N2^{+}, Ar^{+},UF5^{+}, UF4^{+},UF3^{+},UF2^{+},UF^{+}'

  ######################################################################
  #
  f = Sustancias(sust)
  f.sort(order='q', reverse=True)
  # Estas líneas elijen los isótopos conteniendo el 235
  # l = f.list(lambda x: x['P'] < 5)
  # l = f.list(lambda x: x['M'] < 236)
  # l = f.list(lambda x: x['A'] == 235)
  l = f.list(lambda x: '235' in x['L'])

  # Quitamos los isótopos
  f.remove(l, criteria='key')

  # seteamos x,y
  m = sqrtmass(f)  # sqrt(masas/cargas)
  t = np.array([datos[x] for x in f.list()])                 # tiempos

  p = np.polyfit(m, t, 1)       # Fiteo lineal

  fragmentos = Sustancias(particulas)
  fragmentos.sort('q', reverse=True)
  fragmentos.sort('M', reverse=True)
  x = sqrtmass(fragmentos)
  y = np.polyval(p, x)
  r = np.c_[x, y].T

  # print(fragmentos.list())
  pp = np.polyfit(t, m, 1)
  xx = np.linspace(1, 24, 38)
  yy = np.polyval(pp, xx)

  r.sort()
  x, y = r

  # Sacamos la tabla
  for i, k in enumerate(fragmentos.list()):
    fragmentos[k]['t'] = y[i]
  fragmentos.sort('t')

  # print(fragmentos.to_table(cols='Alqt', tablefmt='fancy_grid'))
  # print(fragmentos.to_table(cols='Alqt', tablefmt='latex_booktabs'))
  # headers = ['Fragmento', 'Masa', 'Abundancia (\%)', 'Tiempo ($\mu$s)']
  # fragmentos.to_pdf(cols='LAPt', headers=headers)
  with plt.style.context('presentation'):
    # Plotting
    plt.figure(num=1)
    plt.clf()
    r = np.r_[x, y]
    plt.plot(xx**2, np.polyval(p, xx), '--b', label="$P(x)=({0:.4f} x  {1:+.4f})^2$".format(*p))
    plt.plot(xx**2, np.polyval([p[0], 0], xx), '--g',
             label="$P(x)=({0:.4f} x)^2$".format(p[0]))
    plt.plot(x**2, y, 'or', label="Interpolación")
    plt.plot(m**2, t, 'ok', label='datos')

    plt.xlabel(r"$m/q$")  # labels again
    plt.ylabel(r"$\mathrm{Tiempos}$ $\mathrm{(\mu s)}$")
    plt.legend(loc='best')

  plt.figure(num=2)
  plt.clf()
  plt.plot(x, y, '-or', label="$P(x)={0:.4f} x  {1:+.4f}$".format(*p))
  plt.plot(yy, xx, '--b', label="$P(x)={0:.4f} x  {1:+.4f}$".format(*pp))

  plt.plot(m, t, 'ok', label='datos')

  plt.xlabel(r"$\sqrt{m/q}$")  # labels again
  plt.ylabel(r"Tiempos ($\mu{}$s)")
  plt.legend(loc='best')

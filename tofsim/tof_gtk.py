#!/usr/bin/python3
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

from .nist_elem import analyze_substance
from .tof import ToF
from .version import VERSION, COPYRIGHT
import subprocess as sub
from pathlib import Path

import sys
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')
# from matplotlib.widgets import Cursor


# default_conffile = os.path.join(os.path.dirname(__file__), 'tof.conf')
default_conffile = Path(__file__).resolve().parent / 'tof.conf'


class tof_gtk:
  Npoints_fast = 100000

  def __init__(self, conffile=None):

    # use GtkBuilder to build our interface from the XML file
    try:
      builder = Gtk.Builder()
      fnint = "tof_gtk.ui"
      interface = str(Path(__file__).resolve().parent / fnint)
      builder.add_from_file(interface)
    except BaseException as error:
      self._message(f"{error}.\n\n Failed to load UI XML file: {fnint}")
      sys.exit(1)

    if conffile is None:
      conffile = default_conffile
    self.masses = self.init_calc(conffile)
    self.init_gui(builder)
    self.init_graph()
    self.line = None

    # connect signals
    builder.connect_signals(self)
    self.mw.set_default_size(1000, 600)
    # self.Npoints = self.tof.Npoints       # Usado para guardar el valor seteado por user

  def _message(self, message):
    # log to terminal window
    print(message)

  # Create the tof object
  def init_calc(self, conffile=None):
    self.tof = ToF()
    return self.tof.load_conf_file(conffile)

  def init_gui(self, builder):
    # get the widgets which will be referenced in callbacks
    self.mw = builder.get_object('w1')   # Main window
    self.sw1 = builder.get_object('sw1')   # subwindow with plot
    self.sw2 = builder.get_object('sw2')   # subwindow with toolbar
    self.tv = builder.get_object('treeview1')
    self.lm = builder.get_object('listmass')   # List of Masses

    self.addmass = builder.get_object('addmasas')
    self.enmass = builder.get_object('enmass')

    self.swupd = builder.get_object('swfast')   # Auto-update
    self.isotop = builder.get_object('chiso')   # Get isotopes

    self.popup_menu = builder.get_object('tvmenu')
    self.cbaddrow = builder.get_object('cbaddrow')
    # Preferences window
    self.preferences_dialog = builder.get_object('dialog_pref')
    self.sbs = builder.get_object('sb_s')
    self.sbd = builder.get_object('sb_d')
    self.sbD = builder.get_object('sb_D')
    self.sbLt = builder.get_object('sbLt')
    self.cmLt = builder.get_object('comboLt')
    self.sbLr = builder.get_object('sbLr')
    self.cmLr = builder.get_object('comboLr')
    self.enNp = builder.get_object('enNpoints')
    self.entp = builder.get_object('entimeprec')
    self.chneg = builder.get_object('chneg')
    self.chgrd = builder.get_object('chgrd')
    self.threshold_isotope = builder.get_object('thsubst')

    self.sbEs = builder.get_object('sbEs1')   # Potencial Vs
    self.sbEd = builder.get_object('sbEd1')   # Potencial Vd
    self.sbT = builder.get_object('sbT')      # Temperature

    self.update_display_tof()

    # Initialize the masses with default values
    if self.masses is None:
      self.masses = {
          '235UF6': {'M': 349, 'P': 0.03, 'tex': r"$^{{235}}UF_{{6}}$"},
          '238UF6': {'M': 352, 'P': 0.37, 'tex': r"$^{{238}}UF_{{6}}$"},
          '235UF5': {'M': 328, 'P': 0.07, 'tex': r"$^{{235}}UF_{{5}}$"},
          '238UF5': {'M': 333, 'P': 0.53, 'tex': r"$^{{238}}UF_{{5}}$"},
      }
    self.update_display_mass()

  def update_display_tof(self):
    # Initialize the values in the gui
    self.sbEs.set_value(self.tof.Vs)
    self.sbEd.set_value(self.tof.Vd)
    self.sbT.set_value(self.tof.Temperature)
    self.sbs.set_value(self.tof.s)
    self.sbd.set_value(self.tof.d)
    self.sbD.set_value(self.tof.D)
    self.sbLt.set_value(self.tof.dt * 1.e3)
    self.sbLr.set_value(self.tof.ds * 10)
    self.enNp.set_text(str(self.tof.Npoints * 1.e-6))
    self.entp.set_text(str(self.tof.timeprec * 1.e3))
    if self.tof.tdist.lower() == 'normal':
      self.cmLt.set_active(0)
    else:
      self.cmLt.set_active(1)
    if self.tof.posdist.lower() == 'normal':
      self.cmLr.set_active(0)
    else:
      self.cmLr.set_active(1)

  def update_display_mass(self):
    self.lm.clear()
    for k, v in self.masses.items():
      # if v.has_key('L'): key= v['L']
      # else:             key=k
      self.lm.append([k, v['M'], v['P']])

  # def onclick(self, event):
  #   print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
  #     event.button, event.x, event.y, event.xdata, event.ydata)
  #   x= [event.xdata,event.xdata]
  #   y= self.ax.get_ylim()
  #   if self.line == None:
  #     self.line, = self.ax.plot(x,y,'r',lw=2)
  #   else:
  #     self.line.set_xdata(x)
  #     self.line.set_ydata(y)
  #   #We need to draw
  #   self.canvas.draw()

  # Create the graph and add to the window
  def init_graph(self):
    self.fig = Figure(figsize=(5, 5), dpi=100)
    self.ax = self.fig.add_subplot(111)

    self.canvas = FigureCanvas(self.fig)
    self.canvas.set_size_request(400, 400)
    self.sw1.add_with_viewport(self.canvas)

    toolbar = NavigationToolbar(self.canvas)
    self.sw2.add_with_viewport(toolbar)

  def graph(self):
    species, X = self.tof.data_to_array()
    if self.chneg.get_active():
      X[1:] *= -1
    self.ax.cla()

    if species is not None:
      # for i,k in enumerate(sorted(species[1:-1], key= lambda x: self.masses[x]['M'])):
      for i, k in enumerate(species[1:-1]):
        lab = self.masses[k].get('L', k)
        self.ax.plot(X[0, :], X[i + 1, :], lw=3, label=lab)
      self.ax.plot(X[0, :], X[-1, :], 'o-k', ms=2, lw=1)

      ymin, ymax = X[-1, :].min(), X[-1, :].max()
      self.ax.set_ylim((ymin * 1.05, 1.05 * ymax))
      self.ax.set_xlabel(r" $t(\mu s)$", fontsize="x-large")
      self.ax.set_ylabel(r"$\rho(t)$", fontsize='x-large')
      ncol = (len(species) - 2) // 8 + 1
      self.ax.legend(title=r'$T={0}^{{\circ}}K$'.format(self.tof.Temperature),
                     loc='best', fontsize='small', framealpha=0.5, ncol=ncol)

      leyenda = u'Parámetros del TOF\n'
      for k in ['s', 'd', 'D', 'Vs', 'Vd']:
        leyenda += r'${0}={1}$  '.format(k, self.tof.__dict__[k])
      self.ax.set_title(leyenda)

    if self.chgrd.get_active():
      self.ax.grid(True)
    else:
      self.ax.grid(False)
    self.canvas.draw()

  def on_addmasas_clicked(self, widget):
    subst = self.enmass.get_text().split(',')
    thr = float(self.threshold_isotope.get_text()) * 1.e-2
    isotopes = self.isotop.get_active()
    for s in subst:
      self.masses.update(analyze_substance(s.strip(), threshold=thr, isotopes=isotopes))

    self.update_display_mass()
    self.enmass.set_text('')

  def on_swupd_activate(self, switch):
    pass
    # if switch.get_active():      self.tof.Npoints = 100000
    # else:                        self.tof.Npoints = self.Npoints

  def on_sbEd1_value_changed(self, spinbutton):
    if self.swupd.get_active():
      self.update_plot()
    # if self.swupd.get_active():
    #   self.update_plot()

  def on_sbEs1_value_changed(self, spinbutton):
    if self.swupd.get_active():
      self.update_plot()

  def on_about_activate(self, menuitem):
    authors = ["Juan Fiol - para LASIE"]
    ad = Gtk.AboutDialog()
    ad.set_transient_for(self.mw)
    ad.set_destroy_with_parent(True)
    ad.set_program_name(u"Simulación de TOF - Version {}".format(VERSION))
    ad.set_copyright("Copyright 2020 Juan Fiol\n" + COPYRIGHT)
    ad.set_comments(u"Time-of-flight mass spectrometer simulator")
    ad.set_authors(authors)
    ad.set_logo_icon_name(Gtk.STOCK_EXECUTE)
    # callbacks for destroying the dialog

    def close(dialog, response, editor):
      dialog.destroy()

    def delete_event(dialog, event, editor):
      return True
    ad.connect("response", close, self)
    ad.connect("delete-event", delete_event, self)
    ad.show()

  def on_teoria_activate(self, menuitem):
    """Open the pdf file.
    TODO: Change to html documentation, possibly online
    """
    pdfteoria = Path(__file__).resolve().parent / 'tof_teoria.pdf'
    viewers = ['evince', 'okular', 'acrobat']
    for v in viewers:
      status = sub.call([v, pdfteoria])
      if status == 0:
        return 0

  # Save configuration (File -> Save)
  def on_save_activate(self, menuitem):
    fcd = Gtk.FileChooserDialog("Save Configuration...", None,
                                Gtk.FileChooserAction.SAVE,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    response = fcd.run()
    if response == Gtk.ResponseType.OK:
      self.tof.save_conf_file(fcd.get_filename(), self.masses)
    fcd.destroy()

  # Export data
  def on_export_activate(self, menuitem):
    fcd = Gtk.FileChooserDialog("Export data...", None,
                                Gtk.FileChooserAction.SAVE,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    response = fcd.run()
    if response == Gtk.ResponseType.OK:
      self.tof.save_data((fcd.get_filename()))
    fcd.destroy()

  # Load configuration (File -> Open)
  def on_open_activate(self, data=None):
    fcd = Gtk.FileChooserDialog("Open Configuration...",
                                None,
                                Gtk.FileChooserAction.OPEN,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    response = fcd.run()
    if response == Gtk.ResponseType.OK:
      self.load_conf_file(fcd.get_filename())
    fcd.destroy()

  def load_conf_file(self, fname):
    m = self.tof.load_conf_file(fname)
    if m is not None:
      self.masses = m
      self.update_display_mass()
    self.update_display_tof()

  # When the main window is destroyed, we want to break out of the GTK main loop.
  def on_w1_destroy(self, widget, data=None):
    self._message('Exterminate!')
    Gtk.main_quit()

  # Called when the user clicks the 'Quit' menu.
  def on_mquit_activate(self, menuitem):
    self.on_w1_destroy(menuitem)

  # Edicion de Especie, Masa y Poblacion ################
  def on_cellEsp_edited(self, widget, path, text):
    self.lm[path][0] = text

  def on_spMass_edited(self, widget, path, text):
    self.lm[path][1] = float(text.replace(',', '.'))

  def on_spPob_edited(self, widget, path, text):
    self.lm[path][2] = float(text.replace(',', '.'))

  def on_treeview1_button_press_event(self, tv, event):
    if event.button == 3:
      time = event.time
      self.popup_menu.popup(None, None, None, None, event.button, time)

  def on_addrow_activate(self, menuitem):
    self.add_rows(1, -1)

  def on_butAdd_clicked(self, menuitem):
    nrows = int(self.cbaddrow.get_active_text().split()[0])
    self.add_rows(nrows, -1)

  def add_rows(self, nrows, position):
    for n in range(nrows):
      self.lm.insert(position)

  def on_butDel_clicked(self, menuitem):
    self.delete_selected_masses()

  def delete_selected_masses(self):
    selection = self.tv.get_selection()
    if selection is not None:
      model, pathlist = selection.get_selected_rows()
      for path in reversed(pathlist):
        tree_iter = model.get_iter(path)
        self.masses.pop(self.lm.get_value(tree_iter, 0))
        self.lm.remove(tree_iter)
      self.update_masas()

# #######################################################################

  # Setup del TOF
  def on_butTOFset_clicked(self, menuitem, data=None):
    self.preferences_dialog.present()

  def on_butPrefOK_clicked(self, widget):
    self.update_tof_param()

  def on_dialog_pref_delete_event(self, widget, data):
    # self.preferences_dialog.hide()
    return True

  def update_tof_param(self):
    self.tof.Temperature = self.sbT.get_value()
    self.tof.Vs = self.sbEs.get_value()
    self.tof.Vd = self.sbEd.get_value()

    self.tof.s = self.sbs.get_value()
    self.tof.d = self.sbd.get_value()
    self.tof.D = self.sbD.get_value()

    self.tof.ds = self.sbLr.get_value() * 0.1
    self.tof.dt = self.sbLt.get_value() * 1.e-3

    if self.swupd.get_active():
      self.tof.Npoints = self.Npoints_fast
    else:
      self.tof.Npoints = int(float(self.enNp.get_text()) * 1000000)

    self.tof.timeprec = float(self.entp.get_text()) * 1.e-3

    self.tof.tdist = self.cmLt.get_active_text()
    self.tof.posdist = self.cmLr.get_active_text()

  def on_butPrefClose_clicked(self, widget):
    self.preferences_dialog.hide()

  def on_chgrd_toggled(self, widget):
    self.graph()

  def on_chneg_toggled(self, widget):
    self.graph()
# #######################################################################

  # Calculations
  def calculate(self, particles):
    return self.tof.signal(particles)

  def update_plot(self):
    self.update_tof_param()
    self.update_masas()
    self.times = self.calculate(self.masses)
    self.graph()

  def on_butCalc_clicked(self, widget):
    self.update_plot()

  def update_masas(self):
    m = {}
    for label, Mass, Pobl in self.lm:
      if label.strip() != '':
        if label in self.masses:
          LL = self.masses[label].get('L', label)
        else:
          LL = label

        m[label] = {'M': Mass, 'P': Pobl, 'L': LL}
    if m != {}:
      self.masses = m              # Update all parameters

# #######################################################################

  # Run main application window
  def main(self):
    self.mw.show_all()
    Gtk.main()


if __name__ == "__main__":
  import argparse
  # from version import VERSION
  default_conffile = Path(__file__).resolve().parent / 'tof.conf'
  parser = argparse.ArgumentParser(
      description=u'"Simulación de la señal obtenida en el tiempo de vuelo"')

  parser.add_argument('-V', '--version', action='version',
                      version='%(prog)s version {}'.format(VERSION))
  parser.add_argument(
      "-c",
      "--conf",
      default=default_conffile,
      metavar='File',
      help="Configuration file to load")

  args = parser.parse_args()

  TOF_w1 = tof_gtk(args.conf)
  TOF_w1.main()

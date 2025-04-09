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

# from tof.nist_elem import analyze_substance
from matplotlib.figure import Figure
from tofsim.tof import ToF, _conffile
from tofsim.version import __version__, COPYRIGHT
# from tofsim.tof import ToF
import subprocess as sub
from pathlib import Path

import pandas as pd
import streamlit as st

import matplotlib as mpl
mpl.use("agg")

#############################################################################
# Workaround for the limited multi-threading support in matplotlib.
# Per the docs, we will avoid using `matplotlib.pyplot` for figures:
# https://matplotlib.org/3.3.2/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server.
# Moreover, we will guard all operations on the figure instances by the
# class-level lock in the Agg backend.
#############################################################################
# from matplotlib.backends.backend_agg import RendererAgg
# _lock = RendererAgg.lock


# -- Set page config
apptitle = 'TOF Simulator'
st.set_page_config(page_title=apptitle, page_icon='random',
                   layout='centered'  # alternativa 'wide'
                   )

# Title the app
st.title('Time of Flight Simulator')

# st.markdown("""
#  * Use the menu at left to select data and set plot parameters
# """)

if "show_grid" not in st.session_state:
  st.session_state.show_grid = False
if "negative_signal" not in st.session_state:
  st.session_state.negative_signal = False

show_grid = False
negative = False


@st.cache_resource
def create_ToF(conffile=None):
  T = ToF()
  T.fragments.thr = 0.015
  if conffile is not None:
    T.load_conf_file(conffile)
  return T


def delete_selected_masses(frags, rows):
  to_del = [masses[m][0] for m in rows]
  for f in to_del:
    frags.remove(f, criteria='key')


def update_plot(Tof, show_grid=False, negative=False, **props):
  Tof.signal()
  propiedades = {'graph_all': True, 'show_grid': show_grid, 'negative': negative}
  propiedades.update(props)
  fig = Tof.make_plot(**propiedades)
  return fig


def get_parameters(T):
  with st.expander("## TOF Parameters"):
    T.s = st.number_input('Distance Extraction (cm)', 0.1, 10.0, T.s, 0.1)  # min, max, default
    T.d = st.number_input('Distance Acceleration (cm)', 0.1, 10.0, T.d, 0.1)  # min, max, default
    T.D = st.number_input('Vuelo libre (cm)', 10.0, 200.0, T.D, 1.)  # min, max, default
    T.Vs = st.number_input('Voltage Extraction (V)', 10.0, 1000.0, float(T.Vs), 10.)  # min, max, default
    T.Vd = st.number_input('Voltage Acceleration (V)', 10.0, 10000.0, float(T.Vd), 10.)  # min, max, default

  with st.expander('## Conditions'):
    T.Temperature = st.number_input('Atoms Temperature (K)', 10.0, 2000.0, float(T.Temperature), 10.)  # min, max, default
    T.dt = 1.e-3*st.number_input('Pulse duration (ns)', 1., 500.0, 1.e3*T.dt, 0.1)  # min, max, default
    T.tdist = st.selectbox("Time distribution", ("normal", "uniform"))
    T.ds = 1.e-1*st.number_input('Spot radius (mm)', 0.05, 10.0, 1.e1*T.ds, 0.1)  # min, max, default
    T.posdist = st.selectbox("Spatial distribution", ("normal", "uniform"))


# Create TOF and masses
T = create_ToF()
frags = T.fragments

if "in_mass" not in st.session_state:
  st.session_state.in_mass = ""


def submit():
  st.session_state.in_mass = st.session_state.new_mass
  st.session_state.new_mass = ""


with st.sidebar:
  get_parameters(T)

  # with st.expander("Add Substances"):
  st.subheader("Add Substances", divider=True)
  frags.thr = st.slider('Isotope threshold', 0., 100., 1.5, 0.1,
                        help="Minimum percentage of population of an isotope that will be included")
  frags.thr /= 100.
  st.text_input("Add Substances", value="", max_chars=None, help="Add comma-separated substances. Eg:Al,Yb,CO2", key="new_mass", on_change=submit)

  with st.expander("Select Calculation Properties"):
    T.Npoints = int(1.e6*st.number_input('Nº of particles ($10^6$)', 0.1, 5.0, T.Npoints*1.e-6, 0.1))  # min, max, default, step
    T.timeprec = 1.e-3*st.number_input('Time precision (ns)', 0.1, 5.0, 1.e3*T.timeprec, 0.1)  # min, max, default
    st.session_state.show_grid = st.checkbox("Show Grid")
    st.session_state.negative_signal = st.checkbox("Negative Signal")

# Clear the mass input text and add the masses
ms = st.session_state.in_mass
st.session_state.in_mass = ""
frags.add(ms)


masses = frags.get_lista(cols=['l', 'M', 'P'])
masas = st.data_editor(masses, key="changes", num_rows="dynamic",
                       column_config={'0': 'Label', '1': 'Mass', '2': 'Population'},
                       )

changes = st.session_state['changes']
# print(f"{changes=}")
delete_selected_masses(frags, changes.get('deleted_rows'))


######################################################################
if frags:
  fig = update_plot(T, **{'show_grid': st.session_state.show_grid, 'negative': st.session_state.negative_signal})
  graf = st.pyplot(fig, clear_figure=True, transparent=False)


with st.expander("Information"):
  st.code(f"{T}")

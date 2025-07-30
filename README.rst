#####################################
Time-of-flight spectrometer Simulator
#####################################

tof-simulator is a package to simulate the spectra from a Time-of-Flight mass spectrometer.

It has capabilities to analyze substances from convenient names and may be used as a python module in a script or interactively as a Graphical program.

**********
Interfaces
**********

The package may be used in three different forms:

- Python module in a script. Something like:


  ```python

  from tofsim import ToF
  # Create the TOF with all isotopes from Ar and Kr
  T = ToF('Ar','Kr')

  # Adjust the TOF parameters
  T.Vs = 120                      # Extraction voltaje
  T.Vd = 3000                     # Acceleration voltaje
  
  
  T.signal()                      # Make the spectra
  
  p = T.get_statistics_peaks()    # Get the peaks
  
  print(p)                        # Print the peaks

  ```


- Gtk GUI interface `tof_gtk`

- Web GUI interface `tof_stl`
  


****
Demo
****


- Start the GUI and calculate the spectra

  .. image:: doc/images/demo1.gif


- Modify the TOF parameters and recalculate

  .. image:: doc/images/demo2.gif


.. note:: See Project page: https://github.com/fiolj/tof-simulator

	  

************
Installation
************

Library installation
====================

Install using pip, either system-wide (administrator rights are needed)

::

   pip install tof-simulator

or (usually preferred) for the current user:

::

   pip install --user tof-simulator

   
.. note:: The installation as described above does not include GUI systems, they are optional

Gtk GUI installation
====================

To install the optional Gtk GUI use:

::

   pip install --user tof-simulator[gtk]


Web GUI installation
====================

The optional Web GUI uses streamlit ( https://streamlit.io/ ), and can be installed as:

::

   pip install --user tof-simulator[stl]


Installation from source
========================

In order to install from source, you can:

- Clone the project
  ::

     git clone https://github.com/fiolj/tof-simulator

- Go to the local folder of the project and build the package:

  ::

     cd tof-simulator
     python3 -m build
   
- Install the recently created package

  ::

     pip install --user dist/tofsim-4.0-py3-none-any.whl[gtk,stl]



************
Dependencies
************

- In order to run the simulator programmatically:

  - Only `Numpy <https://numpy.org>`_ is required.
  - Optionally,  `matplotlib <matplotlib.org>`_  is needed to use included capabilities for plotting.

- To use the Gtk GUI, the requirements are:

  - `matplotlib <matplotlib.org>`_

  - `PyGobject <https://pygobject.readthedocs.io/en/latest>`_.
    
    Information on how to install PyGobject on different platforms may be found in
    `the documentation <https://pygobject.readthedocs.io/en/latest/getting_started.html>`_

- To use the Gtk GUI, the requirements are:

  - `matplotlib <matplotlib.org>`_

  - `streamlit <https://streamlit.io/>`_
    

*********
Copyright
*********

Copyright (C) 2020 Juan Fiol

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/.



*************
Documentation
*************

Further information on installation, dependencies and use may be found in the `documentation <https://tof-simulator.readthedocs.io/en/latest/>`_.

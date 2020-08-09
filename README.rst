#####################################
Time-of-flight spectrometer Simulator
#####################################

tof-simulator is a package to simulate the spectra from a Time-of-Flight mass spectrometer.

It has capabilities to analyze substances from convenient names and may be used as a python module in a script or interactively as a Graphical program.

************
Installation
************

Install using pip, either system-wide (administrator rights are needed)

::

   pip install tof-simulator-X.Y.tar.gz

or (usually preferred) for the current user:

::

   pip install --user tof-simulator-X.Y.tar.gz

************
Dependencies
************

- In order to run the simulator programmatically:

  - Only `Numpy <https://numpy.org>`_ is required.
  - Optionally,  `matplotlib <matplotlib.org>`_  is needed to use included capabilities for plotting.

- To use the GUI, the requirements are:

  - `matplotlib <matplotlib.org>`_

  - `PyGobject <https://pygobject.readthedocs.io/en/latest>`_.
    
    Information on how to install PyGobject on different platforms may be found in
    `the documentation <https://pygobject.readthedocs.io/en/latest/getting_started.html>`_


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
along with this program.  If not, see <https://www.gnu.org/licenses/>.



*************
Documentation
*************

Further information on installation, dependencies and use is in the `documentation <https://fiolj.github.io/tof-simulator/>`_.

############
Installation
############

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
  - Optionally:

    - Package `tabulate <https://github.com/astanin/python-tabulate>`_ for pretty-printing information on TOF parameters and masses.

    - `matplotlib <matplotlib.org>`_  is needed to use included capabilities for plotting.

- To use the GUI, the additional requirements are:

  - `matplotlib <matplotlib.org>`_

  - `PyGobject <https://pygobject.readthedocs.io/en/latest>`_.
    
    Information on how to install PyGobject on different platforms may be found in
    `the documentation <https://pygobject.readthedocs.io/en/latest/getting_started.html>`_

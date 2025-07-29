************
Installation
************

Library installation
====================

Install using pip, either system-wide (administrator rights are needed)::

   pip install tof-simulator

or (usually preferred) for the current user::

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

    

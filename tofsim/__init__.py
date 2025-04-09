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

__all__ = ["tof", "nist_elem", "gtk", "stl"]

from .version import __version__
from .nist_elem import Sustancias, analyze_substance, mass2conf
from .tof import ToF
from .stl import app
# from .gtk import tof_gtk

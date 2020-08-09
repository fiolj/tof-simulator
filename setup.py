#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# File: setup.py
#
# Copyright (C) 2020 Juan Fiol
# Written by Juan Fiol <juanfiol@gmail.com>
import os
from distutils.core import setup
from tofsim import version


def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    "\n" + read('README.txt') + '\n' + version.COPYRIGHT
)


def setup_package():
  setup(name="tof-simulator",
        version=version.VERSION,
        description="Time-of-Flight Mass spectrometry simulator",
        long_description=long_description,
        url="www.cab.cnea.gov.ar",
        keywords="simulation,mass-spectrometry,TOF",
        author="Juan Fiol",
        author_email="fiol@cab.cnea.gov.ar",
        packages=['tofsim'],
        package_data={'tofsim': ['tof_gtk.xml', 'tof.conf', 'tof_teoria.pdf', 'nist_data.txt'],
                      },
        data_files=[('share/applications', ['tof_gtk.desktop']),
                    ],
        scripts=['scripts/tof_gtk'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ]
        )


if __name__ == '__main__':
  print(version.VERSION)
  setup_package()

#!/usr/bin/env python3
# *****************************************************************************
# Copyright (C) 2021-2022 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
# This file is part of the visyerres_sgdf Python module.
# *****************************************************************************
""" Setup script for the thcolor Python package and script. """

from setuptools import setup as _setup

kwargs = {}
kwargs['setup_requires'] = ['flake8']

_setup(**kwargs)

# End of file.

#!/usr/bin/env python

# Copyright 2018 The Piccolo Team
#
# This file is part of piccolo2-web.
#
# piccolo2-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-web.  If not, see <http://www.gnu.org/licenses/>.

'''
Definitions of global variables
File: definitions.py

Contains:
    ROOT_DIR
    CONFIG_PATH

'''
import os

# This is the Project Root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# This is where the config file is
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.conf')

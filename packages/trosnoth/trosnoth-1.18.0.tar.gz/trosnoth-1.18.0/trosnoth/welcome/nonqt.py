# Trosnoth (Ubertweak Platform Game)
# Copyright (C) Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''
The purpose of this file is to allow modules outside of trosnoth.welcome
to access functions that are common to trosnoth.welcome without risking
importing Qt if it's not already there.

This module MUST NOT import PySide2, either directly or indirectly.
'''

import contextlib
import sys

from trosnoth import data


ICON_FILE = data.base_path / 'welcome' / 'icon.png'


def hide_qt_windows():
    if 'PySide2.QtCore' in sys.modules:
        from trosnoth.welcome.common import hide_qt_windows as hide
        return hide()
    return empty_context_manager()


@contextlib.contextmanager
def empty_context_manager():
    yield

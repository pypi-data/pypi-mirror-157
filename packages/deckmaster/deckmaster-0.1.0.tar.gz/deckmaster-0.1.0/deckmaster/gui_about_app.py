#!/usr/bin/env python3


"""
""" """

This file is part of python-deckmaster.

python-deckmaster is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

python-deckmaster is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with python-deckmaster.  If not, see <https://www.gnu.org/licenses/>.

Copyright (c) 2022, Maciej Barć <xgqt@riseup.net>
Licensed under the GNU GPL v3 License
SPDX-License-Identifier: GPL-3.0-only
"""


from sys import version as PYTHON_VERSION

from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.QtWidgets import QMessageBox

from . import (
    __app_name__,
    __description__,
    __version__
)


def about_app():
    """Show information about the application."""

    message = QMessageBox()
    details_text = f"""Versions of used libraries:
  - Python
    {PYTHON_VERSION}
  - Qt
    {QT_VERSION_STR}
"""

    message.setWindowTitle(f"About {__app_name__}")
    message.setIcon(QMessageBox.Information)

    message.setText(f"{__app_name__}, version {__version__}")
    message.setInformativeText(__description__)
    message.setDetailedText(details_text)

    message.exec_()

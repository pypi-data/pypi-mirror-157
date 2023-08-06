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


from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QMenuBar
)

from . import __app_name__

from . import deck_json
from . import gui_about_app


class MenuWidget(QMenuBar):
    """Custom menu widget."""

    def __init__(self, root=None):
        super().__init__()

        self.root = root

        self.file_menu = self.addMenu("&File")

        self.action_new = QAction("&New")
        self.action_new.setShortcut("Ctrl+N")
        self.action_new.setStatusTip("New deck")
        self.action_new.triggered.connect(self.new_file)
        self.file_menu.addAction(self.action_new)

        self.action_open = QAction("&Open")
        self.action_open.setShortcut("Ctrl+O")
        self.action_open.setStatusTip("Open deck")
        self.action_open.triggered.connect(self.open_file)
        self.file_menu.addAction(self.action_open)

        self.action_save = QAction("&Save")
        self.action_save.setShortcut("Ctrl+S")
        self.action_save.setStatusTip("Save deck")
        self.action_save.triggered.connect(self.save_file)
        self.file_menu.addAction(self.action_save)

        self.action_exit = QAction("&Exit")
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.setStatusTip(f"Exit {__app_name__}")
        self.action_exit.triggered.connect(self.close_app)
        self.file_menu.addAction(self.action_exit)

        self.help_menu = self.addMenu("&Help")

        self.action_about = QAction("&About")
        self.action_about.setStatusTip(f"About {__app_name__}")
        self.action_about.triggered.connect(gui_about_app.about_app)
        self.help_menu.addAction(self.action_about)

    @pyqtSlot()
    def new_file(self):
        """Start creating the deck from scratch."""

        self.root.deck = deck_json.DeckJSON()

        self.root.refill_deck_list()

    @pyqtSlot()
    def open_file(self):
        """Open deck from a file."""

        selected_file = QFileDialog.getOpenFileName(
            self, "Open file", "~", "DeckJSON (*.json)")

        if self.root.debug:
            print(selected_file)

        if selected_file[0] != "" and isinstance(selected_file[0], str):
            # Just the path.
            self.root.deck.read_file(selected_file[0])

            # Put the deck contents in their place.
            self.root.refill_deck_list()

    @pyqtSlot()
    def save_file(self):
        """Save deck as a file."""

        selected_file = QFileDialog.getSaveFileName(
            self, "Save file", "~", "DeckJSON (*.json)")

        if self.root.debug:
            print(selected_file)

        if selected_file[0] != "" and isinstance(selected_file[0], str):
            # Just the path.
            self.root.deck.write_file(selected_file[0])

    @pyqtSlot()
    def close_app(self):
        """Close the application, Qt-style."""

        self.root.close()

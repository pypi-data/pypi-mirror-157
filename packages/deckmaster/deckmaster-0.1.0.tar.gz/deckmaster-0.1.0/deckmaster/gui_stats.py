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
    QGridLayout,
    QPlainTextEdit,
    QWidget
)

from . import bridge


class StatsWidget(QWidget):
    """Custom stats widget."""

    def __init__(self, root=None):
        super().__init__()

        self.deck = root.deck
        self.session = root.session

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.stats_text_box = QPlainTextEdit()
        self.layout.addWidget(self.stats_text_box)
        self.stats_text_box.setPlainText("")

    @pyqtSlot()
    def display_deck_stats(self):
        """Display deck statistics in the stats tab."""

        self.stats_text_box.clear()

        self.stats_text_box.insertPlainText("Colors distribution:\n")
        colors = bridge.count_colors(self.session, self.deck, "mainboard")
        for key, value in colors.items():
            self.stats_text_box.insertPlainText(f" - {key}: {value}\n")

        self.stats_text_box.insertPlainText("Card types distribution:\n")
        types = bridge.count_types(self.session, self.deck, "mainboard")
        for key, value in types.items():
            self.stats_text_box.insertPlainText(f" - {key}: {value}\n")

        self.stats_text_box.insertPlainText("Mana cost distribution:\n")
        cmcs = bridge.count_cmcs(self.session, self.deck, "mainboard")
        for key, value in cmcs.items():
            self.stats_text_box.insertPlainText(f" - {key}: {value}\n")

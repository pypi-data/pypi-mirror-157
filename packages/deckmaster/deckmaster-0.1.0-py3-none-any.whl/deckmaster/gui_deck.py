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
    QListWidget,
    QPushButton,
    QWidget
)


class DeckWidget(QWidget):
    """Custom deck widget."""

    def __init__(self, root=None):
        super().__init__()

        self.root = root
        self.debug = root.debug
        self.deck = root.deck

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.deck_cards_list = QListWidget()
        self.layout.addWidget(self.deck_cards_list)

        self.deck_plus_one_card_button = QPushButton("+1")
        self.layout.addWidget(self.deck_plus_one_card_button)
        self.deck_plus_one_card_button.clicked.connect(self.plus_one_card)

        self.deck_minus_one_card_button = QPushButton("-1")
        self.layout.addWidget(self.deck_minus_one_card_button)
        self.deck_minus_one_card_button.clicked.connect(self.minus_one_card)

        self.deck_remove_card_button = QPushButton("Remove")
        self.layout.addWidget(self.deck_remove_card_button)
        self.deck_remove_card_button.clicked.connect(self.remove_card)

    @pyqtSlot()
    def plus_one_card(self):
        """Increase the amount of currently selected card in deck by one."""

        selected_index = self.deck_cards_list.currentIndex().row()
        index_uuid = self.deck.contents["mainboard"][selected_index]["uuid"]

        if self.debug:
            print(f"selected_index = {selected_index}")
            print(f"index_uuid = {index_uuid}")

        self.deck.add_card("mainboard", index_uuid, amount=1)

        if self.root:
            self.root.refill_deck_list()

    @pyqtSlot()
    def minus_one_card(self):
        """Increase the amount of currently selected card in deck by one."""

        selected_index = self.deck_cards_list.currentIndex().row()
        index_uuid = self.deck.contents["mainboard"][selected_index]["uuid"]

        if self.debug:
            print(f"selected_index = {selected_index}")
            print(f"index_uuid = {index_uuid}")

        self.deck.remove_card("mainboard", index_uuid, amount=1)

        if self.root:
            self.root.refill_deck_list()

    @pyqtSlot()
    def remove_card(self):
        """Increase the amount of currently selected card in deck by one."""

        selected_index = self.deck_cards_list.currentIndex().row()
        index_uuid = self.deck.contents["mainboard"][selected_index]["uuid"]

        if self.debug:
            print(f"selected_index = {selected_index}")
            print(f"index_uuid = {index_uuid}")

        self.deck.remove_card_completely("mainboard", index_uuid)

        if self.root:
            self.root.refill_deck_list()

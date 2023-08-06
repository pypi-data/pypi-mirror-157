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
    QComboBox,
    QGridLayout,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QWidget
)

from .printingsdb import Cards


class SearchWidget(QWidget):
    """Custom search widget."""

    def __init__(self, root=None):
        super().__init__()

        self.root = root
        self.debug = root.debug
        self.deck = root.deck
        self.session = root.session

        # List of UUIDs of search results
        self.search_card_list = []

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # TODO: Make so the user cannot change text.
        self.search_card_text_box = QPlainTextEdit()
        self.layout.addWidget(self.search_card_text_box)
        self.search_card_text_box.setPlainText("")

        self.search_card_property_list = QComboBox()
        self.layout.addWidget(self.search_card_property_list)
        self.search_card_property_list.addItem("name")
        self.search_card_property_list.addItem("uuid")
        self.search_card_property_list.addItem("type")
        self.search_card_property_list.addItem("colorIdentity")
        self.search_card_property_list.addItem("setCode")
        self.search_card_property_list.addItem("artist")

        self.search_card_text_field = QLineEdit()
        self.layout.addWidget(self.search_card_text_field)

        self.search_card_search_button = QPushButton("Search")
        self.layout.addWidget(self.search_card_search_button)
        self.search_card_search_button.clicked.connect(self.search_card)

        self.search_card_results_list = QListWidget()
        self.layout.addWidget(self.search_card_results_list)
        self.search_card_results_list.clicked.connect(self.set_displayed_card)

        self.search_card_add_to_deck_button = QPushButton("Add to deck")
        self.layout.addWidget(self.search_card_add_to_deck_button)
        self.search_card_add_to_deck_button.clicked.connect(
            self.add_result_card_to_deck)

    @pyqtSlot()
    def search_card(self):
        """Search for a card."""

        query_property = str(self.search_card_property_list.currentText())
        query_text = self.search_card_text_field.text()

        card_property = Cards.__table__.columns[query_property]
        property_name = query_text

        result = (self.session.query(Cards)
                  .filter(card_property == property_name))

        # Clean the card list helper variable
        self.search_card_list = []

        # Clean the results list
        self.search_card_results_list.clear()

        for card in result:
            self.search_card_list.append(card.uuid)
            self.search_card_results_list.addItem(
                f"{card.name}  {card.manaCost}  {card.setCode}")

        self.search_card_text_box.setPlainText(
            f"Query: {query_property} {query_text}")

    @pyqtSlot()
    def set_displayed_card(self):
        """Set the displayed card."""

        selected_index = self.search_card_results_list.currentIndex().row()
        index_uuid = self.search_card_list[selected_index]

        if self.debug:
            print(f"selected_index = {selected_index}")
            print(f"index_uuid = {index_uuid}")

        # Query by card's UUID
        result = (self.session.query(Cards)
                  .filter(Cards.uuid == index_uuid))

        # Trick for empty lists and if somehow we get many results,
        # but that should not happen with UUIDs.
        for card in result:
            content = (
                f"{card.name}\n" +
                f"{card.manaCost}" +
                f", ({card.convertedManaCost}, {card.colorIdentity})\n" +
                f"{card.type}\n" +
                f"{card.text}\n" +
                (f"{card.power} / {card.toughness}\n"
                 if card.power and card.toughness else "") +
                (card.loyalty if card.loyalty else ""))

            if self.debug:
                print(content)

            self.search_card_text_box.setPlainText(content)

    @pyqtSlot()
    def add_result_card_to_deck(self):
        """Add a card which is a result of a search action to the deck."""

        selected_index = self.search_card_results_list.currentIndex().row()
        index_uuid = self.search_card_list[selected_index]

        if self.debug:
            print(f"selected_index = {selected_index}")
            print(f"index_uuid = {index_uuid}")

        self.deck.add_card("mainboard", index_uuid, amount=1)

        if self.root:
            self.root.refill_deck_list()

#!/usr/bin/env python3


"""
Application GUI.
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


from PyQt5.QtWidgets import (
    QGridLayout,
    QTabWidget,
    QWidget
)

from . import __description__
from . import bridge
from . import deck_json

from .printingsdb import Session

from .gui_deck import DeckWidget
from .gui_menu import MenuWidget
from .gui_search import SearchWidget
from .gui_stats import StatsWidget


class App(QWidget):
    """Main application class."""

    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug

        self.deck = deck_json.DeckJSON()
        self.session = Session(debug=debug).session
        self.board_names = self.deck.boards

        # List of UUIDs of search results
        self.search_card_list = []

        self.title = f"Deckmaster - {__description__}"

        # Window properties

        self.left = 0
        self.top = 0
        self.width = 700
        self.height = 500

        # Main layout

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Menu bar and keyboard shortcuts for actions

        self.menu_bar = MenuWidget(root=self)
        self.layout.addWidget(self.menu_bar)

        # Tabs

        # Search tab
        self.search_tab = SearchWidget(root=self)

        # Deck tab
        self.deck_tab = DeckWidget(root=self)

        # Stats tab
        self.stats_tab = StatsWidget(root=self)

        # Tabs initialization
        self.tabwidget = QTabWidget()
        self.layout.addWidget(self.tabwidget)
        self.tabwidget.addTab(self.search_tab, "Search")
        self.tabwidget.addTab(self.deck_tab, "Deck")
        self.tabwidget.addTab(self.stats_tab, "Stats")

        # Refresh stats on tab change
        self.tabwidget.tabBarClicked.connect(self.stats_tab.display_deck_stats)

        # Initialization

        # Initialize the UI
        self.init_ui()

    def refill_deck_list(self):
        """Fill the deck list again."""

        self.deck_tab.deck_cards_list.clear()

        for content in self.deck.contents["mainboard"]:
            uuid = content["uuid"]
            amount = content["amount"]
            maybe_card = bridge.get_card_by_uuid(self.session, uuid)

            if maybe_card:
                card = maybe_card
                self.deck_tab.deck_cards_list.addItem(
                    f"{card.name} {card.manaCost} {card.setCode} x{amount}")

    def init_ui(self):
        """Initialize the user interface."""

        # Window
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Show
        self.show()

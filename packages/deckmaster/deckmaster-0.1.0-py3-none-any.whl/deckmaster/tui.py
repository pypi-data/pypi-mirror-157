#!/usr/bin/env python3


"""
Application TUI.
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


import os

from cmd import Cmd

from . import bridge
from . import deck_json

from .printingsdb import Session, Cards


def print_card(card):
    """Print most important card object properties."""

    print(f"{card.name} ({card.uuid})")
    print(f"{card.manaCost} ({card.convertedManaCost}, {card.colorIdentity})")
    print(card.type)
    print(card.text)

    if card.power and card.toughness:
        print(f"{card.power} / {card.toughness}")

    if card.loyalty:
        print(f"{card.loyalty}")


class App(Cmd):
    """Main application class."""

    def __init__(self, debug=False):

        super().__init__()

        self.deck = deck_json.DeckJSON()
        self.session = Session(debug=debug).session

        self.board_names = self.deck.boards
        self.prompt = "(DeckMaster)> "

    def do_exit(self, _):
        """Command to exit the REPL."""

        return True

    def do_EOF(self, _):
        """Special method to quit on "Ctrl-D"."""

        return True

    def postloop(self):

        print("")
        print("Goodbye!")
        print((os.get_terminal_size()[0] - 1) * "-")

    def do_json(self, _):
        """Show current deck in JSON format."""

        print(self.deck.string())

    def do_name(self, string_args):
        """Set deck's name."""

        if string_args == "":
            print(self.deck.json()["name"])
        else:
            self.deck.set_name(string_args)

    def do_read(self, string_args):
        """Read deck form path."""

        self.deck.read_file(string_args)

    def do_write(self, string_args):
        """Write the deck to path."""

        self.deck.write_file(string_args)

    def do_add(self, string_args):
        """Add a amount of cards by its uuid to a board."""

        list_args = string_args.split(" ")

        if len(list_args) == 3:
            self.deck.add_card(list_args[0], list_args[1], int(list_args[2]))
        else:
            print("Wrong number of arguments, 3 expected.")

    def do_remove(self, string_args):
        """Remove a amount of cards by its uuid to a board."""

        list_args = string_args.split(" ")

        self.deck.remove_card(list_args[0], list_args[1], int(list_args[2]))

    def do_search(self, string_args):
        """Search for a card."""

        list_args = string_args.split(" ")
        card_property = Cards.__table__.columns[list_args[0]]
        property_name = " ".join(list_args[1:])

        result = (self.session.query(Cards)
                  .filter(card_property == property_name))
        for card in result:
            print(f" - {card.name}")
            print(f"   {card.manaCost}, {card.setCode}, {card.uuid}")

    def get_card_by_uuid(self, card_uuid):
        """Get card object by UUID."""

        return bridge.get_card_by_uuid(self.session, card_uuid)

    def do_card(self, string_args):
        """Given a card UUID show it's most important properties."""

        maybe_card = self.get_card_by_uuid(string_args)

        if maybe_card:
            print_card(maybe_card)

    def count_board_cards(self, board):
        """Count number of cards in a board."""

        return bridge.count_board_cards(self.deck, board)

    def do_count(self, string_args):
        """Count cards in a board."""

        if string_args == "":
            for board_name in self.board_names:
                self.do_count(board_name)
        else:
            print(f"Board: {string_args}")
            print(f"Cards: {self.count_board_cards(string_args)}")

    def do_decklist(self, _):
        """Print the "decklist"."""

        deck_name = self.deck.json()["name"]

        if deck_name == "":
            print("Unnamed deck")
        else:
            print(f"Deck name: {deck_name}")

        for board_name in self.board_names:
            board = self.deck.json()[board_name]

            print(f"Board: {board_name}, {len(board)} cards:")

            for card in board:
                uuid = card["uuid"]
                name = self.get_card_by_uuid(uuid).name
                amount = card["amount"]
                print(f" - {name} ({uuid}) [{amount}]")

    def colors(self):
        """Show amount of cards for given color."""

        colors = bridge.count_colors(self.session, self.deck, "mainboard")

        print("Color distribution:")

        for key, val in sorted(colors.items()):
            if val > 0:
                print(f" - {key}: {val}")

    def types(self):
        """Show amount of cards for given card types."""

        deck_types = bridge.count_types(self.session, self.deck, "mainboard")

        print("Type distribution:")

        for key, val in sorted(deck_types.items()):
            if val > 0:
                print(f" - {key}: {val}")

    def cmcs(self):
        """Show amount of cards for given converted mana costs."""

        deck_cmcs = bridge.count_cmcs(self.session, self.deck, "mainboard")

        print("Converted mana cost distribution:")

        for key, val in sorted(deck_cmcs.items()):
            if val > 0:
                print(f" - {key}: {val}")

    def do_stats(self, _):
        """Print deck statistics."""

        self.do_count("")
        self.colors()
        self.cmcs()
        self.types()

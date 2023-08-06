#!/usr/bin/env python3


"""
API to access JSON decklists.

Format:
```json
{
  "name": "Deck Name",
  "mainboard": [{"uuid": "UUID", "amount": 3}],
  "sideboard": [],
  "commanders": []
};
```
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


import json


default_contents = {
    "name": "", "game": "", "format": "",
    "mainboard": [], "sideboard": [], "commander": []
}


class DeckJSON():
    "Deck JSON class."

    def __init__(self, contents=default_contents):

        self.boards = ["mainboard", "sideboard", "commander"]
        self.contents = contents

    def json(self):
        """Return contents of a DeckJSON object as JSON."""

        return self.contents

    def string(self):
        """Return contents of a DeckJSON object as string."""

        return json.dumps(self.contents)

    def read_file(self, file_path):
        """Parse deck JSON file to JSON and populate object's contents."""

        with open(file_path, "r", encoding="utf-8") as opened_file:
            self.contents = json.loads(opened_file.read())

    def write_file(self, file_path):
        """Write deck JSON file from a DeckJSON object contents."""

        with open(file_path, "w", encoding="utf-8") as opened_file:
            opened_file.write(self.string())

    def set_name(self, deck_name):
        """Set deck's name."""

        self.contents["name"] = deck_name

    def check_board(self, board):
        """Check if a given "board" is valid."""

        return board in self.boards

    def assert_board(self, board):
        """Throw if a given "board" is invalid."""

        assert self.check_board(board), f"Board is invalid, given \"{board}\"."

    def add_card(self, board, uuid, amount=1):
        """Add card to "board" list field of a DeckJSON object."""

        self.assert_board(board)

        next_card = next(
            (card for card in self.contents[board] if card["uuid"] == uuid),
            False)

        if next_card:
            next_card["amount"] += amount
        else:
            self.contents[board].append({"uuid": uuid, "amount": amount})

    def remove_card(self, board, uuid, amount=1):
        """Remove a specified amount of a given card from "board" list field
        of a DeckJSON object."""

        self.assert_board(board)

        for card in self.contents[board]:
            if card["uuid"] == uuid:
                if card["amount"] - amount <= 0:
                    self.contents[board].remove(card)
                else:
                    card["amount"] -= amount
                break

    def remove_card_completely(self, board, uuid):
        """Remove all instances of a card from a "board"."""

        self.assert_board(board)

        for card in self.contents[board]:
            if card["uuid"] == uuid:
                self.contents[board].remove(card)

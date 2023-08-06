#!/usr/bin/env python3


"""
Functions to bridge "deck_json" and "printingsdb".
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


from .printingsdb import Cards


def get_card_by_uuid(active_session, card_uuid):
    """Get card object by UUID."""

    query_result = None

    try:
        query_result = (active_session.query(Cards)
                        .filter(Cards.uuid == card_uuid))
    except Exception:
        pass

    if query_result and query_result != []:
        return query_result[0]

    return None


def count_board_cards(deck_json_deck, board_name):
    """Count number of cards in a board."""

    return sum(map((lambda c: c["amount"]), deck_json_deck.json()[board_name]))


def count_colors(active_session, deck_json_deck, board_name):
    """Count card colors in a deck."""

    deck_colors = {
        "black": 0,
        "blue": 0,
        "colorless": 0,
        "green": 0,
        "red": 0,
        "white": 0
    }

    for content in deck_json_deck.json()[board_name]:
        card = get_card_by_uuid(active_session, content["uuid"])
        amount = content["amount"]

        if not card.colorIdentity:
            deck_colors["colorless"] += amount
        # FIXME: Spaghetti code below
        if "B" in card.colorIdentity:
            deck_colors["black"] += amount
        if "U" in card.colorIdentity:
            deck_colors["blue"] += amount
        if "G" in card.colorIdentity:
            deck_colors["green"] += amount
        if "R" in card.colorIdentity:
            deck_colors["red"] += amount
        if "W" in card.colorIdentity:
            deck_colors["white"] += amount

    return deck_colors


def count_types(active_session, deck_json_deck, board_name):
    """Count card types in a deck."""

    deck_types = {}

    for content in deck_json_deck.json()[board_name]:
        card = get_card_by_uuid(active_session, content["uuid"])
        amount = content["amount"]

        # Strip supertypes and subtypes
        real_type = card.type.split("—")[0].strip()
        if card.supertypes:
            real_type = real_type.removeprefix(card.supertypes).strip()

        if real_type in deck_types:
            deck_types[real_type] = (deck_types[real_type] + amount)
        else:
            deck_types[real_type] = amount

    return deck_types


def count_cmcs(active_session, deck_json_deck, board_name):
    """Count cards converted mana costs in a deck."""

    deck_cmcs = {}

    for content in deck_json_deck.json()[board_name]:
        card = get_card_by_uuid(active_session, content["uuid"])
        amount = content["amount"]
        card_cmc = int(card.convertedManaCost)

        if card_cmc in deck_cmcs:
            deck_cmcs[card_cmc] = (deck_cmcs[card_cmc] + amount)
        else:
            deck_cmcs[card_cmc] = amount

    return deck_cmcs

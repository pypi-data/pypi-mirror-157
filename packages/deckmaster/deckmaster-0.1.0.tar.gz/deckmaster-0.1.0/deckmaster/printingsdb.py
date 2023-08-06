#!/usr/bin/env python3


"""
Interaction with database provided by MTGJSON.
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

# from sqlalchemy.sql import select

from sqlalchemy import (
    Column,
    # ForeignKey,
    Float,
    Integer,
    Date,
    MetaData,
    String,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from . import __cache_dir__


class Connection():
    """Connection to "AllPrintings.sqlite" database."""

    fallback_printingsdb_path = "sqlite:///.cache/AllPrintings.sqlite"

    def __init__(self, printingsdb_path=None, debug=False):

        if printingsdb_path:
            self.dir = printingsdb_path
        else:
            if os.path.exists(".cache/AllPrintings.sqlite"):
                self.dir = ".cache"
            else:
                self.dir = __cache_dir__

        self.connection_string = f"sqlite:///{self.dir}/AllPrintings.sqlite"

        if debug:
            print(f"connection_string = {self.connection_string}")

        self.engine = create_engine(self.connection_string, echo=debug)
        self.metadata = MetaData()
        self.connection = self.engine.connect()


class Session():
    """Session of a connection to "AllPrintings.sqlite" database."""

    def __init__(self, debug=False):

        self.db_session = sessionmaker(bind=Connection(debug=debug).engine)
        self.session = self.db_session()


BaseModel = declarative_base()


class Sets(BaseModel):
    """The "sets" table."""

    __tablename__ = "sets"
    id = Column(Integer, primary_key=True)
    baseSetSize = Column(Integer)
    block = Column(String(100))
    booster = Column(String(100))
    code = Column(String(8), nullable=False)
    isFoilOnly = Column(Integer, nullable=False)
    isForeignOnly = Column(Integer, nullable=False)
    isNonFoilOnly = Column(Integer, nullable=False)
    isOnlineOnly = Column(Integer, nullable=False)
    isPartialPreview = Column(Integer, nullable=False)
    keyruneCode = Column(String(100))
    mcmId = Column(Integer)
    mcmIdExtras = Column(Integer)
    mcmName = Column(String(100))
    mtgoCode = Column(String(100))
    name = Column(String(100))
    parentCode = Column(String(100))
    releaseDate = Column(Date)
    sealedProduct = Column(String(100))
    tcgplayerGroupId = Column(Integer)
    totalSetSize = Column(Integer)
    type = Column(String(100))


class Cards(BaseModel):
    """The "cards" table."""

    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    artist = Column(String(100))
    asciiName = Column(String(100))
    availability = Column(String(100))
    boosterTypes = Column(String(100))
    borderColor = Column(String(100))
    cardKingdomEtchedId = Column(String(100))
    cardKingdomFoilId = Column(String(100))
    cardKingdomId = Column(String(100))
    cardParts = Column(String(100))
    colorIdentity = Column(String(100))
    colorIndicator = Column(String(100))
    colors = Column(String(100))
    convertedManaCost = Column(Float)
    duelDeck = Column(String(100))
    edhrecRank = Column(Integer)
    faceConvertedManaCost = Column(Float)
    faceFlavorName = Column(String(100))
    faceManaValue = Column(Float)
    faceName = Column(String(100))
    finishes = Column(String(100))
    flavorName = Column(String(100))
    flavorText = Column(String(100))
    frameEffects = Column(String(100))
    frameVersion = Column(String(100))
    hand = Column(String(100))
    hasAlternativeDeckLimit = Column(String(8), nullable=False, default=0)
    hasContentWarning = Column(String(8), nullable=False, default=0)
    hasFoil = Column(String(8), nullable=False, default=0)
    hasNonFoil = Column(String(8), nullable=False, default=0)
    isAlternative = Column(String(8), nullable=False, default=0)
    isFullArt = Column(String(8), nullable=False, default=0)
    isFunny = Column(String(8), nullable=False, default=0)
    isOnlineOnly = Column(String(8), nullable=False, default=0)
    isOversized = Column(String(8), nullable=False, default=0)
    isPromo = Column(String(8), nullable=False, default=0)
    isRebalanced = Column(String(8), nullable=False, default=0)
    isReprint = Column(String(8), nullable=False, default=0)
    isReserved = Column(String(8), nullable=False, default=0)
    isStarter = Column(String(8), nullable=False, default=0)
    isStorySpotlight = Column(String(8), nullable=False, default=0)
    isTextless = Column(String(8), nullable=False, default=0)
    isTimeshifted = Column(String(8), nullable=False, default=0)
    keywords = Column(String(100))
    language = Column(String(100))
    layout = Column(String(100))
    leadershipSkills = Column(String(100))
    life = Column(String(100))
    loyalty = Column(String(100))
    manaCost = Column(String(100))
    manaValue = Column(Float)
    mcmId = Column(String(100))
    mcmMetaId = Column(String(100))
    mtgArenaId = Column(String(100))
    mtgjsonV4Id = Column(String(100))
    mtgoFoilId = Column(String(100))
    mtgoId = Column(String(100))
    multiverseId = Column(String(100))
    name = Column(String(100))
    number = Column(String(100))
    originalPrintings = Column(String(100))
    originalReleaseDate = Column(String(100))
    otherFaceIds = Column(String(100))
    power = Column(String(100))
    printings = Column(String(100))
    promoTypes = Column(String(100))
    purchaseUrls = Column(String(100))
    rarity = Column(String(100))
    rebalancedPrintings = Column(String(100))
    scryfallId = Column(String(100))
    scryfallIllustrationId = Column(String(100))
    scryfallOracleId = Column(String(100))
    securityStamp = Column(String(100))
    setCode = Column(String(100))
    side = Column(String(100))
    signature = Column(String(100))
    subtypes = Column(String(100))
    supertypes = Column(String(100))
    tcgplayerEtchedProductId = Column(String(100))
    tcgplayerProductId = Column(String(100))
    text = Column(String(100))
    toughness = Column(String(100))
    type = Column(String(100))
    types = Column(String(100))
    uuid = Column(String(36), nullable=False)
    variations = Column(String(100))
    watermark = Column(String(100))


# session.query(Sets).all()[0].name
# session.query(Cards).all()[0].name

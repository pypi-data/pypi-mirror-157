#!/usr/bin/env python3


"""
Module to download database assets.
For Magic: the Gathering - AllPrintings.sqlite
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


from os.path import join
from zipfile import ZipFile

from requests import get

from . import __cache_dir__


def download_mtg_database(download_dir=__cache_dir__):
    """Download a compressed SQLite DB from "https://mtgjson.com/"."""

    db_file = "AllPrintings.sqlite"
    zip_file = f"{db_file}.zip"
    remote_url = f"https://mtgjson.com/api/v5/{zip_file}"
    db_file_path = join(download_dir, db_file)
    zip_file_path = join(download_dir, zip_file)

    try:
        with get(remote_url, stream=True) as remote_url_get:
            remote_url_get.raise_for_status()

            with open(zip_file_path, "wb") as zip_file_path_open:
                print(f"Downloading to {zip_file_path} from {remote_url} ...")

                for chunk in remote_url_get.iter_content(chunk_size=8192):
                    zip_file_path_open.write(chunk)

    except Exception:
        raise Exception("Could not download!")

    try:
        with ZipFile(zip_file_path, "r") as zip_file_path_zipfile:
            print(f"Extracting {zip_file_path} to {db_file_path} ...")

            zip_file_path_zipfile.extractall(download_dir)

    except Exception:
        raise Exception("Could not extract!")

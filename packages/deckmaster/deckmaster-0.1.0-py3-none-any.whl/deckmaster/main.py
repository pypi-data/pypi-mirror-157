#!/usr/bin/env python3


"""
Main entrypoint module.
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
import signal
import sys

import argparse

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    print("Warning: \"QApplication\" not loaded! GUI not available.")

from . import (
    __cache_dir__,
    __description__,
    __version__,
    download,
    gui,
    tui
)


def bootstrap_gui_loop(debug):
    """Initiate needed components and the main GUI application loop."""

    # C-c to kill the app
    # https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app_event_loop = QApplication(sys.argv)
    _ = gui.App(debug=debug)
    sys.exit(app_event_loop.exec_())


def bootstrap_tui_loop(debug):
    """Initiate needed components and the main TUI application loop."""

    app = tui.App(debug=debug)
    app.cmdloop()


def main():
    """Main."""

    parser = argparse.ArgumentParser(
        description=f"%(prog)s - {__description__}"
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-D", "--debug",
        action="store_true",
        help="Turn on debugging options"
    )
    parser.add_argument(
        "-g", "--gui",
        action="store_true",
        help="Launch the graphical interface"
    )
    parser.add_argument(
        "-u", "--update",
        action="store_true",
        help="Download new version of the cards database"
    )
    args = parser.parse_args()

    __cache_dir__.mkdir(parents=True, exist_ok=True)

    if args.update or os.listdir(__cache_dir__) == []:
        download.download_mtg_database()

    if args.debug:
        print("Running with debugging turned on!")

    if args.gui:
        bootstrap_gui_loop(args.debug)
    else:
        bootstrap_tui_loop(args.debug)


if __name__ == "__main__":
    main()

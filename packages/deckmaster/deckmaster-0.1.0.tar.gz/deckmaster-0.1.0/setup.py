#!/usr/bin/env python3


from setuptools import setup

try:
    from deckmaster import __version__
except ImportError:
    __version__ = "unknown"

try:
    from deckmaster import __description__
except ImportError:
    __description__ = "unknown"


setup(
    name="deckmaster",
    version=__version__,
    description=__description__,
    author="Maciej Barć",
    author_email="xgqt@riseup.net",
    url="https://gitlab.com/xgqt/python-deckmaster",
    license="GPL-3",
    keywords="cards ccg deck game tcc",
    python_requires=">=3.6.*",
    install_requires=["PyQt5", "requests", "sqlalchemy"],
    packages=["deckmaster"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["deckmaster = deckmaster.main:main"]},
)

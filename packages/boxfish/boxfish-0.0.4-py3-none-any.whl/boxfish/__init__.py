# __init__.py

"""Boxfish, a lightweight tool for table extraction from HTML pages."""

import pathlib

# Main modules
from boxfish.data import config
from boxfish.data import soups
from boxfish.data import website

# Main functions
from boxfish.data.config import create
from boxfish.data.config import build
from boxfish.data.website import extract

# Version
__version__ = (pathlib.Path(__file__).parent / "VERSION").read_text()

# Initialization
print('Initializing boxfish ...')

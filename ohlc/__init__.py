# flake8: noqa: F401
import sys
__version__ = '0.1.11'
__tag__     = 'py3'

# expose main type and main func in package
from ohlc.types import Ohlc
from ohlc.candles.app import main


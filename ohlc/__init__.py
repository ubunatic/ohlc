# flake8: noqa: F401
# expose main type and main func in package
import sys
__version__ = '0.1.10'
__tag__     = 'py3'

from ohlc.types import Ohlc
from ohlc.candles.app import main


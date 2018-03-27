# flake8: noqa: F401
# expose main type and main func in package
from ohlc.types import Ohlc
from ohlc.candles.app import main

def setup_logging(args):
    import logging
    if args.debug: level = logging.DEBUG
    else:          level = logging.INFO
    logging.basicConfig(level=level)


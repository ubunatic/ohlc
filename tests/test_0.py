import sys
import ohlc

def test_version():
    assert ohlc.__tag__ == 'py3'
    assert ohlc.__version__ > '0.0.0'

import sys
import ohlc

def test_version():
    py  = sys.version_info.major
    tag = ohlc.__tag__

    if   py >= 3: assert tag == 'py3'
    elif py < 3:  assert tag == 'py2'
    else:         assert False, 'bad or missing tags'

    assert ohlc.__version__ > '0.0.0'

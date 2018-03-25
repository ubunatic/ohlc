[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ubunatic)

ohlc: data type and tools
=========================
ohlc provides `Ohlc`, a `namedtuple` for storing and efficiently processing
open-high-low-close data, used for financial charts and calculations.
It also provides tools for processing and visualizing lists of `Ohlc` values
in the console.

Examples
--------
```python
    from ohlc import Ohlc
    
    o = Ohlc.from_values([2,5,4,7,11,7,2,9,5])  # Ohlc(open=2, high=11, low=2, close=5)    
    o.spread()                                  # 9    
    o = Ohlc(3,4,1,2)                           # Ohlc(open=3, high=4, low=1, close=2)   
    o == (3,4,1,2)                              # True -- Yeay! it is a regular tuple!

    o1 = Ohlc.from_values(range(5,15))
    o2 = Ohlc.from_values(range(14,3,-1), prev=o1)
    o3 = Ohlc.from_values(range(5,20),    prev=o2)
    [o1,o2,o3]                                  # [Ohlc(open=5, high=14, low=5, close=14),
                                                #  Ohlc(open=14, high=14, low=4, close=4),
                                                #  Ohlc(open=5, high=19, low=5, close=19)]    
    
    o3.heikin()                                 # compute Heikin-Ashi candles from Ohlc chain
                                                # Ohlc(open=9.0, high=19, low=5, close=12.0)
```
Visualization
-------------

![ohlc demo screen](https://github.com/ubunatic/ohlc/blob/master/ohlc-ui.png)

For visualizations it provides raw colored console output using terminal colors and also
supports styled output for embedding in [urwid](http://urwid.org) console apps.
It provides a simple ohlc grapher built using the [widdy](https://github.com/ubunatic/widdy/)
widgets urwid-wrapper.

Installation
------------

    pip install ohlc

Usage (WIP)
-----------
The cli usage is not final, please be patient!

    ohlc candles --name "random values"             # start the ohlc candlestick visualization using random values
    shuf -i0-1000 | ohlc candles --name "shuf 1000" # visualize raw input data

Development
-----------
First clone the repo.

    git clone https://github.com/ubunatic/ohlc
    cd ohlc

Then install the cloned version and install missing tools.

    make             # clean and run all tests
    make install     # install the checked-out dev version
    make build       # transpile Py3 to Py2

You may need to install some tools and modules, i.e., `flake8`, `pytest-3`, `twine`, `urwid`, and maybe others.

[Pull requests](https://github.com/ubunatic/ohlc/pulls) are welcome!

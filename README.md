[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ubunatic)

ohlc: data type and tools
=========================
ohlc provides `Ohlc`, a `namedtuple` for storing and efficiently processing
open-high-low-close data, used for financial charts and calculations.
It also provides tools for processing and visualizing lists of `Ohlc` values
in the console.

For visualizations it provides raw colored console output using terminal colors and also
supports styled output for embedding in [urwid](http://urwid.org) console apps.
It provides a simple ohlc grapher built using the [widdy](https://github.com/ubunatic/widdy/)
widgets urwid-wrapper.

Installation
------------

    pip install ohlc

Usage (WIP)
-----------

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
    make transpiled  # transpile Py3 to Py2

You may need to install some tools and modules, i.e., `flake8`, `pytest-3`, `twine`, `urwid`, and maybe others.

[Pull requests](https://github.com/ubunatic/ohlc/pulls) are welcome!

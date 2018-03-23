[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ubunatic)

ohlc
=====

Widdy ohlc widgets for rapid prototyping of [urwid](http://urwid.org) based console apps.

Installation
------------

    pip install ohlc

Usage
-----
Read the [examples](https://github.com/ubunatic/ohlc/tree/master/ohlc/examples)
or try the demo apps:

    ohlc chuck     # chuck norris joke reader
    ohlc counter   # fun with text tables
    ohlc all       # run all available demos

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

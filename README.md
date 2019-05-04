[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ubunatic)

Ohlc: Types + Tools for Open-High-Low-Close Values
==================================================
Ohlc provides `Ohlc`, a `namedtuple` for storing and efficiently processing
open-high-low-close data, used for financial charts and calculations.
It also provides tools for processing, generating, and visualizing lists of `Ohlc`
values in the console.

Installation
------------

    pip install ohlc


Using the Data Type
-------------------
```python
from ohlc import Ohlc

o = Ohlc.from_values([2,5,4,7,11,7,2,9,5])  # Ohlc(open=2, high=11, low=2, close=5)
o.spread()                                  # 9
o = Ohlc(3,4,1,2)                           # Ohlc(open=3, high=4, low=1, close=2)
o == (3,4,1,2)                              # True -- Yeay! It is a regular tuple!

o1 = Ohlc.from_values(range(5,15))              # Ohlc(open=5, high=14, low=5, close=14)
o2 = Ohlc.from_values(range(14,3,-1), prev=o1)  # Ohlc(open=14, high=14, low=4, close=4)
o3 = Ohlc.from_values(range(5,20),    prev=o2)  # Ohlc(open=5, high=19, low=5, close=19)

o3.heikin()                                 # compute Heikin-Ashi candle from Ohlc chain
                                            # Ohlc(open=9.0, high=19, low=5, close=12.0)
```

Formatting Values
-----------------
```python
for o in [o1,o2,o3]: print(o.format())  # 5.000000 14.000000 5.000000 14.000000
                                        # 14.000000 14.000000 4.000000 4.000000
                                        # 5.000000 19.000000 5.000000 19.000000

print(o.format(sep=','))                # 5.000000,19.000000,5.000000,19.000000
print(o.format(sep='', fmt='{:d}\n'))   # 5
                                        # 19
                                        # 5
                                        # 19
```

Transformation + Aggregation
----------------------------
```python
o1                                      # Ohlc(open=5, high=14, low=5, close=14)
o1.transform(scale=1.25, offset=1)      # Ohlc(open=7.5, high=18.75, low=7.5, close=18.75)]

agg = o.from_ohlc_list([o1,o2,o3])      # Ohlc(open=5, high=19, low=4, close=19)
```


Ohlc Plotting
-------------
For plotting, the class `ohlc.candles.CandleCanvas` provides raw colored console output
using terminal colors, but also supports styled output for embedding in
[urwid](http://urwid.org) console apps.

A simpe plotter (powered by urwid + [widdy](https://github.com/ubunatic/widdy/) widgets)
can be started using the provided `ohlc` command.

```bash
    # start the ohlc candlestick visualization using random values, heikin-ashi candles,
    # price action bars (colors), and the chart title: 'Candles'
    ohlc --pab --ha --random --title 'Candles'
```
![ohlc demo screen](https://github.com/ubunatic/ohlc/blob/master/docs/ohlc-ui.gif)

Omitting most options produces classic candle stick charts.
```bash
    ohlc --random --title 'Classic Candles'
```
![ohlc classic screen](https://github.com/ubunatic/ohlc/blob/master/docs/ohlc-classic.png)

When plotting in interactive mode do not use `/dev/stdin` (this is already used by urwid).
Use a file or file descriptor as the positional `input` argument to `ohlc`.
```bash
	 # plot some input data
    ohlc <(echo -e "8 11 7 4 5\n5 4 8 6\n6\n6 5\n5 6 1 4") --title "Input"
```
![ohlc input plot](https://github.com/ubunatic/ohlc/blob/master/docs/ohlc-input-plot.png)

Non-Interactive Mode
--------------------
There is also a non-interactive mode using the option `-n` or `--non-interactive`
that just reads the input to the end plots the end of the input stream using the
given or available screen width. This mode also supports `/dev/stdin` as input.
```bash
echo -e "8 11 7 4 5\n5 4 8 6\n6\n6 5\n5 6 1 4" | ohlc -n --title "Input" -W 23 -H 8
# ┌─────────────────────┐
# ││        ┌ 11.00     │
# │╽╷       ├ 8.50      │
# │┃┃╹┃╽    ├ 6.00      │
# │╵╵  ╿    └ 3.50      │
# │┌─────┐   max:11.00  │
# │0     1   last:4.00  │
# └─────────────────────┘
```
NOTE: This feature is pre-alpha and not to be considered used for integration in other apps.
 
Tools
-----
The command `ohlc-input` computes an `Ohlc` tuple for each input line and pipes out the four values.
```bash
ohlc-input <(echo 3 4 1 6; echo 6 1 6 2; echo 1 3 8 2)
# 3.000000 6.000000 1.000000 6.000000
# 6.000000 6.000000 1.000000 2.000000
# 1.000000 8.000000 1.000000 2.000000
```

The command `ohlc-random` generates and prints random `Ohlc` values.
```bash
ohlc-random --data_rate 1
# 0.100000 0.100000 0.073059 0.076472
# 0.076472 0.106526 0.073043 0.104767
# 0.104767 0.146023 0.098335 0.142284
# 0.142284 0.169882 0.118809 0.162817
# 0.162817 0.164071 0.131635 0.140002
# 0.140002 0.140246 0.111727 0.124778
```

Development
-----------
First clone/fork the repo.

    git clone https://github.com/ubunatic/ohlc
    cd ohlc

Then install the cloned version and install any missing tools.

    make             # clean and run all tests

You may need to install some tools and modules, i.e., `flake8`, `pytest`, `twine`, `urwid`,
and maybe others.

For packaging and local distribution you can build a Python wheel.

    make build       # build python wheel 

[Pull requests](https://github.com/ubunatic/ohlc/pulls) are welcome!

Change Log
----------
* 2018:       inital PoC and experiments + Py2 Py3 backport magic
* 2019-05-04: removed Python2 support and makepy dependency, added non-interactive mode

Open Issues (by priority)
-------------------------
* project: cleanup upstream dependencies (widdy) and make them optional if possible (urwid)
* project: move custom argparse to separate package
* project: add Pypi flags
* bug: try detect unicode support and fallback to ASCII (e.g., in default iTerm2 on OSX)
* example: BTC Ticker or Custom Symbol Ticker
* usability: react on urwid resizing events
* musthave: add or allow adding `datetime` to `Ohlc` tuples
* project: add CI/CD
* feature: draw correct time axis
* feature: set candle interval (5m 15m 30m 1h 4h, 6h, 1d, 3d, 1w, 1M, etc.)
* feature: add axis labels
* feature: support for bright color scheme
* feature: scrolling over all cached data
* feature: interactively shrink/grow the canvas (adjust top/bottom padding)
* feature: allow setting the cache size
* feature: allow seeking over input files
* feature: monitor CPU usage and reduce redraw (big + fast charts are still very expensive)
* example: Iteractive Ticker
* example: MultiChart App
* example: MultiChart Tickers
* example: Interactive MultiChart Tickers
* feature: indiator overlays (RSI, EMA12, EMA26, etc.)
* feature: indicators bars below chart (price action colored volume bars)

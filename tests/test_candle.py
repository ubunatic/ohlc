# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ohlc.candles import candle, fills, turtle
from ohlc.types import Ohlc
from ohlc import colors
from ohlc.random import random_ohlc_generator
from random import shuffle
import pytest

"""
import logging
def test_benchmark_candles():
    logging.basicConfig(level=logging.INFO)
    t = bench.timeit("test_filler", module_name='ccshell.tests.test_candle', number=3)
    print("timeit main: ", t, "seconds")
    t = bench.bench(test_filler, number=3)
    print("bench main: ", t, "seconds")
"""

def test_candle_chart_resize():
    gen = random_ohlc_generator(v_start=10, v_min=5, v_max=15)

    w = 60
    h = 30
    app = candle.CandleChart(h=h,w=w)

    def test_cases():
        for hi in [0, 1, 2, h/2, h]:
            for wi in [0, 1, 2, w/2, w/3]:
                for border in [None, candle.BOX]:
                    print("start testing", hi, wi, border)
                    yield (hi, wi, border)
                    print("finished testing", hi, wi)

    for hi, wi, border in test_cases():
        app = candle.CandleChart(h=hi, w=wi, border=border)
        for i in range(app.canvas.width): app.add_ohlc(next(gen))
        app.print_lines()
        h2 = hi / 2 + 2
        w2 = wi / 2 + 2
        print("testing resize", hi, wi, "to h =", h2)
        app.resize(h=h2); app.print_lines()
        print("testing resize", hi, wi, "to w = ", w2)
        app.resize(w=w2); app.print_lines()
        print("testing reset", h2, w2)
        app.reset();        app.print_lines()
        print("testing restore + refill", hi, wi)
        app.resize(h=hi, w=wi)
        for i in range(app.canvas.width): app.add_ohlc(next(gen))
        app.print_lines()

def test_filler():
    # ╷╵│
    base = [
        #o  h  l  c, label      # noqa
        [3, 7, 3, 7, "  "],  # bullish
        [3, 7, 2, 7, " ╵"],  # bullish with small low
        [3, 7, 1, 7, " │"],  # bullish with big   low
        [3, 8, 3, 7, "╷ "],  # bullish with small high
        [3, 9, 3, 7, "│ "],  # bullish with big   high
        [3, 8, 2, 7, "╷╵"],  # bullish with small high and low
        [3, 9, 1, 7, "││"],  # bullish with big   high and low
    ]

    hilo = [d[4]  for d in base]
    base = [d[:4] for d in base]

    def scaled(scale, offset=0.0):
        return [[v * scale + offset for v in d] for d in base]

    data = base[:]
    data += scaled(0.5,  0.0)
    data += scaled(0.5,  2.5)
    data += scaled(0.5,  5.0)
    data += scaled(0.25,  0.0)
    data += scaled(0.25,  2.5)
    data += scaled(0.25,  5.0)
    data += scaled(0.25,  7.5)
    data += scaled(0.1,   0.0)
    data += scaled(0.1,   3.0)
    data += scaled(0.1,   6.0)
    data += scaled(0.1,   9.0)

    labels = [2 * ["\033[38;2;100;100;100m"], ["high","low "]]
    labels += int(len(data) / len(base)) * hilo

    rand_data = list(random_ohlc_generator(count=20, v_start=5, v_max=10, v_min=0.1))
    labels += [[" random ",
                " data..."]]

    bulls = data[:] + rand_data
    bears = [[c,h,l,o] for o,h,l,c in data] + rand_data

    y_axis = list("{: >2d} ┤".format(i) for i in range(20))
    y_axis.reverse()

    filler = fills.Filler()
    for values in [bulls, bears]:
        h = 14; scale = h / 10
        candles = [filler.fill(d, height=h, scale=scale) for d in values]
        cols = [y_axis] + candles
        sep = "–" * (len(cols) + 3)
        print("printing test candles:")
        print(sep)
        for row in zip(*cols):
            print("".join(row))
        for row in zip(*labels):
            print("".join(row) + colors.SH_END)
        print(sep)

def test_candle_chart():
    # test small values
    app = candle.CandleChart(h=15)
    n = 500
    low = 1.0
    high = 10.0
    dv = (high - low) / n

    k = 8

    def shuf(l): shuffle(l); return l

    up    = [low    + dv * pow(float(v),2.5) for v in range(n)]
    dn    = [up[-1] - dv * pow(float(v),2.5) for v in range(n)]
    ups   = [Ohlc.from_values(shuf(up[i:i+k])) for i in range(0,n,k)]
    downs = [Ohlc.from_values(shuf(dn[i:i+k])) for i in range(0,n,k)]

    for o in ups + downs: app.add_ohlc(o)
    print("printing candle chart:")
    app.print_lines()

@pytest.mark.skipif(turtle is None, reason="requires drawille")
def test_drawille():
    rand_data = list(random_ohlc_generator(count=20, v_start=5, v_max=10, v_min=0.1))
    frame = turtle.drawille_frame(rand_data)
    print("drawille frame:")
    print(frame)

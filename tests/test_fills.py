from ohlc import colors
from ohlc.colors import modes
from ohlc.candles import fills
from ohlc.random import random_ohlc_generator

def test_color_fills():
    n, t = colors.NUM_COLORS, fills.TERM
    try:     run_fill_test()
    finally: colors.NUM_COLORS, fills.TERM = n, t

def run_fill_test():
    data = random_ohlc_generator(v_start=1, v_max=4, v_min=1)

    def test_fill(fill_mode, color_mode, num_colors, term):
        if color_mode == modes.URWID: test_print = False
        else:                         test_print = True
        print("test_fill: fill_mode{}, color_mode:{}, num_colors:{}, test_print:{}".format(
            fill_mode, color_mode, num_colors, test_print))
        colors.NUM_COLORS = num_colors
        fills.TERM = term
        filler = fills.Filler(color_mode=color_mode, fill_mode=fill_mode)
        candles = [filler.fill(next(data), height=5) for i in range(20)]
        if test_print:
            lines = ["".join(row) for row in zip(*candles)]
            print("\n".join(lines), colors.SH_END)

    for fill_mode in (fills.THIN, fills.SIMPLE, fills.COMPLEX):
        for color_mode in (modes.URWID, modes.SHELL):
            for num_colors in (0,8,256):
                for term in ('xterm', 'linux'):
                    test_fill(fill_mode, color_mode, num_colors, term)


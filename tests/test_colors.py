from ohlc.colors import PriceActionBars, colors
from ohlc.random import random_ohlc_generator

def test_PriceActionBars():
    gen = random_ohlc_generator()
    pab = PriceActionBars()
    values = [next(gen) for _ in range(100)]
    pab_colors = [pab.barcolor(v) for v in values]
    assert len(pab_colors) > 0, 'pa must generate colors'
    for c in pab_colors:
        assert c in colors, 'color must be a valid pab color'

from ohlc.types import Ohlc
from ohlc.random import random_ohlc_generator, random_values_generator


def test_Ohlc():
    tup = Ohlc(open=1, high=2, low=0, close=2)
    assert len(tup) == 4

    vals  = list(random_values_generator(count=10))
    ohlcs = list(random_ohlc_generator(count=10))

    vals5  = 5 * vals
    ohlcs5 = 5 * ohlcs

    assert len(vals) == 10
    assert len(ohlcs) == 10
    assert len(vals5) == 5 * 10
    assert len(ohlcs5) == 5 * 10

    assert len(Ohlc.from_ohlc_list(ohlcs)) == 4
    assert len(Ohlc.from_ohlc_list(ohlcs5)) == 4

    # ohlc computation is repearable
    assert Ohlc.from_values(vals) == Ohlc.from_values(vals5)
    assert Ohlc.from_ohlc_list(ohlcs) == Ohlc.from_ohlc_list(ohlcs5)

    # ohlc computation is idempotent
    for tup in ohlcs:
        assert Ohlc.from_values(list(tup)) == tup

    # no zero prices allowed
    assert 0.0 not in vals
    for tup in ohlcs:
        assert 0.0 not in tup


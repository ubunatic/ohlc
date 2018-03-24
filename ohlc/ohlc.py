from random import random as _rand
from collections import namedtuple
from typing import List

ZERO = 0.000001  # replacement for zero in random number handling

class Ohlc(namedtuple('Ohlc', 'open high low close')):
    """Ohlc stores open, high, low, and close values as namedtuple"""
    ZERO = ZERO
    _prev = None  # type: Ohlc
    @staticmethod
    def from_values(values:List[float], prev=None):
        if len(values) == 0: return None
        o = Ohlc(values[0], max(values), min(values), values[-1])
        o._prev = prev
        return o

    @staticmethod
    def from_ohlc_list(ohlc_list:List[tuple]):
        if len(ohlc_list) == 0: return None
        o, h, l, c = ohlc_list[0]
        for tup in ohlc_list:
            h = max(h, tup.high)
            l = min(l, tup.low)
            c = tup.close
        if l > h: raise ValueError("invalid ohlc data: low above high")
        return Ohlc(o, h, l, c)

    def includes(self, other):
        return self.low <= other.low and self.high >= other.high

    def touches(self, other):
        return self.low == other.low or self.high == other.high

    def spread(self, zero=ZERO):
        dv = self.high - self.low
        if dv == 0: return zero
        else:       return dv

    def transform(self, scale, offset):
        o = Ohlc((self.open  + offset) * scale,
                 (self.high  + offset) * scale,
                 (self.low   + offset) * scale,
                 (self.close + offset) * scale)
        o._prev = self.prev
        return o

    @property
    def prev(self):
        if self._prev is None: return self
        else:                  return self._prev

    def heikin(self):
        prev = self.prev  # type: Ohlc
        if prev is self: o = self.open
        else:            o = (prev.open + prev.close) / 2.0
        c = sum(self) / 4.0
        hk = Ohlc(o, self.high, self.low, c)
        hk._prev = self.prev
        return hk

    def lowest(self, i):
        i = max(0,i); l = self.low; cur = self
        while cur.prev is not cur and i > 0:
            cur = cur.prev; l = min(l, cur.low); i -= 1
        return l

    def highest(self, i):
        i = max(0,i); h = self.high; cur = self
        while cur.prev is not cur and i > 0:
            cur = cur.prev; h = max(h, cur.high); i -= 1
        return h

def random_values_generator(*, v_start=0.1, count=float('inf'), amp=0.2, v_min=None, v_max=None):
    if 0.0 in [v_start, v_min, v_max]:
        raise ValueError("start, min, and max values cannot be zero")
    v_start = float(v_start)
    if v_min is None: v_min = v_start / 10
    if v_max is None: v_max = v_start * 10
    v_min, v_max = float(v_min), float(v_max)
    if not v_min <= v_start <= v_max:
        raise ValueError("start not between min and max values")
    i = 0
    v = v_start
    while i < count:
        i += 1
        v = max(v_min, min(v_max, v + amp * v * (_rand() - _rand())))
        if v == 0.0: v = max(v_min, min(v_max, ZERO))
        yield v

def random_ohlc_generator(*, v_start=0.1, count=float('inf'), step=10, v_max=None, v_min=None):
    nums = random_values_generator(v_start=v_start, v_max=v_max, v_min=v_min)
    values = [float(v_start)]
    i = 0
    o = None
    while i < count:
        # keep last values from prev. batch to allow open-close transition
        values = [values[-1]] + [next(nums) for _ in range(step)]
        i += 1
        o = Ohlc.from_values(values, prev=o)
        yield o


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

    def format(self, sep=' ', fmt='{:f}'):
        return sep.join(fmt.format(v) for v in self)

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


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, logging, os
from collections import namedtuple
from ohlc.types import Ohlc
from ohlc import colors
from ohlc.colors import modes

log = logging.getLogger(__name__)
debug = log.debug
_DEBUG = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log.warn("running fills as main is only useful for testing/debugging")
    debug = print  # replace log debug with raw print to test output
    _DEBUG = True

_example = """
Basic Block Drawing
===================
 ╷
 ░ <-------- dimmed color for bullish candles
 ░ ╷
 ░ █ <------ bright color for bearish candles
 ░ █
 ░ █    ┿ <--- smallest possible OHLC in a single char
 │ █
 │ █    ░ <--- single char candle if {high,low} == {opem,close}
 ╵ │  ╷
      ▒ <--- not used, too bright to distinguish from bearish candles
      ▒
      │ <--- use full stroke for inner-spikes
      ╵ <--- use half strokes for end spikes
"""

# Fill modes
SIMPLE  = 'simple'
COMPLEX = 'complex'
THIN    = 'thin'

TERM = os.environ.get('TERM')

# Tested Main Characters
CandleShapes = namedtuple('CandleShapes', 'dn up eq space spike')
MonoShapes   = CandleShapes(*tuple("█▒┿ │"))  # use full-width TERM=linux compatible chars
ColorShapes  = CandleShapes(*tuple("██┿ │"))  # use full-width TERM=linux compatible chars
SevenShapes  = CandleShapes(*tuple("▉▉┿ │"))  # requires unicode support!

SPIKES = tuple("╷│╵")

def bullish(s): return colors.SH_GREEN + s
def bearish(s): return colors.SH_RED   + s
def spacish(s): return colors.SH_SPACE + s

FillParams = namedtuple('FillParams', 'o,h,l,c,top,bot,oc,lh,ohlc')
Fills      = namedtuple('Fills', 'fill spikes')

def _fill_params(ohlc:Ohlc, scale, offset) -> FillParams:
    o, h, l, c = [scale * (v + offset) for v in ohlc]
    top = max(o,c)
    bot = min(o,c)
    oc = top - bot
    lh = h - l
    return FillParams(o,h,l,c,top,bot,oc,lh,ohlc)


class Filler():
    def __init__(self, *, color_mode=modes.SHELL, shapes=SevenShapes, fill_mode=THIN,
                 heikin=False, pab=False):
        self.price_action_barcolor = colors.PriceActionBars().barcolor
        if TERM == 'linux':
            # system console supports colors but only only limited font set
            shapes = ColorShapes
            fill_mode = SIMPLE
        if colors.NUM_COLORS == 0:
            shapes = MonoShapes
        self.shapes = shapes
        self.color_mode = color_mode
        self.heikin = heikin
        self.pab = pab
        dn, up, eq, space, _ = shapes
        self.bears = Fills(dn, SPIKES)
        self.bulls = Fills(up, SPIKES)
        self.space = space
        if   fill_mode == COMPLEX: self._fill = self._complex_fill
        elif fill_mode == THIN:    self._fill = self._thin_fill
        else:                      self._fill = self._simple_fill

        if color_mode == modes.URWID:
            RED     = colors.RED
            GREEN   = colors.GREEN
            SPACE   = colors.SPACE
            T_RED   = (RED,)
            T_GREEN = (GREEN,)
            self.bearish = lambda c: (RED, c)
            self.bullish = lambda c: (GREEN, c)
            self.spacish = (SPACE, space)
            # setup zip-based functions for color filling, since these may be a bit faster
            # than calling item fill functions in a loop
            self.bearish_zip = lambda chars: zip(len(chars) * T_RED,   chars)
            self.bullish_zip = lambda chars: zip(len(chars) * T_GREEN, chars)
        elif colors.NUM_COLORS == 0:
            self.bearish     = self.bullish     = lambda c: c
            self.bearish_zip = self.bullish_zip = lambda chars: chars
        else:
            self.bearish = bearish
            self.bullish = bullish
            self.spacish = spacish(space)
            self.bearish_zip = lambda chars: (self.bearish(c) for c in chars)
            self.bullish_zip = lambda chars: (self.bullish(c) for c in chars)

        if shapes is not MonoShapes and self.color_mode == modes.URWID and self.pab:
            self.barcolor = lambda ohlc: (self.price_action_barcolor(ohlc),)
        else:
            self.barcolor = None

    def fill(self, ohlc:Ohlc, height, scale=1.0, offset=0.0):
        if height <= 0: return []
        if self.heikin: ohlc = ohlc.heikin()
        params = _fill_params(ohlc, scale, offset)
        chars = self._fill(params, height)
        return self.colorize(chars, params)

    def colorize(self, chars, params:FillParams):
        if self.barcolor:
            return zip(len(chars) * self.barcolor(params.ohlc), chars)
        if params.o <= params.c: return self.bullish_zip(list(chars))
        else:                    return self.bearish_zip(list(chars))

    def _simple_fill(self, params:FillParams, height):
        o,h,l,c,top,bot,oc,lh,_ = params

        if o <= c: fill, spikes = self.bulls
        else:      fill, spikes = self.bears
        space = self.space
        spike = spikes[1]

        i = height
        res = []
        while i > h:   res.append(space); i -= 1
        while i > top: res.append(spike); i -= 1
        while i > bot: res.append(fill);  i -= 1
        if len(res) > 0 and res[-1] != fill: res[-1] = fill
        while i > l:   res.append(spike); i -= 1
        while i > 0:   res.append(space); i -= 1
        assert len(res) == height
        return res

    def _thin_fill(self, params:FillParams, height):
        o,h,l,c,top,bot,oc,lh,_ = params

        res = []
        cell  = []
        space = self.space
        h,l,top,bot = [int(3 * v) for v in [h,l,top,bot]]
        filled = False
        for i in range(3 * height, 0, -1):
            if   top >= i >= bot: cell.append(2); filled = True
            elif h   >= i >= l:   cell.append(1)
            else:                 cell.append(0)
            if len(cell) == 3:
                if not filled and (i <= top or i == 1):
                    if sum(cell) == 3: cell = (1,2,1)
                    elif cell[0] == 1: cell[0] = 2
                    elif cell[2] == 1: cell[2] = 2
                    else:              cell[1] = 2
                    filled = True
                if sum(cell) == 0: res.append(space)
                else:              res.append(THINS[tuple(cell)])
                cell = []
        return res

    def _complex_fill(self, params:FillParams, height):
        o,h,l,c,top,bot,oc,lh,_ = params

        cell  = []
        cells = []
        zero  = (0,0,0)
        l_skip = h_skip = 0
        h,l,top,bot = [int(3 * v) for v in [h,l,top,bot]]
        for i in range(3 * height, 0, -1):
            if   top >= i >= bot: cell.append(2)
            elif h   >= i >= l:   cell.append(1)
            else:                 cell.append(0)
            if len(cell) == 3:
                if sum(cell) == 0:
                    if len(cells) == 0: h_skip += 1
                    else:               l_skip += 1
                else:
                    cells.append(tuple(cell))
                cell = []

        res = []
        if len(cells) == 1:
            res.append(SINGLES[cells[0]])
        elif len(cells) == 2:
            c0, c1 = cells[0], cells[1]
            h0, f1 = HEADS[c0], FEET[c1]
            # if h0 not in SINGLE_VALUES or f1 not in SINGLE_VALUES:
            #     if sum(c0) >= sum(c1): h0 = SINGLES[c0]
            #     else:                  f1 = SINGLES[c1]
            res += [h0, f1]
        elif len(cells) > 1:
            last = len(cells) - 1
            for i in range(len(cells)):
                if i == 0:    prev = zero
                else:         prev = cells[i-1]
                if i == last: nex = zero
                else:         nex = cells[i+1]
                cell = cells[i]
                if prev[2] != 0 and nex[0] != 0:
                    res.append(MIDS[cell])
                elif nex[0] != 0 or cell[0] == 0:
                    res.append(HEADS[cell])
                elif prev[2] != 0 or cell[2] == 0:
                    res.append(FEET[cell])
                else:
                    res.append(SINGLES[cell])

        c_zero = SINGLES[zero]
        res = h_skip * [c_zero] + res + l_skip * [c_zero]

        msg = "\n".join([str(cells), str(res)])
        assert len(res) == height, "invalid height: {} != {}\n{}".format(len(res), height, msg)
        return res

CharsConfig = namedtuple('CharsConfig', 'heads mids feet singles thins fulls')

def DefaultCharsConfig():
    # _, I, B = 0, 1, 2
    log.debug("_setup_fills")

    # table to map sector spec to screen characters,
    # space marks empty sectors, X marks invalid combinations
    #           bars        spikes      hammers   complete        invalid
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    heads   = "     ╻   ▉       ╷   │       ┯ ╽   │ ┿ ┿ ╽ ▉ ▉ ▉   X X X X X "
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    mids    = "                                   │ ╿ ┿ ╽ ▉ ▉ ▉   X X X X X "
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    feet    = " ╹     ▉     ╵     │     ╿ ┷       │ ╿ ┿ ┿ ▉ ▉ ▉   X X X X X "
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    singles = " ▔ ▬ ▁ ┷ ┯   ▔ ▬ ▁ ┷ ┯   ▔ ┷ ┯ ▁   ┼ ┿ ┿ ┿ ▉ ▉ ▉   X X X X X "
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    thins   = " ╹ ▮ ╻ ╹ ╻   ╵ ▫ ╷ ╵ ╷   ╹ ┷ ┯ ╻   │ ╿ ┿ ╽ ╿ ╽ ┃   X X X X X "
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    fulls   = " ▔ ▬ ▁ █ ▆   ╵ ▬ ╷ │ │   │ ┿ ┿ │   │ │ ┿ │ █ █ █   X X X X X "
    #           –––––––––   –––––––––   –––––––   –––––––––––––   ––––––––––
    p0      = " #     #     |     |     # |       | # | | # | #   # | # | # "
    p1      = "   #   # #     |   | |   | # # |   | | # | # # #           | "
    p2      = "     #   #       |   |       | #   | | | # | # #   # # | | # "

    lines = [heads, mids, feet, singles, fulls, thins, p0, p1, p2]
    chars = 3 * [3 * [3 * ['E']]]           # setup three-dim empty fill matrix (copy-by-ref)
    chars = json.loads(json.dumps(chars))   # materialize matrix (emulate copy-by-value)
    syms  = tuple(' |#')                    # names of the matrix keys (fill representaton)
    idx = {s:i for i,s in enumerate(syms)}  # however, we better use real ints for lookup
    debug("syms:", syms)
    debug("idx:", idx)
    candle_fulls = {}
    candle_thins = {}
    candle_heads = {}
    candle_mids  = {}
    candle_feet  = {}
    candle_singles = {}
    for head, mid, foot, single, full, thin, a, b, c in zip(*lines):  # transpose rows to cols
        i,j,k = idx[a], idx[b], idx[c]      # compute int index values
        chars[i][j][k]          = single    # overwrite 'E' in chars cube with actual char
        candle_heads[(i,j,k)]   = head
        candle_mids[(i,j,k)]    = mid
        candle_feet[(i,j,k)]    = foot
        candle_singles[(i,j,k)] = single
        candle_fulls[(i,j,k)]   = full
        candle_thins[(i,j,k)]   = thin
        if single != ' ': debug("adding:", [(i,j,k),(a,b,c),head,mid,foot,full,thin])

    if 'E' in str(chars): raise ValueError("missing render combination")

    def test(t,m,b):
        t,m,b = [tuple(int(v) for v in d) for d in [t,m,b]]
        hmf = [candle_heads[t], candle_mids[m], candle_feet[b]]
        thn = [candle_thins[t], candle_thins[m], candle_thins[b]]
        ful = [candle_fulls[t], candle_fulls[m], candle_fulls[b]]
        debug("\n".join(" ".join(l) for l in zip(hmf,thn,ful)))

    debug("test cells:")
    test("000","111","222")
    test("222","111","000")
    test("222","222","111")
    test("111","222","222")
    test("111","121","111")
    test("112","222","211")
    test("122","222","221")

    return CharsConfig(candle_heads, candle_mids, candle_feet, candle_singles, candle_fulls, candle_thins)

CHARS = DefaultCharsConfig()
HEADS, MIDS, FEET, SINGLES, FULLS, THINS = CHARS  # type: dict, dict, dict, dict, dict, dict, CharsConfig

HEAD_VALUES   = tuple(set(HEADS.values()))
MID_VALUES    = tuple(set(MIDS.values()))
FOOT_VALUES   = tuple(set(FEET.values()))
SINGLE_VALUES = tuple(set(SINGLES.values()))


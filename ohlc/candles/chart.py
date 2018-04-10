# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys
from ohlc import colors
from ohlc.colors import modes
from ohlc.candles import fills
from ohlc.types import Ohlc
from collections import namedtuple

try:                from shutil import get_terminal_size
except ImportError: from shutil_backports import get_terminal_size

IS_PY2 = sys.version_info.major < 3

_DEBUG = os.environ.get('DEBUG','') != '' or '--debug' in sys.argv

BoxChars = namedtuple("BoxChars", "top mid bot")
LineBox = BoxChars(top="┌─┐",
                   mid="│ │",
                   bot="└─┘")

LEFT   = 'left'
RIGHT  = 'right'
TOP    = 'top'
BOTTOM = 'bottom'
BOX    = 'box'

class Layout(namedtuple('Layout', 'canvas x_axis y_axis info')): pass

class Size():
    def __init__(self, h, w):
        self.h = max(0, int(h))
        self.w = max(0, int(w))

    def __repr__(self): return "Size(h={}, w={})".format(self.h, self.w)

class LineStore():
    width = 0
    height = 0
    def __init__(self, *, color_mode=modes.SHELL):
        self.color_mode = color_mode
        self.debug_lines = []
        self._lines = []
        self._cache = []
        self._dirty = True

    @property
    def urwid(self): return self.color_mode == modes.URWID

    @property
    def lines(self): return self._lines[:]
    @lines.setter
    def lines(self, lines):
        self._lines = lines[:]; self._dirty = True

    def invalidate(self): self._dirty = True

    def debug(self, *args):
        lines = [str(a) for a in args]
        self.debug_lines = lines

    def format(self):
        if self.urwid:
            for line in self.lines:
                yield self.urwid_line(line)
        else:
            for line in self.lines:
                res = self.format_line(line)
                yield res

    def urwid_line(self, line):
        if   type(line) is str:   return [line]
        elif type(line) is tuple: return list(line)
        elif type(line) is list:  return line
        else:                     return [str(line)]

    def format_line(self, line):
        if   type(line) is str:   return line
        elif type(line) is tuple: return "".join(line)  # assuming raw string tuple
        elif type(line) is list:  return "".join(self.format_line(s) for s in line)
        else:                     return str(line)

    def print_lines(self):
        if self._dirty:
            self._cache = list(self.format())
            self._dirty = False
        for l in self._cache: print(l)

    def resize(self, size:Size) -> bool:
        h = size.h; w = size.w
        if self.height != h or self.width != w:
            self.height = h
            self.width  = w
            self.invalidate()
            self.redraw()
            return True
        return False

    def redraw(self): pass

class CandleCanvas(LineStore):
    show_labels = False
    _candles_dirty = False
    visible_ohlc = None
    cache_size = 10000
    def __init__(self, *, h=0, w=0, color_mode=modes.SHELL, **fill_args):
        self.height = h
        self.width = w
        self.candles = []
        self.data = []
        self.filler = fills.Filler(color_mode=color_mode, **fill_args)
        super().__init__(color_mode=color_mode)

    @property
    def visible_cols(self): return max(0,int(self.width))
    @property
    def visible_data(self):
        n = self.visible_cols
        if n > 0: return self.data[-self.visible_cols:]
        else:     return []
    @property
    def left_ohlc(self):
        i = self.visible_cols
        if len(self.data) > i: return self.data[-i]
        else:                  return self.data[0]
    @property
    def right_ohlc(self): return self.data[-1]
    @property
    def last_clipped_ohlc(self):
        i = self.visible_cols + 1
        if len(self.data) > i: return self.data[-i]
        else:                  return self.left_ohlc

    def canvas_lines(self):
        pad = max(0, self.visible_cols - len(self.candles))
        for line in zip(*self.candles[-self.visible_cols:]):
            yield line + (" " * pad,)

    def requires_redraw(self):
        b = self.visible_ohlc
        return (b is None or self._dirty or
                not b.includes(self.left_ohlc) or
                not b.includes(self.right_ohlc) or
                b.touches(self.last_clipped_ohlc))

    def draw_candles(self, data):
        if len(data) == 0: return []
        tup = self.visible_ohlc
        height = self.height
        scale = float(height) / tup.spread(Ohlc.ZERO)
        return (self.filler.fill(d, height=height, scale=scale, offset=-tup.low)
                for d in data)

    def visible_scale(self):
        tup = self.visible_ohlc
        return (tup.high - tup.low) / self.height

    def add_ohlc(self, ohlc:Ohlc):
        while len(self.data) > self.cache_size:  del self.data[0]
        while len(self.candles) > self.visible_cols + 2: del self.candles[0]
        self.data.append(ohlc)
        self.redraw_candles(last_ohlc=-1)

    def redraw_candles(self, last_ohlc=None):
        if self.requires_redraw():
            self.visible_ohlc = Ohlc.from_ohlc_list(self.visible_data)
            self.candles = list(self.draw_candles(self.visible_data))
        elif last_ohlc is not None:
            ohlc = self.data[last_ohlc]
            self.candles = self.candles + list(self.draw_candles([ohlc]))
        self._candles_dirty = False

    def reset(self):
        self.data = []
        self.candles = []
        self.visible_ohlc = None
        self._candles_dirty = True
        self.redraw()

    def resize(self, size:Size):
        if super().resize(size):
            self._candles_dirty = True
            self.redraw()

    def redraw(self):
        self.redraw_candles()
        lines = list(self.canvas_lines())
        if self.show_labels:
            label_line = "".join("{: <3.0f}".format(t.high) for t in self.visible_data)
            lines[-1] = "".join(r if r != " " else l
                                for l, r in zip(lines[-1], label_line))
        if _DEBUG:
            self.debug(
                "──" * self.visible_cols,
                dict(data=len(self.data),
                     vis=len(self.visible_data),
                     candles=len(self.candles),
                     lines=len(lines),
                     width=self.width,
                     height=self.height),
                "ohlc:      " + str(self.visible_ohlc),
                "candle 1:  " + str((self.candles + [None])[0]),
                "line 1:    " + str((lines + [None])[0]),
            )

        while len(lines) < self.height: lines.append(" " * self.width)

        if self.filler.color_mode == modes.SHELL:
            lines = [(colors.SH_BG_GRAY,) + tuple(line) + (colors.SH_END,) for line in lines]

        self.lines = lines

class Axis(LineStore):
    H = 'horizontal'
    V = 'vertical'
    _tix = ('└┴─┘',  # top axis
            '┐┌',    # left axis and
            '┤├',    # right axis
            '││',
            '┘└',
            '┌┬─┐',  # bottom axis
            '–-––')  # plain axis

    Tix = tuple(_tix[0])
    Bix = tuple(_tix[5])
    Lix, Rix = list(zip(*_tix[1:5]))
    Nix = tuple(_tix[6])

    def __init__(self, canvas, skip=1, side=BOTTOM, numbers=True, **ls_args):
        self.skip = skip
        self.side = side
        self.numbers = numbers
        self.canvas = canvas
        if   side == TOP:    self.dir = self.H; self.ticks = self.Tix
        elif side == LEFT:   self.dir = self.V; self.ticks = self.Lix
        elif side == RIGHT:  self.dir = self.V; self.ticks = self.Rix
        elif side == BOTTOM: self.dir = self.H; self.ticks = self.Bix
        else:                self.dir = self.H; self.ticks = self.Nix
        super().__init__(**ls_args)

    def redraw(self):
        w_tick = self.skip + 1
        width  = self.width
        height = self.height

        l, tick, plain, r = self.ticks

        if self.dir == self.H:
            n = self.canvas.width - int(w_tick / 2)
            m = int(n / w_tick)
        else:
            n = self.canvas.height - 1
            m = int(n / w_tick)

        mw   = m * w_tick
        rest = n - mw
        edge = self.skip * plain

        if self.dir == self.H and rest > 1:
            r = tick + rest * plain

        ticks = [l + edge] + [tick + edge] * (m - 1) + [r]
        debug = []

        line_fmt  = "{: <" + str(width) + "}"
        htick_fmt = "{: <" + str(w_tick) + "}"

        w2 = str(max(0, width - 2))
        if self.side == RIGHT: vtick_fmt = "{1} {0: <" + w2 + ".02f}"
        else:                  vtick_fmt = "{0: >" + w2 + ".02f} {1}"

        if self.numbers:
            if self.dir == self.V:
                tup = self.canvas.visible_ohlc
                if tup is None:
                    high = m; dv = 1
                else:
                    high = tup.high; dv = (high - tup.low) / max(1, len(ticks))
                ticks = [vtick_fmt.format(high - dv * i, s) for i, s in enumerate(ticks)]
                if _DEBUG and len(ticks) > 0:
                    ticks[0] = vtick_fmt.format(float(width), "W")
                labels = []
            else:
                labels = [htick_fmt.format(i) for i, t in enumerate(ticks)]
                if _DEBUG and len(labels) > 0:
                    labels[0] = htick_fmt.format(str(height) + "H")
                debug.append(str(dict(n=n, m=m, mw=mw, rest=rest)))

        if self.dir == self.H:
            ticks = [line_fmt.format("".join(ticks))]
            if len(labels) > 0:  labels = [line_fmt.format("".join(labels))[:width]]
            else:                labels = []
            if self.side == TOP: lines = labels + ticks
            else:                lines = ticks + labels
        else:
            lines = ticks

        self.debug(*debug)
        self.lines = lines

class TextBox(LineStore):
    def __init__(self, text, *, w=0, h=0, **ls_args):
        self.text = text
        self.height = h
        self.width = w
        super().__init__(**ls_args)

    def redraw(self):
        raw_lines = self.text.split('\n')
        w_max = int(self.width)
        h     = int(self.height)
        fmt = '{: ^' + str(w_max) + 's}'
        lines = []
        for raw_line in raw_lines:
            if len(lines) >= h: break
            words = raw_line.split(' ')
            line = ''
            for word in words:
                if len(lines) >= h: break
                if len(word) > w_max: word = word[:w_max]
                # word fixed, now add it to the lines
                l = len(line); w = len(word)
                if   l == 0:             line = word               # set first word
                elif l + w + 1 <= w_max: line += " " + word        # add another word
                else: lines.append(fmt.format(line)); line = word  # break line
            if len(lines) < h: lines.append(fmt.format(line))      # add remainder
        while len(lines) < h: lines.append(fmt.format(""))     # fill to bottom
        self.lines = lines


class CandleChart(LineStore):
    canvas = None
    x_axis = None
    y_axis = None
    info   = None
    def __init__(self, *, h=None, w=None, border=BOX,
                 color_mode=modes.SHELL, fill_mode=fills.THIN,
                 heikin=False, pab=False, **ls_args):
        ts = get_terminal_size()
        if w is None: w = ts.columns
        if h is None: h = ts.lines - 1
        self.width  = int(w)
        self.height = int(h)
        self.border = border
        self.canvas = CandleCanvas(color_mode=color_mode, fill_mode=fill_mode,
                                   heikin=heikin, pab=pab)
        self.x_axis = Axis(self.canvas, side=BOTTOM, skip=5, color_mode=color_mode)
        self.y_axis = Axis(self.canvas, side=RIGHT, skip=0, color_mode=color_mode)
        self.info = TextBox("CANDLES ROCK!", color_mode=color_mode)
        super().__init__(color_mode=color_mode, **ls_args)
        self.resize(h=h, w=w)

    def add_ohlc(self, ohlc:Ohlc):
        self.canvas.add_ohlc(ohlc)
        self.x_axis.redraw()
        self.y_axis.redraw()
        self.canvas.redraw()
        o = self.canvas.visible_ohlc
        self.info.text = "max:{:2.2f}\nlast:{:2.2f}".format(o.high, o.close)
        self.info.redraw()

    def compute_border_chars(self, w):
        if self.border:
            l, m, r = LineBox.top
            top = l + m * w + r
            l, m, r = LineBox.bot
            bot = l + m * w + r
            l, _, r = LineBox.mid
        else:
            l = r = top = bot = ''

        if self.urwid:
            l,r,top,bot = [[] if v == '' else [('default',v)]
                           for v in [l,r,top,bot]]

        return l,r,top,bot

    def format(self):
        l,r,top,bot = self.border_chars
        c_lines = list(self.canvas.format())
        y_lines = list(self.y_axis.format())
        x_lines = list(self.x_axis.format())
        i_lines = list(self.info.format())
        top_lines = zip(y_lines, c_lines)
        bot_lines = zip(i_lines, x_lines)

        if self.border: yield top
        for y, c in top_lines: yield l + c + y + r
        for i, x in bot_lines: yield l + x + i + r
        if self.border: yield bot
        # if _DEBUG: yield self.layout

    def print_lines(self):
        for l in self.format(): print(l)

    def reset(self):  self.canvas.reset()
    def redraw(self): self.canvas.redraw()

    @property
    def layout(self) -> Layout:
        h = self.height; w = self.width
        if self.border == BOX:
            h -= 2
            w -= 2
        l = Layout(Size(h - 2, w - 12),  # canvas
                   Size(2,     w - 12),  # x_axis
                   Size(h - 2, 12),      # y_axis
                   Size(2,     12))      # info
        return l

    def resize(self, *, h=None, w=None):
        if h is None: h = self.height
        if w is None: w = self.width
        super().resize(Size(h,w))
        self.border_chars = self.compute_border_chars(self.width - 2)
        l = self.layout
        if self.canvas is not None: self.canvas.resize(l.canvas)
        if self.x_axis is not None: self.x_axis.resize(l.x_axis)
        if self.y_axis is not None: self.y_axis.resize(l.y_axis)
        if self.info   is not None: self.info.resize(l.info)


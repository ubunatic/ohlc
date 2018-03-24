import time, asyncio, os, traceback, sys
import widdy
from ohlc.candles import fills
from ohlc import colors
from ohlc.colors import modes
from ohlc.candles.candle import CandleChart
from ohlc.types import Ohlc
from ohlc.random import random_ohlc_generator

palette = [
    (colors.OK,       'dark green',      'black'),
    (colors.ERR,      'light red',       'black'),

    (colors.BULL,      'dark green',      'black'),
    (colors.BEAR,      'light red',       'black'),
    (colors.BULL_INV,  'black',           'dark green'),
    (colors.BEAR_INV,  'black',           'light red'),

    (colors.SPACE,     'black',           'black', '', 'g19',             'g19'),
    (colors.GREEN,     'dark green,bold', 'black', '', 'dark green,bold', 'g19'),
    (colors.RED,       'dark red,bold',   'black', '', 'dark red,bold',   'g19'),

    (colors.LIME,    'light green',  'black', '', '#0f0', 'g19'),
    (colors.RED,     'dark red',     'black', '', '#f00', 'g19'),
    (colors.FUCHSIA, 'dark magenta', 'black', '', '#f0f', 'g19'),
    (colors.AQUA,    'dark cyan',    'black', '', '#0ff', 'g19'),
    (colors.YELLOW,  'yellow',       'black', '', '#ff0', 'g19'),
    (colors.ORANGE,  'brown',        'black', '', '#f80', 'g19'),
    (colors.GREEN,   'dark green',   'black', '', '#080', 'g19'),
]

class DataSource:
    def __init__(self, data_gen, data_rate=10.0, sink=None):
        self.data_gen = data_gen
        self.data_rate = data_rate
        self.data_task = None
        self.paused = True
        self.sink = sink

    def pause(self):
        t = self.data_task
        if t is not None: t.cancel()
        self.paused = True

    def unpause(self):
        self.pause()  # stop old task first
        self.data_task = asyncio.Task(self.data_loop())
        # Nothing more to do here, we just start the task. Urwid already started
        # the event loop and we do not need to wait for any completon here.

    def next(self):
        if self.data_gen is None: return None
        return next(self.data_gen)

    async def data_loop(self):
        if self.sink is None: raise ValueError("cannot start data_loop without data sink")
        self.paused = False
        while not self.paused:
            await asyncio.sleep(self.data_rate)
            self.sink.send(self.next())

def random_source(**source_args):
    gen = random_ohlc_generator(v_start=20.0, v_min=10.0, v_max=100.0)
    return DataSource(gen, **source_args)

class CandleApp(widdy.App):
    def __init__(self, source, **chart_args):
        chart_args['border'] = None
        self.chart = CandleChart(**chart_args)
        t, self.update_text = widdy.Text('loading candles...')
        box = widdy.LineBox(t)
        menu = widdy.Menu(
            ('R', colors.OK, 'next ohlc'),
            ('H', colors.OK, 'cycle height'),
            ('W', colors.OK, 'cycle width'),
            ('P', colors.OK, 'play/pause'),
        )
        frame = widdy.Frame(widdy.Header("Candles"), box, menu)
        handlers = widdy.Handlers(
            ('R', self.next_candle),
            ('H', self.resize_height),
            ('W', self.resize_width),
            ('P', self.toggle_pause),
        )
        self.paused = True
        self.source = source
        self.source.sink = self
        super().__init__(frame, handlers=handlers, pal=palette)
        if colors.NUM_COLORS > 0:
            self.screen.set_terminal_properties(colors=colors.NUM_COLORS)

    def resize_height(self):
        x,y = self.screen_size
        h = self.chart.height
        h_max = y - 5
        if h >= h_max: h = 5
        else:          h = min(h_max, int(h * 1.2))
        self.chart.resize(h=h)

    def resize_width(self):
        x,y = self.screen_size
        w = self.chart.width
        w_max = x - 3
        if w >= w_max: w = 20
        else:          w = min(w_max, int(w * 1.2))
        self.chart.resize(w=w)

    def toggle_pause(self):
        if self.source.paused: self.source.unpause()
        else:                  self.source.pause()

    def next_candle(self): self.send(self.source.next())

    def send(self, ohlc:Ohlc):
        try:
            if ohlc is not None: self.chart.add_ohlc(ohlc)
            lines = list(self.chart.format())
            if len(lines) > 0:
                l = lines[0]
                if type(l) is str:
                    raise ValueError("first line is str, expected list, please use urwid render mode")
            self.update_text(list(s + [('','\n')] for s in lines))
        except:
            print(traceback.format_exc())


def main():
    source = random_source(data_rate=0.04)
    app = CandleApp(source, w=60, h=15, color_mode=modes.URWID, heikin=True)
    app.run()

if __name__ == '__main__': main()

import time, sys, traceback, logging  # noqa
import widdy
from ohlc import colors, cli
from ohlc.colors import modes
from ohlc.candles import chart
from ohlc.types import Ohlc
from ohlc.random import random_ohlc_generator
from threading import Thread  # noqa

log = logging.getLogger(__name__)

palette = [
    (colors.OK,        'dark green',      'black'),
    (colors.ERR,       'light red',       'black'),

    (colors.BULL,      'dark green',      'black'),
    (colors.BEAR,      'light red',       'black'),
    (colors.BULL_INV,  'black',           'dark green'),
    (colors.BEAR_INV,  'black',           'light red'),

    (colors.SPACE,     'black',           'black', '', 'g19',             'g19'),
    (colors.GREEN,     'dark green,bold', 'black', '', 'dark green,bold', 'g19'),
    (colors.RED,       'dark red,bold',   'black', '', 'dark red,bold',   'g19'),

    (colors.LIME,      'light green',     'black', '', '#0f0', 'g19'),
    (colors.RED,       'dark red',        'black', '', '#f00', 'g19'),
    (colors.FUCHSIA,   'dark magenta',    'black', '', '#f0f', 'g19'),
    (colors.AQUA,      'dark cyan',       'black', '', '#0ff', 'g19'),
    (colors.YELLOW,    'yellow',          'black', '', '#ff0', 'g19'),
    (colors.ORANGE,    'brown',           'black', '', '#f80', 'g19'),
    (colors.GREEN,     'dark green',      'black', '', '#080', 'g19'),
]

class DataSource:
    def __init__(self, source_gen, data_rate=1.0, sink=None):
        """DataSource allows to setup a managed pausable data pipeline.
        After calling `unpause`, you can `send` data to it, which it forwards to `sink.send`.
        You must provide a `sink` in this case. Alternatively, instead of sending data,
        you can also call `next` to get the next value from the original `source_gen` if given.
        You can call `pause` and `unpause` to stop/restart the pipeline.

        Note that a sender should check the `paused` before calling `send` and that the
        DataSource always starts in `paused` mode. Calling `next` is independed of pausing.

        To avoid the `paused` check and having to sleep in external code,
        you can provide a `on_unpause` callback.
        """
        self.source_gen = source_gen
        self.data_rate = data_rate
        self.thread = None
        self.paused = True
        self.sink = sink

    def pause(self):
        if self.paused: return
        self.paused = True
        t = self.thread
        t.join()
        self.thread = None

    def unpause(self):
        self.pause()
        self.thread = t = Thread(target=self.loop)
        t.daemon = True
        t.start()

    def next(self):
        """next tries to fetch the next value from the source generator.
        Use `next` to bypass the `loop` and directly read values from the `source_gen`,
        e.g., when paused. If all data is consumed, `next` raises `StopIteration`.
        """
        if self.source_gen is None: raise StopIteration
        return next(self.source_gen)

    def read(self, num_records=float('inf'), max_time=float('inf')):
        """read the datasource and return a list of records up to the end of the source
        or up to the defined `num_records` or for a defined `max_time`.
        """
        if self.source_gen is None: return []
        data = []; n = 0; t0 = time.time()
        for s in self.source_gen:
            if time.time() - t0 > max_time: break
            if n >= num_records:            break
            n += 1
            data.append(s)
        return data

    def loop(self):
        """loop runs fetches and forwards data until the DataSource is paused."""
        if self.sink is None: raise ValueError("cannot start data loop without data sink")
        self.paused = False
        t = self.thread
        while not self.paused:
            if t is not self.thread:
                log.warn("found new data thread, stopping current"); break
            try:
                v = next(self.source_gen)
                self.sink.send(v)
                if self.data_rate != 0: time.sleep(1.0 / float(self.data_rate))
            except StopIteration: break

def random_source(data_rate=1.0, count=0, **source_args):
    if count == 0: count = float('inf')
    rgen = random_ohlc_generator(v_start=20.0, v_min=10.0, v_max=100.0, count=count)
    source = DataSource(rgen, data_rate=data_rate)
    return source

class CandleApp(widdy.App):
    def __init__(self, source, title='Candles', **chart_args):
        chart_args['border'] = None
        self.chart = chart.CandleChart(**chart_args)
        t, self.update_text = widdy.Text('loading candles...')
        box = widdy.LineBox(t)
        menu = widdy.Menu(
            ('R', colors.OK, 'next ohlc'),
            ('H', colors.OK, 'cycle height'),
            ('W', colors.OK, 'cycle width'),
            ('P', colors.OK, 'play/pause'),
        )
        frame = widdy.Frame(widdy.Header(str(title)), box, menu)
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
            try: self.screen.set_terminal_properties(colors=colors.NUM_COLORS)
            except KeyError: log.warn("failed to set NUM_COLORS")

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
            log.error("faild to add ohlc value: %s", traceback.format_exc())

STDIN_NAMES = ['/dev/stdin', '-', '', None]

def main():
    from ohlc.input import input_gen

    p = cli.ArgumentParser().with_input().with_debug().with_logging().with_version()
    p.flag('--random',                help='test candlesticks with random values')
    p.flag('--pab',                   help='use PriceActionBars colors')
    p.flag('--ha',                    help='use heikin-ashi candles')
    p.flag('--interactive',     '-i', help='show interactive chart',    dest='interactive', default=True)
    p.flag('--non-interactive', '-n', help='print chart only and exit', dest='interactive', action='store_false')
    p.opti('--title',  '-T',          help='title of the chart', default=None)
    p.opti('--width',  '-W',          help='width of the non-interactive chart',  default=None, type=int)
    p.opti('--height', '-H',          help='height of the non-interactive chart', default=None, type=int)
    args = p.parse_args()

    if args.random: source = random_source(data_rate=10.0)
    else:           source = DataSource(input_gen([args.input]), data_rate=0)

    # TODO: add support for resizing, i.e., dymanic size
    ts = chart.get_terminal_size()
    w = ts.columns - 4
    h = min(30, ts.lines - 4)

    if not args.interactive:
        w = args.width or w
        h = args.height or h
        c = chart.CandleChart(w=w, h=h, color_mode=modes.SHELL)
        # read records for at most 1s from a potentially infinite data source
        data = source.read(max_time=1)
        data = data[-w:]
        for s in data: c.add_ohlc(s)
        c.print_lines()
    else:
        if args.input in STDIN_NAMES and not args.random:
            raise ValueError("cannot read from stdin in interactive app")
        app = CandleApp(source, w=w, h=h, color_mode=modes.URWID,
                        heikin=args.ha, pab=args.pab, title=args.title)
        app.run()


if __name__ == '__main__': main()

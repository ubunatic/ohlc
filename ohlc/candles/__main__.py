import sys, urwid
from ohlc.candles.app import CandleApp, random_source
from ohlc.colors import modes

def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print('run with --debug to enable debug output')
        return
    source = random_source(data_rate=0.04)
    app = CandleApp(source, w=60, h=15, color_mode=modes.URWID, heikin=True)
    app.run()

main()

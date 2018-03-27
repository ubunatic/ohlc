import fileinput, logging
from ohlc.types import Ohlc
from ohlc import cli
from typing import List  # noqa

log = logging.getLogger(__name__)

class OhlcInput(fileinput.FileInput):
    prev = None
    def __init__(o, *args, **kwargs):
        o.values = []   # type:List # list of pending values from the last line
        super().__init__(*args, **kwargs)

    def __next__(o):
        log.debug("reading next line")
        line = super().__next__().strip().split(" ")
        values = [float(v) for v in line]
        o.prev = res = Ohlc.from_values(values, prev=o.prev)
        return res

def input_gen(*args, **kwargs):
    with OhlcInput(*args, **kwargs) as f:
        for val in f: yield val

def main():
    p = cli.ArgumentParser().with_logging().with_debug().with_input()
    args = p.parse_args()
    for v in input_gen([args.input]): print(v)

if __name__ == '__main__': main()

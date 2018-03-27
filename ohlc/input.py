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
        log.debug("OhlcInput initalized, files:%s", o._files)

    def __next__(o):
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
    for o in input_gen([args.input]): print(o.format())

if __name__ == '__main__': main()

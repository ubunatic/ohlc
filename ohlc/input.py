import fileinput, logging
from ohlc.types import Ohlc
from ohlc import cli
from typing import List  # noqa
from contextlib import contextmanager

log = logging.getLogger(__name__)

@contextmanager
def OhlcInput(*args, **kwargs):
    fi = fileinput.FileInput(*args, **kwargs)
    log.debug("OhlcInput initalized, files:%s", fi._files)
    def ohlc_gen():
        prev = None
        values = []  # type:List[float]
        for line in fi:
            line = line.strip().split(" ")
            values = [float(v) for v in line]
            prev = res = Ohlc.from_values(values, prev=prev)
            yield res
    yield ohlc_gen()

def input_gen(*args, **kwargs):
    with OhlcInput(*args, **kwargs) as f:
        for val in f: yield val

def main():
    p = cli.ArgumentParser().with_logging().with_debug().with_input()
    args = p.parse_args()
    for o in input_gen([args.input]): print(o.format())

if __name__ == '__main__': main()

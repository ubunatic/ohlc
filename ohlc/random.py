import time
from random import random as _rand
from ohlc.types import ZERO, Ohlc
from ohlc import cli

def random_values_generator(*, v_start=0.1, count=float('inf'), amp=0.2, v_min=None, v_max=None):
    if 0.0 in [v_start, v_min, v_max]:
        raise ValueError('start, min, and max values cannot be zero')
    v_start = float(v_start)
    if v_min is None: v_min = v_start / 10
    if v_max is None: v_max = v_start * 10
    v_min, v_max = float(v_min), float(v_max)
    if not v_min <= v_start <= v_max:
        raise ValueError('start not between min and max values')
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

def main():
    p = cli.ArgumentParser().with_debug().with_logging()
    p.opti('--data_rate', '-r', help='number of ohlc values per second', default=10, type=int)
    args = p.parse_args()  # noqa
    gen = random_ohlc_generator()
    delay = 1.0 / float(args.data_rate)
    for o in gen:
        print(o.format())
        time.sleep(delay)

import argparse, logging  # noqa

log = logging.getLogger(__name__)

def setup_logging(args):
    if getattr(args,'debug', False): level = logging.DEBUG
    else:                            level = logging.INFO
    log.debug('setup logging')
    logging.basicConfig(level=level)

class ArgumentParser(argparse.ArgumentParser):
    defers = ()
    def with_debug(p):
        p.add_argument('--debug', help='enable debug log', action='store_true')
        return p
    def with_input(p):
        p.add_argument('input', help='input file descriptor', default='-', nargs='?')
        return p
    def with_logging(p):
        p.defers += (p.setup_logging,)
        return p

    def setup_logging(p):
        args, _ = super().parse_known_args()
        setup_logging(args)

    def parse_args(p, *args, **kwargs):
        res = super().parse_args(*args, **kwargs)
        for fn in p.defers: fn()
        return res

    def parse_known_args(p, *args, **kwargs):
        res = super().parse_known_args(*args, **kwargs)
        for fn in p.defers: fn()
        return res

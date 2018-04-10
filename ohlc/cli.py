# flake8: noqa: F401
import argparse, logging, sys

log = logging.getLogger(__name__)

def setup_logging(args):
    """setup_logging checks the given arg for the "default" flag and sets up logging"""
    if getattr(args,'debug', False): level = logging.DEBUG
    else:                            level = logging.INFO
    log.debug('setup logging')
    logging.basicConfig(level=level)

class ArgumentParser(argparse.ArgumentParser):
    callbacks = None
    opti = argparse.ArgumentParser.add_argument       # short name for add_argument

    def flag(p, flag, *args, **kwargs):
        """flag create command line flag that does not take additional value parameters"""
        if 'action' not in kwargs:
            kwargs['action'] = 'store_true'           # make the option a flag
        return p.add_argument(flag, *args, **kwargs)  # passthrough any other args

    def with_debug(p):
        """with_debug adds a --debug flag"""
        p.add_argument('--debug', help='enable debug log', action='store_true')
        return p

    def with_version(p):
        """with_version adds a --version flag"""
        p.add_argument('--version', help='show version info', action='store_true')
        # p.add_parse_callback(p.show_version)
        return p

    def with_input(p, default='-', nargs='?', help='input file descriptor', **argparse_args):
        """with_input adds a positional optional "input" argument"""
        p.add_argument('input', help=help, default=default, nargs=nargs, **argparse_args)
        return p

    def with_logging(p):
        """with_logging make the parser setup logging after parsing input args"""
        p.add_parse_callback(p.setup_logging)
        return p

    def setup_logging(p):
        """setup_logging reads the current args and sets up logging"""
        args, _ = p.parse_known_args()
        setup_logging(args)

    def show_version(p):
        args, _ = p.parse_known_args()
        if args.version:
            py  = sys.version.split('\n')[0]
            ver = '0.0.0'
            sys.stdout.write('{} {}\n'.format(ver, py))
            sys.exit(0)

    def add_parse_callback(p, fn):
        """add_parse_callback adds the given callbacks which are excuted once
        after parsing the parser's arguments"""
        if p.callbacks is None: p.callbacks = []
        p.callbacks.append(fn)

    def _parse_known_args(p, *args, **kwargs):
        """_parse_known_args wraps argparse.ArgumentParser._parse_known_args
        to trigger defered functions once after parsing."""
        res = super()._parse_known_args(*args, **kwargs)
        fns = p.callbacks or []  # get current callbacks
        p.callbacks = None       # delete all callbacks to avoid recursion
        for fn in fns: fn()
        return res

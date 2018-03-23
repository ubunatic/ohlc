from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

def load(filename):
    with open(path.join(here, filename)) as f: return f.read()

def unquote(s): return s.replace('"','').replace("'",'').strip()

def cfg2kv(cfg):
    for line in cfg.split('\n'):
        k, *v = line.split('=')
        yield (unquote(k), unquote(''.join(v)))

readme = load('README.md')
cfg    = dict(cfg2kv(load('project.cfg')))

name        = cfg['name']
binary      = cfg.get('binary')
main        = cfg.get('main')
requires    = cfg.get('requires','').split(' ')
keywords    = cfg.get('keywords','').split(' ')
classifiers = [cfg[k] for k in cfg if tuple(k) in zip(10 * 'c',range(10))]
entry_points = None

if binary is not None or main is not None:
    script = '{b}={m}:main'.format(b=binary, m=main)
    entry_points = {'console_scripts': [script]}

setup(
    name             = name,
    version          = cfg['version'],
    description      = cfg['description'],
    long_description = readme,
    url              = 'https://github.com/ubunatic/{}'.format(name),
    author           = 'Uwe Jugel',
    author_email     = 'uwe.jugel@gmail.com',
    # python_requires  = '>=3.5',
    license          = 'MIT',
    # see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        cfg['status'],
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ] + classifiers,
    keywords = keywords,
    packages = find_packages(
        exclude = ['contrib', 'docs', 'tests'],
    ),
    # see: https://packaging.python.org/en/latest/requirements.html
    install_requires = requires,
    # example: pip install ohlc[dev]
    extras_require = {
        'dev': ['pytest','flake8','twine','pasteurize'],
        # check-mainfest coverage
    },
    # data files
    # package_data={ 'sample': ['package_data.dat'] },
    # extern data files installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    entry_points = entry_points,
    # The key is used to render the link text on PyPI.
    project_urls = {
        'Documentation': 'https://github.com/ubunatic/{}'.format(name),
        'Bug Reports':   'https://github.com/ubunatic/{}/issues'.format(name),
        'Funding':       'https://github.com/ubunatic/{}'.format(name),
        'Say Thanks!':   'https://saythanks.io/to/ubunatic'.format(name),
        'Source':        'https://github.com/ubunatic/{}'.format(name),
    },
)


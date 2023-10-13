from setuptools import setup, find_packages

name = 'ohlc'

setup(
    name = name,
    version = '0.1.12',
    author = 'Uwe Jugel',
    author_email = 'uwe.jugel@gmail.com',
    description = ('ohlc: open-high-low-close types and tools'),
    license = 'MIT',
    keywords = 'ohlc data types finance bitcoin ccxt candlesticks charts widgets graph',
    url = 'https://github.com/ubunatic/ohlc',
    scripts = [],
    packages = find_packages(
        exclude = ['contrib', 'docs', 'tests'],
    ),
    install_requires = [
        'urwid',
        'typing',
        'drawille',
        'widdy',
    ],
    download_url = 'https://github.com/ubunatic/ohlc/tarball/master',
    entry_points={
        "console_scripts": [
            'ohlc= ohlc:main',
            'ohlc-random=ohlc.random:main',
            'ohlc-input=ohlc.input:main',
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console :: Curses',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Office/Business :: Financial :: Investment',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls = {
        'Documentation': f'https://github.com/ubunatic/{name}',
        'Bug Reports':   f'https://github.com/ubunatic/{name}/issues',
        'Funding':       f'https://github.com/ubunatic/{name}',
        'Say Thanks!':    'https://saythanks.io/to/ubunatic',
        'Source':        f'https://github.com/ubunatic/{name}',
    },
)

from setuptools import setup, find_packages
from builtins import open
import sys, os

here     = os.path.abspath(os.path.dirname(__file__))
cfg_file = os.path.join(here, 'project.cfg')
cfg_file = os.environ.get('TOX_PROJECT_CONFIG', cfg_file)

PY2 = sys.version_info.major < 3

def load(filename):
    with open(filename) as f: return f.read()

def load_config(f=cfg_file): return cfg2kv(load(f))

def unquote(s): return s.replace('"','').replace("'",'').strip()

def cfg2kv(cfg):
    cat = 'project'
    res = {cat: {}}
    for line in cfg.split('\n'):
        line = line.strip()
        if line.startswith('#') or line == '': continue
        if line.startswith('[') and line.endswith(']'):
            cat = line[1:][:-1]
            if cat not in res: res[cat] = {}
            continue
        assig = line.split('=')
        res[cat][unquote(assig[0])] = unquote('='.join(assig[1:]))
    return res

def run_setup():
    readme = load('README.md')
    cfg = load_config()
    project = cfg['project']
    scripts = cfg.get('scripts',     {})
    classif = cfg.get('classifiers', {})
    python  = cfg.get('python',      {})

    py_default  = [unquote(v) for v in python.get('default',  '3').split()]
    py_backport = [unquote(v) for v in python.get('backport', '2').split()]

    name        = project['name']
    binary      = project.get('binary')
    main        = project.get('main')
    requires    = project.get('requires','').split(' ')
    keywords    = project.get('keywords','').split(' ')
    version     = project['version']
    description = project['description']
    status      = project['status']

    classifiers     = [classif[k]                    for k in classif]
    console_scripts = ['{}={}'.format(k, scripts[k]) for k in scripts]
    entry_points    = {'console_scripts': console_scripts}

    if binary is not None and main is not None:
        script = '{b}={m}:main'.format(b=binary, m=main)
        console_scripts.append(script)

    classifiers = [status,
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License']
    if PY2:
        classifiers += ['Programming Language :: Python :: {}'.format(v) for v in py_backport]
        readme = """
        ***This is the backport of '{name}' for Python 2.***
        ***Please upgrade to Python 3+ and use the current '{name}' version.***
        {rest}
        """.format(name=name, rest=readme)
        project_name    = name  # "{}-backport".format(name)
        python_requires = '>=2.7, <3'
        # package_dir     = {'':'./backport'}
        package_dir     = {'':'.'}  # assume non-universal build
    else:
        classifiers += ['Programming Language :: Python :: {}'.format(v) for v in py_default]
        project_name    = name
        python_requires = '>=3.5'
        package_dir     = {'':'.'}

    setup(
        name             = project_name,
        version          = version,
        description      = description,
        long_description = readme,
        url              = 'https://github.com/ubunatic/{}'.format(name),
        author           = 'Uwe Jugel',
        author_email     = 'uwe.jugel@gmail.com',
        python_requires  = python_requires,
        license          = 'MIT',
        # see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers = classifiers,
        keywords = keywords,
        package_dir = package_dir,
        packages = find_packages(
            # where   = package_dir[''],
            exclude = ['contrib', 'docs', 'tests'],
        ),
        # see: https://packaging.python.org/en/latest/requirements.html
        install_requires = requires,
        # example: pip install widdy[dev]
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
            'Say Thanks!':   'https://saythanks.io/to/ubunatic',
            'Source':        'https://github.com/ubunatic/{}'.format(name),
        },
    )

if __name__ == '__main__': run_setup()

from setuptools import setup, find_packages
from builtins import open
from configparser import ConfigParser
import sys, os

here       = os.path.abspath(os.path.dirname(__file__))
cfg_file   = os.path.join(here, 'project.cfg')
data_files = [('.', ['project.cfg'])]

PY2 = os.environ.get('PY_TAG') == 'py2' or sys.version_info.major < 3

def load(filename):
    with open(filename) as f: return f.read()

def load_lines(filename):
    with open(filename) as f:
        for l in f: yield l.strip()

def load_config(f=cfg_file):
    p = ConfigParser()
    p.read(cfg_file)
    return {sec:{k:p[sec][k] for k in p[sec].keys()} for sec in p.sections()}

def unquote(s): return s.replace('"','').replace("'",'').strip()

def read_version(main_dir='ohlc', init='__init__.py'):
    version = tag = None
    init = os.path.join(here, main_dir, init)
    for l in load_lines(init):
        if   l.startswith('__version__'): version = unquote(l.split('=')[1])
        elif l.startswith('__tag__'):     tag     = unquote(l.split('=')[1])

    if version is None: raise ValueError('__version__ missing in {}'.format(init))
    if tag     is None: raise ValueError('__tag__ missing in {}'.format(init))
    if PY2: assert tag == 'py2', 'invalid PY_TAG={}'.format(tag)
    else:   assert tag == 'py3', 'invalid PY_TAG={}'.format(tag)
    return version

def run_setup():
    readme = load('README.md')
    cfg = load_config()
    project = cfg['project']
    author  = cfg.get('author',  {})
    scripts = cfg.get('scripts', {})
    python  = cfg.get('python',  {})

    author_name  = author.get('name')
    author_email = author.get('email')
    github_name  = author.get('github_name')

    name         = project['name']
    license      = project['license']
    main         = project['main']
    binary       = project.get('binary')
    requires     = project.get('requires','').split(' ')
    keywords     = project.get('keywords','').split(' ')
    description  = project['description']
    status       = project['status']
    classifiers  = project.get('classifiers', '').split('\n')

    code_version = read_version(main)
    version      = project.get('version', code_version)
    assert version == code_version, 'please update or remove "version" from project.cfg'

    py_default  = [unquote(v) for v in python.get('default',  '3').split()]
    py_backport = [unquote(v) for v in python.get('backport', '2').split()]
    deps_default  = python.get('default_deps','').split(' ')
    deps_backport = python.get('backport_deps','').split(' ')

    console_scripts = ['{}={}'.format(k, scripts[k]) for k in scripts]
    entry_points    = {'console_scripts': console_scripts}

    if binary is not None and main is not None:
        script = '{b}={m}:main'.format(b=binary, m=main)
        console_scripts.append(script)

    if PY2:
        for script in console_scripts[:]:
            b,m = script.split('=')
            b = '{}'.format(b)  # TODO: check if exists and propose resolutions
            console_scripts.remove(script)
            console_scripts.append('{}={}'.format(b,m))

    classifiers += [status]
    if PY2:
        requires += deps_backport
        classifiers += ['Programming Language :: Python :: {}'.format(v) for v in py_backport]
        readme = """
        **This is the backport of '{name}' for Python 2.**
        **Please upgrade to Python 3+ and use the current '{name}' version.**
        {rest}
        """.format(name=name, rest=readme)
        project_name    = name
        python_requires = python.get('backport_requires', '>=2.7, <3')
    else:
        requires += deps_default
        classifiers += ['Programming Language :: Python :: {}'.format(v) for v in py_default]
        project_name    = name
        python_requires = python.get('default_requires', '>=3.5')

    if github_name is None:
        project_urls = None
        url = None
    else:
        gh = github_name
        url = 'https://github.com/{}/{}'.format(gh, name)
        project_urls = {
            'Documentation': 'https://github.com/{}/{}'.format(gh, name),
            'Bug Reports':   'https://github.com/{}/{}/issues'.format(gh, name),
            'Funding':       'https://github.com/{}/{}'.format(gh, name),
            'Say Thanks!':   'https://saythanks.io/to/{}'.format(gh),
            'Source':        'https://github.com/{}/{}'.format(gh, name),
        }

    setup(
        name             = project_name,
        version          = version,
        description      = description,
        long_description = readme,
        url              = url,
        author           = author_name,
        author_email     = author_email,
        python_requires  = python_requires,
        license          = license,
        classifiers = classifiers,
        keywords = keywords,
        packages = find_packages(
            exclude = ['contrib', 'docs', 'tests'],
        ),
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
        project_urls = project_urls,
        data_files = data_files,
    )

if __name__ == '__main__': run_setup()

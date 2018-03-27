from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

def load(filename):
    with open(path.join(here, filename)) as f: return f.read()

def load_config(f='project.cfg'): return cfg2kv(load(f))

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

    print(console_scripts)

    setup(
        name             = name,
        version          = version,
        description      = description,
        long_description = readme,
        url              = 'https://github.com/ubunatic/{}'.format(name),
        author           = 'Uwe Jugel',
        author_email     = 'uwe.jugel@gmail.com',
        # python_requires  = '>=3.5',
        license          = 'MIT',
        # see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers = [
            status,
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
            'Say Thanks!':   'https://saythanks.io/to/ubunatic'.format(name),
            'Source':        'https://github.com/ubunatic/{}'.format(name),
        },
    )

if __name__ == '__main__': run_setup()

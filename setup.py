""" setup.py
    Basic setup file to enable pip install
    See http://python-distribute.org/distribute_setup.py


    python setup.py register sdist upload

"""

import sys
from setuptools import setup, find_packages

import ioflo


_INSTALL_REQUIRES = []
if sys.version_info < (2, 7):
    # Under Python 2.6 `importlib` is only available as a separate package
    _INSTALL_REQUIRES.append('importlib>=1.0.3')


setup(
    name='ioflo',
    version=ioflo.__version__,
    description='Flow Based Programming Automated Reasoning Engine and Automation Operation System',
    long_description='Enabling the Programmable World. http://ioflo.com  ',
    url='https://github.com/ioflo/ioflo',
    download_url='https://github.com/ioflo/ioflo/archive/master.zip',
    author=ioflo.__author__,
    author_email='info@ioflo.com',
    license=ioflo.__license__,
    keywords=('Automation Operating System Automated Reasoning Engine '
              'Flow Based Programming Intelligent Automation Pub/Sub ioflo FloScript'),
    packages = find_packages(exclude=['test', 'test.*',
                                      'docs', 'docs*',
                                      'log', 'log*', 'ioflo/app/log*']),
    package_data={
        '':       ['*.txt',  '*.md', '*.rst', '*.json', '*.conf', '*.html',
                   '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL'],
        'ioflo': ['app/plan/*.flo', 'app/plan/*/*.flo',
                  'app/plan/*.txt', 'app/plan/*/*.txt',],},
    install_requires = _INSTALL_REQUIRES,
    extras_require = {},
    scripts=['scripts/ioflo'],)

"""
setup.py

Basic setup file to enable pip install
See:
    https://pythonhosted.org/setuptools/
    https://bitbucket.org/pypa/setuptools


python setup.py register sdist upload

"""
import  sys
from setuptools import setup, find_packages

import ioflo

PYTHON26_REQUIRES = []
if sys.version_info < (2, 7): #tuple comparison element by element
    PYTHON26_REQUIRES.append('importlib>=1.0.3')
    PYTHON26_REQUIRES.append('argparse>=1.2.1')

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
    packages=find_packages(exclude=['test', 'test.*',
                                      'docs', 'docs*',
                                      'log', 'log*', 'ioflo/app/log*']),
    package_data={
        '':       ['*.txt',  '*.md', '*.rst', '*.json', '*.conf', '*.html',
                   '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL'],
        'ioflo': ['app/plan/*.flo', 'app/plan/*/*.flo',
                  'app/plan/*.txt', 'app/plan/*/*.txt',],},
    install_requires=([] + PYTHON26_REQUIRES),
    extras_require={},
    scripts=['scripts/ioflo'],)


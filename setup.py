"""
setup.py

Basic setup file to enable pip install
See:
    https://pythonhosted.org/setuptools/
    https://bitbucket.org/pypa/setuptools


$ python setup.py register sdist upload

More secure to use twine to upload
$ pip3 install twine
$ python setup.py sdist
$ twine upload dist/ioflo-1.7.2.tar.gz

"""
import sys
import os
from setuptools import setup, find_packages

# Change to Ioflo's source directory prior to running any command
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're probably being frozen, and __file__ triggered this NameError
    # Work around this
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)

IOFLO_METADATA = os.path.join(SETUP_DIRNAME, 'ioflo', '__metadata__.py')

# Load the metadata using exec() so we don't trigger an import of ioflo.__init__
# This is mainly a problem for Python 2.6

exec(compile(open(IOFLO_METADATA).read(), IOFLO_METADATA, 'exec'))


if sys.version_info < (3,7,4):
    msg = "FAIL: Requires Python 3.7.4 or later, but setup.py was run using {}.{}.{}"
    v = sys.version_info
    print(msg.format(v.major, v.minor, v.micro))
    print("NOTE: Installation failed. Run setup.py using Python 3.7.4 or later")
    sys.exit(1)



setup(
    name='ioflo',
    version=__version__,
    description='Flow Based Programming Automated Reasoning Engine and Automation Operation System',
    long_description='Enabling the Programmable World. http://ioflo.com  ',
    url='https://github.com/ioflo/ioflo',
    download_url='https://github.com/ioflo/ioflo/archive/master.zip',
    author=__author__,
    author_email='info@ioflo.com',
    license=__license__,
    keywords=('Automation Operating System Automated Reasoning Engine '
              'Flow Based Programming Intelligent Automation Pub/Sub ioflo FloScript'),
    include_package_data=True,
    packages=find_packages(exclude=['test', 'test.*',
                                      'docs', 'docs*',
                                      'log', 'log*', 'ioflo/app/log*']),
    package_data={
        '':       ['*.txt',  '*.md', '*.rst', '*.json', '*.conf', '*.html',
                   '*.css', '*.ico', '*.png', 'LICENSE', 'LICENSE*.txt' 'LEGAL'],
        'ioflo': ['app/plan/*.flo', 'app/plan/*/*.flo',
                  'app/plan/*.txt', 'app/plan/*/*.txt',],},
    install_requires=[],
    python_requires='>=3.7.4',
    setup_requires=["setuptools_git >= 1.1", ],
    extras_require={},
    scripts=['scripts/ioflo', 'scripts/ioflo3',],)


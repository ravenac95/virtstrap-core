"""
Virtstrap
=========

A bootstrapping mechanism for virtualenv, buildout, and shell scripts.
"""
import sys
import os
from setuptools import setup, find_packages

VERSION = "0.3.0-alpha"

# Installation requirements
REQUIREMENTS = [
    'jinja2',
    'simpleyaml',
]

if sys.version_info < (2, 7):
    REQUIREMENTS.append('argparse>=1.2.1')

# Install the virtstrap support files and virtualenv
# if not in a virtstrap environment
# or if inside a virtstrap development environment.
# FIXME? this feels like too much of a hack. Maybe we should separate 
# virtstrap into multiple packages (one wrapper and one core)
if not os.environ.get('VIRTSTRAP_ENV') or \
    os.environ.get('VIRTSTRAP_DEV_ENV'):
    REQUIREMENTS.append('virtualenv')
    REQUIREMENTS.append('virtstrap-support==%s' % VERSION)

setup(
    name="virtstrap",
    version=VERSION,
    license="MIT",
    author="Reuven V. Gonzales",
    url="https://github.com/ravenac95/virtstrap",
    author_email="reuven@tobetter.us",
    description="A bootstrapping mechanism for virtualenv+pip and shell scripts",
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    platforms='*nix',
    install_requires=REQUIREMENTS,
    entry_points={},
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)

"""
VirtStrap
=========

A bootstrapping mechanism for virtualenv, buildout, and shell scripts.
"""
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name="VirtStrap",
    version="0.2.0",
    license="MIT",
    author="Reuven V. Gonzales",
    url="https://github.com/ravenac95/virtstrap",
    author_email="reuven@tobetter.us",
    description="A bootstrapping mechanism for virtualenv+pip and shell scripts",
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    platforms='*nix',
    install_requires=[
        "PasteScript>=1.3",
        "virtualenv",
    ],
    entry_points="""
        [paste.paster_create_template]
        virtstrap_basic = virtstrap.entry.template:VirtStrapBasicTemplate
    """,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)

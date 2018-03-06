#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'syncthing',
    version = '2.3.0',
    author = 'Blake VandeMerwe',
    author_email = 'blakev@null.net',
    description = 'Python bindings to the Syncthing REST interface, targeting v0.14.44',
    url = 'https://github.com/blakev/python-syncthing',
    license = 'The MIT License',
    install_requires = [
        'python-dateutil==2.6.1',
        'requests==2.18.4'
    ],
    extras_require = {
        'dev': [
            'sphinx',
            'sphinxcontrib-napoleon',
            'sphinx_rtd_theme'
        ]
    },
    packages = [
        'syncthing'
    ],
    package_dir = {
        'syncthing': 'syncthing'
    },
    include_package_data = True,
    zip_safe = True,
    keywords = 'syncthing,sync,rest,backup,api',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Archiving :: Mirroring'
    ],
)
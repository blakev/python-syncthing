#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 11:57 AM

from setuptools import setup

setup(
    name = 'syncthing',
    version = '2.0.0',
    author = 'Blake VandeMerwe',
    author_email = 'blakev@null.net',
    description = 'Python bindings to the Syncthing REST interface, targeting v0.14.19',
    url = 'https://github.com/blakev/python-syncthing',
    license = 'The MIT License',
    install_requires = [
        'requests>=2.9',
        'six==1.10.0'
    ],
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
        'Topic :: System :: Archiving :: Mirroring'
    ],
)
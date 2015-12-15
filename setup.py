#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 11:57 AM

import os
from setuptools import setup

v_str = lambda s: '.'.join(map(str, s))
with open('VERSION', 'r') as version_file:
    version_string = version_file.readline().strip()

version, syncthing_version = version_string.split('|')

version_num = v_str(eval(version))
syncthing_version_num = v_str(eval(syncthing_version))

setup(
    name = 'syncthing',
    version = version_num,
    author = 'Blake VandeMerwe',
    author_email = 'blakev@null.net',
    description = 'Python bindings to the Syncthing REST interface, targeting v%s' % syncthing_version_num,
    url = 'https://github.com/blakev/python-syncthing',
    license = 'The MIT License',
    install_requires = [
        'requests>=2.7',
    ],
    packages = [
        'syncthing'
    ],
    package_dir = {
        'syncthing': 'syncthing'
    },
    include_package_data = True,
    zip_safe = True,
    keywords = 'syncthing,sync,rest,backup',
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
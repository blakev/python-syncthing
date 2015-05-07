#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 11:57 AM


from setuptools import setup

from syncthing import version_num, syncthing_version_num

setup(
    name = 'syncthing',
    version = version_num,

    author = 'Blake VandeMerwe',
    author_email = 'blakev@null.net',

    description = 'Python bindings to the Syncthing REST interface, targeting v%s' % syncthing_version_num,

    url = 'https://github.com/blakev/python-syncthing',
    license = 'The MIT License',

    install_requires = [
        'requests',
        'bunch'
    ],
    packages = [
        'syncthing'
    ],
    package_dir = {
        'syncthing': 'syncthing'
    },
    include_package_data = True,
    zip_safe = False,
    keywords = 'syncthing,sync,rest,backup',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Archiving :: Mirroring'
    ],
)
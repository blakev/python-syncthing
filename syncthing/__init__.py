#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 11:54 AM

import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'VERSION'), 'r') as version_file:
    version_string = version_file.readline().strip()
    VERSION, SYNCTHING_VERSION = version_string.split('|')
    VERSION = eval(VERSION)
    SYNCTHING_VERSION = eval(SYNCTHING_VERSION)

from .interface import Interface
from .syncthing import Syncthing

v_str = lambda s: '.'.join(map(str, s))

version_num = v_str(VERSION)
syncthing_version_num = v_str(SYNCTHING_VERSION)

version = 'python-syncthing v%s targeting v%s' % (version_num, syncthing_version_num)
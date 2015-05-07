#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 11:54 AM

VERSION = (0, 0, 4)
SYNCTHING_VERSION = (0, 11, 2)

from .interface import Interface
from .syncthing import Syncthing

v_str = lambda s: '.'.join(map(str, s))

version_num = v_str(VERSION)
syncthing_version_num = v_str(SYNCTHING_VERSION)

version = 'python-syncthing v%s targeting v%s' % (version_num, syncthing_version_num)
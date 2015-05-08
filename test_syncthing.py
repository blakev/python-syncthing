#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 3:42 PM

import unittest

from syncthing import Interface, Syncthing

try:
    from syncthing import private_settings as settings
except ImportError:
    from syncthing import test_settings as settings

class SyncthingInterfaceTestCase(unittest.TestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        self.i = Interface(None)
        self.xi = Interface(settings.API_KEY, port=settings.PORT)

    def test_interface_default(self):
        Interface

    def test_interface_properties(self):
        assert self.i.root

    def test_interface_classmethods(self):
        assert Interface.from_json
        assert self.i.from_json
        assert Interface.from_dict
        assert self.i.from_dict

    def test_interface_connected(self):
        assert self.xi.is_connected

    def test_interface_ping(self):
        assert self.xi.req('/rest/system/ping', 'GET').ping == 'pong'
        assert self.xi.req('/rest/system/ping', 'POST').ping == 'pong'

class SyncthingSyncthingTestCase(unittest.TestCase):
    _multiprocess_can_split_ = True

    def test_syncthing_default(self):
        Syncthing
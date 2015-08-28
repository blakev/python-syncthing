#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 3:42 PM
import os
import unittest

from six import print_

from syncthing import Interface, Syncthing
from syncthing.settings import default as settings

try:
    from syncthing.settings import local as local_settings
except ImportError as e:
    pass
else:
    settings.__dict__.update(local_settings.__dict__)
    del local_settings


class SyncthingInterfaceGetDocumentationTestCase(unittest.TestCase):
    def test_get_latest_documentation(self):
        from syncthing.interface import get_latest_documentation

        assert os.path.exists(get_latest_documentation())
        assert os.path.exists(get_latest_documentation(as_version='UNITTEST'))

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
#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     Copyright (c) 2016-2017, Blake VandeMerwe
#
#       Permission is hereby granted, free of charge, to any person obtaining
#       a copy of this software and associated documentation files
#       (the "Software"), to deal in the Software without restriction,
#       including without limitation the rights to use, copy, modify, merge,
#       publish, distribute, sublicense, and/or sell copies of the Software,
#       and to permit persons to whom the Software is furnished to do so, subject
#       to the following conditions: The above copyright notice and this permission
#       notice shall be included in all copies or substantial portions
#       of the Software.
#
#     python-syncthing, 2016
# <<

import os
import unittest

from six import string_types

from syncthing import Syncthing, SyncthingError, BaseAPI

KEY = os.getenv('SYNCTHING_API_KEY')
HOST = os.getenv('SYNCTHING_HOST', '127.0.0.1')
PORT = os.getenv('SYNCTHING_PORT', 8384)
IS_HTTPS = bool(int(os.getenv('SYNCTHING_HTTPS', '0')))
SSL_CERT_FILE = os.getenv('SYNCTHING_CERT_FILE')

def syncthing():
    return Syncthing(KEY, HOST, PORT, 10.0, IS_HTTPS, SSL_CERT_FILE)


s = syncthing()

class TestScanFolder(unittest.TestCase):
    def test_folder_scan_root(self):
        folders = s.stats.folder()
        available = list(folders.keys())
        if not available:
            raise EnvironmentError('there are no folders to scan')
        use = available[0]
        ret = s.database.scan(use)
        last_scan = folders[use]['lastScan']
        assert isinstance(ret, string_types)
        assert s.stats.folder()[use]['lastScan'] > last_scan

    def test_folder_scan_sub(self):
        folder = '2vw2z-xwpvk'
        last_scan = s.stats.folder()[folder]['lastScan']
        ret = s.database.scan(folder, 'docs')
        assert isinstance(ret, string_types)
        assert s.stats.folder()[folder]['lastScan'] > last_scan

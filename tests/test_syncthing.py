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
from __future__ import unicode_literals

import os
import unittest

import requests
from syncthing import Syncthing, SyncthingError, BaseAPI

KEY = os.getenv('SYNCTHING_API_KEY')
HOST = os.getenv('SYNCTHING_HOST', '127.0.0.1')
PORT = os.getenv('SYNCTHING_PORT', 8384)
IS_HTTPS = bool(int(os.getenv('SYNCTHING_HTTPS', '0')))
SSL_CERT_FILE = os.getenv('SYNCTHING_CERT_FILE')

def syncthing():
    return Syncthing(KEY, HOST, PORT, 10.0, IS_HTTPS, SSL_CERT_FILE)


class TestBaseAPI(unittest.TestCase):

    def test_a_imports(self):
        assert Syncthing
        assert SyncthingError
        assert BaseAPI

    def test_b_instantiation(self):
        Syncthing('')

    def test_c_attributes(self):
        s = Syncthing('')
        assert s.host is not None
        assert hasattr(s, 'system')
        assert hasattr(s, 'database')
        assert hasattr(s, 'stats')
        assert hasattr(s, 'misc')

    def test_c_connection(self):
        sync = syncthing()
        resp = requests.get(sync.misc.url)
        self.assertEqual(resp.status_code, 200, 'cannot connect to syncthing')

    def test_m_database(self):
        pass

    def test_m_stats(self):
        pass

    def test_m_misc_device(self):
        s = syncthing()

        self.assertEqual(s.misc.device_id(None), '')
        self.assertEqual(s.misc.device_id(''), '')
        with self.assertRaises(SyncthingError):
            s.misc.device_id(1234)

        orig = 'p56ioi7m--zjnu2iq-gdr-eydm-2mgtmgl3bxnpq6w5btbbz4tjxzwicq'
        valid = 'P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2'
        self.assertEqual(s.misc.device_id(orig), valid)

    def test_m_misc_lang(self):
        s = syncthing()
        langs = s.misc.language()
        self.assertIsInstance(langs, list)
        self.assertEqual(len(langs), 1)

        langs = s.misc.get('lang', headers={'Accept-Language': 'en_us'})
        self.assertIsInstance(langs, list)
        self.assertEqual(len(langs), 1)
        self.assertEqual(langs[0], 'en_us')

    def test_m_misc_random_string(self):
        s = syncthing()

        self.assertEqual(len(s.misc.random_string()), 32)
        self.assertEqual(len(s.misc.random_string(16)), 16)
        self.assertEqual(len(s.misc.random_string(0)), 32)
        self.assertEqual(len(s.misc.random_string(1)), 1)
        self.assertEqual(len(s.misc.get('random/string').get('random', None)), 32)


class TestSystemAPI(unittest.TestCase):
    def test_errors(self):
        s = syncthing()
        s.system.errors()

    def test_status(self):
        s = syncthing()
        status = s.system.status()
        self.assertIsInstance(status, dict)
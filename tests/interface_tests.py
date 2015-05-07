#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:10 PM

import unittest

from syncthing import Interface


class TestBasicInterface(unittest.TestCase):
    def setUp(self):
        self.interface = Interface(None)

    def test_connection(self):
        i = Interface(None, port=8384, is_https=False)

        self.assertTrue(i.is_connected)

    def test_root(self):
        i = self.interface

        self.assertTrue(i.host == 'localhost')
        self.assertTrue(i.port == 8080)
        self.assertTrue(i.protocol == 'http')
        self.assertTrue(i.root == 'http://localhost:8080')



if __name__ == '__main__':
    unittest.main()
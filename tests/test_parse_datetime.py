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

import unittest
from datetime import datetime

from syncthing import SyncthingError, parse_datetime


class TestParseDatetime(unittest.TestCase):
    def test_empties(self):
        assert parse_datetime(None) is None
        assert parse_datetime('') is None
        assert parse_datetime(0) is None

    def test_raises(self):
        self.assertRaises(SyncthingError, parse_datetime, 'abc')
        self.assertRaises(SyncthingError, parse_datetime, [1])

    def test_old_docstring_tests(self):
        tests = [
            ('2016-06-06T19:41:43.039284753+02:00', datetime(2016, 6, 6, 21, 41, 43, 39284)),
            ('2016-06-06T19:41:43.039284753+02:00', datetime(2016, 6, 6, 21, 41, 43, 39284)),
            ('2016-06-06T19:41:43.039284753-02:00', datetime(2016, 6, 6, 17, 41, 43, 39284)),
            ('2016-06-06T19:41:43.039284',          datetime(2016, 6, 6, 17, 41, 43, 39284)),
            ('2016-06-06T19:41:43.039284000-02:00', datetime(2016, 6, 6, 19, 41, 43, 39284))
        ]
        for a, b in tests:
            assert parse_datetime(a).toordinal() == b.toordinal()

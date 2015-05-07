#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:13 PM
import sys
import json
import warnings
import logging

import requests
from requests.packages.urllib3 import exceptions
from bunch import Bunch

VERB_SWAPS = {
    'GET': '',
    'POST': 'set',
    'DELETE': 'del',
    'PUT': 'put'
}

# sys.version_info(major=2, minor=7, micro=9, releaselevel='final', serial=0)
PY_MAJOR, PY_MINOR, PY_MICRO = sys.version_info[:3]

if PY_MAJOR == 2:
    import urlparse as uparse
else:
    import urllib.parse as uparse

MIN_TIMEOUT_SECS = 0.5

class Interface(object):
    def __init__(self,
            api_key: str,
            host: str = 'localhost',
            port: int = 8080,
            timeout: float = 3.0,
            is_https: bool = False,
            ssl_cert_file: str = None):

        if is_https and ssl_cert_file is None:
            raise EnvironmentError('Cannot require https connection without ssl key.')

        self.api_key = api_key
        self.host = host
        self.port = port
        self.protocol = 'https' if is_https else 'http'

        self.timeout = max(MIN_TIMEOUT_SECS, timeout)

        self.cert = ssl_cert_file
        self.verify = True if self.cert else False

        self.req_headers = {
            'X-API-Key': self.api_key
        }

    @property
    def root(self):
        return '%s://%s:%d' % (self.protocol, self.host, self.port)

    @property
    def is_connected(self):
        return requests.request(
            'GET',
            self.root,
            timeout = 2.0,
            verify = self.verify,
            cert = self.cert).status_code == 200

    def to_json(self):
        pass

    def req(self, endpoint, verb, **kwargs):
        verb = verb.upper()

        if verb not in VERB_SWAPS.keys():
            raise UserWarning('Unsupported HTTP verb in REST request.')

        the_url = uparse.urljoin(self.root, endpoint)

        print(the_url)

        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', exceptions.InsecureRequestWarning)
                resp = requests.request(
                    verb,
                    the_url,
                    params = kwargs,
                    timeout = self.timeout,
                    verify = self.verify,
                    cert = self.cert,
                    headers = self.req_headers)
        except requests.RequestException as e:
            raise
        else:
            return Bunch(resp.json())





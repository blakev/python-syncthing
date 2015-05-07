#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:13 PM
import sys
import json
import warnings
import logging

import six
import requests
from requests.packages.urllib3 import exceptions
from bunch import Bunch

VERB_SWAPS = {
    'GET': '',
    'POST': 'set',
    'DELETE': 'del',
    'PUT': 'put'
}

if six.PY2:
    import urlparse as uparse
    import codecs

    _u = lambda x: codecs.unicode_escape_decode(x)[0]
    _s = lambda x: x
elif six.PY3:
    import urllib.parse as uparse

    _u = lambda x: x
    _s = lambda x: x.decode('utf-8')
else:
    raise EnvironmentError('Unknown python major version.')



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
            warnings.warn('Using HTTPS without specified ssl_cert_file.')

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

        self.last_request = None

    @property
    def root(self):
        return '%s://%s:%d' % (self.protocol, self.host, self.port)

    @property
    def is_connected(self):
        if not self.last_request:
            self.req('/', 'GET')

        return self.last_request

    @staticmethod
    def from_json(json_str):
        pass

    @staticmethod
    def from_dict(d):
        pass

    def to_json(self):
        pass

    def req(self, endpoint, verb, **kwargs):
        verb = verb.upper()

        if verb not in VERB_SWAPS.keys():
            raise UserWarning('Unsupported HTTP verb in REST request.')

        the_url = uparse.urljoin(self.root, endpoint)

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
            self.last_request = False
            raise
        else:
            self.last_request = resp.status_code == 200

            if 'json' in resp.headers.get('content-type', 'text/plain').lower():
                return Bunch(resp.json())
            else:
                return resp





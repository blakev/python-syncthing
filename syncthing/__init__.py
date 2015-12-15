#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# >>
#     The MIT License (MIT)
#
#     Copyright (c) 2015-2016 Blake VandeMerwe
#
#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.
# <<

__author__ = 'Blake VandeMerwe <blakev@null.net>'
__version__ = VERSION = (1, 0, 0)
SYNCTHING_VERSION = (0, 12, 8)

vstr = lambda x: '.'.join(map(str, x))

version = vstr(VERSION)
syncthing_version = vstr(SYNCTHING_VERSION)
docstr = 'python-syncthing v%s targetting v%s' % (version, syncthing_version)

import sys
import json
import time
import logging
import warnings
from collections import namedtuple

import requests
from requests.packages.urllib3 import exceptions
from requests.exceptions import ConnectionError, ConnectTimeout

py_2 = sys.version_info.major == 2

if py_2:
    import urlparse as uparse
else:
    import urllib.parse as uparse

logger = logging.getLogger(__name__)

MIN_TIMEOUT_SECONDS = 1.0
REST_ENDPOINT = '/rest'

class C(object):
    ommand = namedtuple('Command', 'verb endpoint')

    def __init__(self, verb, endpoint):
        self.command = C.ommand(verb, REST_ENDPOINT + endpoint)

    def __call__(self, data_obj=None, **params):
        if data_obj is not None:
            if not isinstance(data_obj, dict):
                raise ValueError('data_obj must be of type dictionary')

        if not hasattr(C, 'iface'):
            return None

        return C.iface.do_req(self.command.verb, self.command.endpoint, \
                                data_obj, **params)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<Command(%s, "%s")>' % (self.command.verb, self.command.endpoint)


class GetDict(dict):
    def __init__(self, *args, **kwargs):
        super(GetDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        for k, v in kwargs.items():
            if isinstance(v, tuple):
                v = C(*v)
            self[k] = v

    def __getattr__(self, item):
        return self.get(item)


class Commands(object):
    def __init__(self, interface):
        C.iface = interface

        self.sys = GetDict(
            config =    ('GET', '/system/config'),
            insync =    ('GET', '/system/config/insync'),
            connections=('GET', '/system/connections'),
            debug =     ('GET', '/system/debug'),
            discovery = ('GET', '/system/discovery'),
            error =     ('GET', '/system/error'),
            log =       ('GET', '/system/log'),
            ping =      ('GET', '/system/ping'),
            status =    ('GET', '/system/status'),
            upgrade =   ('GET', '/system/upgrade'),
            version =   ('GET', '/system/version'),
            set = GetDict(
                config =    ('POST', '/system/config'),
                debug =     ('POST', '/system/debug'),
                discovery = ('POST', '/system/discovery'),
                clear =     ('POST', '/system/error/clear'),
                error =     ('POST', '/system/error'),
                ping =      ('POST', '/system/ping'),
                reset =     ('POST', '/system/reset'),
                restart =   ('POST', '/system/restart'),
                shutdown =  ('POST', '/system/shutdown'),
                upgrade =   ('POST', '/system/upgrade'),
            )
        )
        self.db = GetDict(
            browse =    ('GET', '/db/browse'),
            completion =('GET', '/db/completion'),
            file =      ('GET', '/db/file'),
            ignores =   ('GET', '/db/ignores'),
            need =      ('GET', '/db/need'),
            status =    ('GET', '/db/status'),
            set = GetDict(
                ignores = ('POST', '/db/ignores'),
                prio =    ('POST', '/db/prio'),
                scan =    ('POST', '/db/scan')
            )
        )
        self.stats = GetDict(
            device =    ('GET', '/stats/device'),
            folder =    ('GET', '/stats/folder')
        )
        self.misc = GetDict(
            device_id = ('GET', '/svc/deviceid'),
            lang =      ('GET', '/svc/lang'),
            report =    ('GET', '/svc/report')
        )

        # set command aliases
        self.misc.language = self.misc.lang
        self.sys.config_insync = self.sys.insync
        self.sys.conf_insync = self.sys.insync
        self.sys.conf = self.sys.config
        self.database = self.db
        self.system = self.sys


class Interface(object):
    def __init__(self, api_key, **options):
        self.options = {
            'api_key': api_key,
            'host': 'localhost',
            'port': 8080,
            'timeout': 3.5,
            'is_https': False,
            'ssl_cert_file': None
        }


        self.options.update(options)
        self.options = GetDict(**self.options)

        if self.options.is_https and self.options.ssl_cert_file is None:
            warnings.warn('using https without specified ssl_cert_file')

        self.verify = True if self.options.ssl_cert_file else False
        self.protocol = 'https' if self.options.is_https else 'http'
        self.timeout = max(MIN_TIMEOUT_SECONDS, self.options.timeout)
        self.req_headers = {
            'X-API-Key': api_key
        }

        # cached "is_connected"
        self.last_req = None
        self.last_req_time = 0

    @property
    def host(self):
        return '%s://%s:%d' % (
            self.protocol, self.options.host, self.options.port)

    @property
    def connected(self):
        if not self.last_req or self.last_req_time < (time.time() - 60):
            self.__req('GET', '/')
        return self.last_req

    def do_req(self, verb, endpoint, data=None, **params):
        url = uparse.urljoin(self.host, endpoint)
        return self.__req(verb, url, data, params)

    def __req(self, verb, url, data=None, params=None):
        verb = verb.upper()

        if verb not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise UserWarning('unsupported http verb in rest request')

        if data is None:
            data = {}

        try:
            with warnings.catch_warnings():
                if not self.options.ssl_cert_file:
                    warnings.simplefilter('ignore', exceptions.InsecureRequestWarning)

            resp = requests.request(
                verb,
                url,
                data=data,
                params=params,
                timeout=self.timeout,
                verify=self.verify,
                cert=self.options.ssl_cert_file,
                headers=self.req_headers
            )

        except ConnectionError as e:
            logger.error('could not connect to ' + self.host)
            raise e

        except ConnectTimeout as e:
            logger.error('connection timed out after ' + self.timeout)
            raise e

        except requests.RequestException as e:
            self.last_req = None
            raise e
        else:
            self.last_req = resp.status_code == requests.codes.ok
            self.last_req = time.time()

            if resp.status_code != requests.codes.ok:
                logger.error('%s %s (%s): %s' % (
                    resp.status_code, resp.reason, resp.url, resp.text))
                return resp

            if 'json' in resp.headers.get('Content-Type', 'text/plain').lower():
                return resp.json()
            else:
                c = resp.content
                if c.startswith('{') and c.endswith('}'):
                    return json.loads(c)
                return c


class Syncthing(object):
    def __init__(self, **kwargs):
        self._interface = None
        self._commands = None

        if kwargs and kwargs.get('api_key', None):
            key = kwargs.pop('api_key')
            self.init(key, **kwargs)

    def init(self, api_key, **kwargs):
        if self._interface is None:
            self._interface = Interface(api_key, **kwargs)
            self._commands = Commands(self._interface)

    def __getattr__(self, item):
        if self._interface is None:
            raise AttributeError('must call Syncthing.init before performing operations')
        return self._commands.__dict__.get(item)
